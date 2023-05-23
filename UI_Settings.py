from tkinter import ttk
import tkinter as tk
import customtkinter as ctk
import values_and_rules
import navigationmenu
from error_handlers import warning


class SettingsPage(ctk.CTkScrollableFrame):


    class SubjectSettingsPage(ctk.CTkFrame):
        


        class SubjectRow(ctk.CTkFrame):

            def prefill_subject_code(self,value):

                if value.strip()!="":
                    self.subject_code_entry.delete(0,tk.END)

                    self.subject_code_entry.insert(0,value)

            def prefill_subject_name(self,value):
                if value.strip()!="":
                    self.subject_name_entry.delete(0,tk.END)

                    self.subject_name_entry.insert(0,value)

            def show_save_button(self):
                if self.shown==False:
                    self.shown=True
                    self.save_button.grid(row=0,column=3,sticky="nw")

            def hide_save_button(self):
                if self.shown==True:
                    self.shown=False
                    self.save_button.grid_forget()

            def save_changes(self,event=None):
                if self.new_obj==True:
                    try:
                        new_subject_code,new_subject_name=self.settings_obj.add_subject(self.subject_name_entry.get(),self.subject_code_entry.get())
                    except ValueError as e:
                        warning(message=str(e))
                        return

                    self.subject_code=new_subject_code
                    self.prefill_subject_code(self.subject_code)
    
                    self.subject_name=new_subject_name
                    self.prefill_subject_name(self.subject_name)

                    self.master.add_new_empty_subject_row()

                else:
                    if self.subject_code_changed:
                        try:
                            new_subject_code=self.settings_obj.change_subject_code(self.subject_code,self.subject_code_entry.get(),self.subject_name_entry.get())
                        except ValueError as e:
                            warning(message=str(e))
                            return
                        self.subject_code=new_subject_code
                        self.prefill_subject_code(self.subject_code)
                    if self.subject_name_changed:
                        try:
                            new_subject_name = self.settings_obj.change_subject_name(self.subject_code,self.subject_name_entry.get())
                        except ValueError as e:
                            warning(message=str(e))
                            return
                        self.subject_name=new_subject_name
                        self.prefill_subject_name(self.subject_name)
                self.hide_save_button()

            def on_change(self,event=None):
                self.subject_code_changed=False
                self.subject_name_changed=False
                if self.subject_code_entry.get().casefold()!=self.subject_code.casefold():
                    self.subject_code_changed=True
                if self.subject_name_entry.get().casefold()!=self.subject_name.casefold():
                    self.subject_name_changed=True
                if self.subject_code_changed or self.subject_name_changed:
                    self.show_save_button()
                else:
                    self.hide_save_button()

            def delete_changes(self,event=None):
                self.settings_obj.remove_subject(self.subject_code)
                self.grid_forget()

            def __init__(self,master,settings_obj,subject_name,subject_code):
                super().__init__(master,fg_color="transparent")
                self.master=master

                self.columnconfigure(0,weight=1)
                self.columnconfigure(1,weight=1)
                self.columnconfigure(2,weight=1)
                self.columnconfigure(3,weight=1)

                self.settings_obj=settings_obj
                self.subject_name=subject_name
                self.subject_code=subject_code
                self.new_obj=False
                if self.subject_name=="" and self.subject_code=="":
                    self.new_obj=True
                

                self.subject_name_entry=ctk.CTkEntry(self,placeholder_text="Subject name")
                self.prefill_subject_name(subject_name)
                self.subject_name_entry.grid(row=0,column=0,sticky="nw")
                self.subject_code_entry=ctk.CTkEntry(self,placeholder_text="Subject code")
                self.prefill_subject_code(subject_code)
                self.subject_code_entry.grid(row=0,column=1,sticky="nw")

                self.subject_code_changed=False
                self.subject_name_changed=False
                self.subject_code_entry.bind("<KeyRelease>",self.on_change)
                self.subject_name_entry.bind("<KeyRelease>",self.on_change)

                self.shown=False
                self.save_button=ctk.CTkButton(self,text="Save",command=self.save_changes)

                self.delete_button=ctk.CTkButton(self,text="Delete",command=self.delete_changes)
                self.delete_button.grid(row=0,column=2,sticky="nw")
        
        def setup(self):
            
            self.subject_row_counter=1
            for subject_code in self.controller.mainline_obj.settings.get_subjects():
                subject_row=self.SubjectRow(self,self.controller.mainline_obj.settings,self.controller.mainline_obj.settings.get_subjects()[subject_code],subject_code)
                subject_row.grid(row=self.subject_row_counter,column=0,sticky="new",padx=15,pady=3)
                self.subject_row_counter+=1
                self.subject_rows.append(subject_row)
            self.add_new_empty_subject_row()

        def update_idle(self):
            for i,subject_row in enumerate(self.subject_rows):
                subject_row.grid_forget()
            self.subject_rows=[]
            self.setup()

        def add_new_empty_subject_row(self):
            subject_row=self.SubjectRow(self,self.controller.mainline_obj.settings,"","")
            subject_row.grid(row=self.subject_row_counter,column=0,sticky="new",padx=15,pady=3) 
            self.subject_row_counter+=1
        
        def __init__(self,controller,settings):
            self.controller=controller
            self.settings=settings
            self.subject_rows=[]



            super().__init__(self.controller,fg_color=self.controller.mainline_obj.colors.bubble_background)

            self.columnconfigure(0,weight=1)
            self.columnconfigure(1,weight=1)
            #self.columnconfigure(2,weight=1)
            #self.columnconfigure(3,weight=1)

            self.subject_settings_label = ctk.CTkLabel(self,text="Subject Selection",font=("Arial", 19))
            self.subject_settings_label.grid(row=0,column=0,padx=15,pady=(15,7),sticky="nw")



    class CourseSettingPage(ctk.CTkFrame):
        def save_changes(self):
            
            self.settings.course_type = self.inverted_course_types[self.selected_variable.get()]
            self.settings.commit_changes()
            self.mainline_obj.resetwindows("MainPage")

        def __init__(self,controller,settings):
            self.settings=settings
            self.controller=controller
            super().__init__(self.controller,fg_color=self.controller.mainline_obj.colors.bubble_background)

            self.course_types = values_and_rules.get_course_types()
            self.inverted_course_types = {v: k for k, v in self.course_types.items()}

            options = list(self.course_types.values())
            
            self.course_settings_label = ctk.CTkLabel(self,text="Course Selection",font=("Arial", 19))
            self.course_settings_label.grid(row=0,column=0,padx=15,pady=(15,7),sticky="nw")

            self.selected_variable = tk.StringVar(self)
            self.selected_variable.set(values_and_rules.get_course_types()[self.settings.course_type]) # default value


            optionmenu = ctk.CTkOptionMenu(self,values=options,variable=self.selected_variable)
            optionmenu.grid(row=1,column=0,sticky="nw",padx=15,pady=7)

            save_changes_button = ctk.CTkButton(self, text="Save Changes",command=self.save_changes)
            save_changes_button.grid(row=2,column=0,sticky="nw",padx=15,pady=7)


    def grid_forget_all(self):
        self.course_settings_page.grid_forget()
        self.subject_settings_page.grid_forget()

    def show_settings_page(self,page):
        self.grid_forget_all()
        if page == "CourseSettings":
            self.course_settings_page.grid(row=1,column=1,sticky="nsew",padx=(0,15),pady=15)
            self.navigation_menu.page_selected("CourseSettings")

        if page == "SubjectSettings":
            self.subject_settings_page.grid(row=1,column=1,sticky="nsew",padx=(0,15),pady=15)
            self.subject_settings_page.update_idle()
            self.navigation_menu.page_selected("SubjectSettings")





    def __init__(self,mainline_obj,scrollable_frame,grid_preload):
        super().__init__(scrollable_frame)
        self.mainline_obj=mainline_obj
        # setup_ui
        self.subject_row_counter=0

        self.columnconfigure(1,weight=1)
        #.columnconfigure(0,weight=1)

        self.settings_menu_frame = ctk.CTkFrame(self)
        self.settings_menu_frame.grid(row=1,column=0,sticky="nsew")

        self.settings = self.mainline_obj.settings
        self.course_settings_page=self.CourseSettingPage(self,self.mainline_obj.settings)
        self.subject_settings_page=self.SubjectSettingsPage(self,self.mainline_obj.settings)

        buttons=[
            {"code":"CourseSettings","text":"Course","command":self.show_settings_page,"param":"CourseSettings","position":"top"},
            {"code":"SubjectSettings","text":"Subjects","command":self.show_settings_page,"param":"SubjectSettings","position":"top"},
        ]

        self.navigation_menu = navigationmenu.NavigationMenu(self.settings_menu_frame,mainline_obj,buttons,text="Settings",fg_color=self.mainline_obj.colors.bubble_background,corner_radius=15,heading_font=("Arial", 22))
        self.navigation_menu.grid(row=0,column=0,padx=15,pady=15,sticky="nw")

