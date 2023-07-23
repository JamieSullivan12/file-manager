import os
from tkinter import ttk
import tkinter as tk
import customtkinter as ctk
import values_and_rules
import navigationmenu
import CommonFunctions
import custom_errors

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
                    self.save_button.grid(row=0,column=3,sticky="new",padx=8,pady=3)

            def hide_save_button(self):
                if self.shown==True:
                    self.shown=False
                    self.save_button.grid_forget()

            def save_changes(self,event=None):
                if self.new_obj==True:
                    try:
                        new_subject_code,new_subject_name=self.settings_obj.add_subject(self.subject_name_entry.get(),self.subject_code_entry.get())
                    except ValueError as e:
                        custom_errors.ExceptionWarning(message=str(e))
                        return

                    self.subject_code=new_subject_code
                    self.prefill_subject_code(self.subject_code)
    
                    self.subject_name=new_subject_name
                    self.prefill_subject_name(self.subject_name)

                    self.master.add_new_empty_subject_row()

                    self.grid_delete_button()
                    self.new_obj=False

                else:
                    if self.subject_code_changed:
                        try:
                            new_subject_code=self.settings_obj.change_subject_code(self.subject_code,self.subject_code_entry.get(),self.subject_name_entry.get())
                        except ValueError as e:
                            custom_errors.ExceptionWarning.warning(message=str(e))
                            return
                        self.subject_code=new_subject_code
                        self.prefill_subject_code(self.subject_code)
                    if self.subject_name_changed:
                        try:
                            new_subject_name = self.settings_obj.change_subject_name(self.subject_code,self.subject_name_entry.get())
                        except ValueError as e:
                            custom_errors.ExceptionWarning(message=str(e))
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

            def grid_delete_button(self):
                self.delete_button.grid(row=0,column=2,sticky="new",padx=8,pady=3)

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
                self.subject_name_entry.grid(row=0,column=0,sticky="new",padx=8,pady=3)
                self.subject_code_entry=ctk.CTkEntry(self,placeholder_text="Subject code")
                self.prefill_subject_code(subject_code)
                self.subject_code_entry.grid(row=0,column=1,sticky="new",padx=8,pady=3)

                self.subject_code_changed=False
                self.subject_name_changed=False
                self.subject_code_entry.bind("<KeyRelease>",self.on_change)
                self.subject_name_entry.bind("<KeyRelease>",self.on_change)

                self.shown=False
                self.save_button=ctk.CTkButton(self,text="Save",command=self.save_changes)
                
                self.delete_button=ctk.CTkButton(self,text="Delete",command=self.delete_changes)

                if not self.new_obj:
                    self.grid_delete_button()
                    
        
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

            self.subject_settings_label = ctk.CTkLabel(self,text="Subject Selection",font=("Arial", 19))
            self.subject_settings_label.grid(row=0,column=0,padx=15,pady=(15,7),sticky="nw")




    class ConfigurationPage(ctk.CTkFrame):

        class CourseRow(ctk.CTkFrame):

            def make_grid(self,small=False):

                row=0
                col=0

                self.entry_code.grid(row=row,column=col,sticky="new",padx=(0,4))
                col+=1


                self.entry_name.grid(row=row ,column=col,sticky="new",padx=(0,4))
                col+=1

                if small:
                    col=0
                    row=1
    
                    self.columnconfigure(0,weight=1)
                    self.columnconfigure(1,weight=1)
                    self.columnconfigure(2,weight=0)
                    self.columnconfigure(3,weight=0)
                else:
                    self.columnconfigure(0,weight=1)
                    self.columnconfigure(1,weight=1)
                    self.columnconfigure(2,weight=1)
                    self.columnconfigure(3,weight=1)


                self.remove_button.grid(row=row,column=col,sticky="new",padx=(0,4))
                col+=1
                if not self.course_obj.get_valid()[0]:
                    self.see_errors_button.grid(row=row,column=col,sticky="new",padx=(0,0))
                else:
                    self.see_info_button.grid(row=row,column=col,sticky="new",padx=(0,0))      
            def __init__(self,master,*args,**kwargs):
                super().__init__(master,*args,**kwargs)


                
                self.entry_code=CommonFunctions.NewEntry(self)
                self.entry_code.toggle_readonly_on()
                

                self.entry_name=CommonFunctions.NewEntry(self)
                self.entry_name.toggle_readonly_on()
                
            
            def remove_command(self,event=None):
                if self.master.controller.mainline_obj.settings.get_course_type() == self.course_obj.course_code and self.course_obj.get_valid()[0]:
                    tk.messagebox.showwarning(title="Cannot save",message="You cannot delete the current active course configuration.")
                else:
                    self.course_obj.remove_command()
                    self.master.controller.mainline_obj.deep_reset()

            def see_errors_command(self,event=None):
                tk.messagebox.showerror(title=f"Errors",message=f"The following errors are for {self.course_obj.course_code} ({CommonFunctions.get_cwd_file(self.course_obj.path)})\n\n"+"\n".join(self.course_obj.get_valid()[1]))

            def see_info_command(self,event=None):
                tk.messagebox.showinfo(title="Info",message=f"Course code: {self.course_obj.course_code}\nCourse name: {self.course_obj.course_name}\nJSON file path: {CommonFunctions.get_cwd_file(self.course_obj.path)}")

            def inject_functionality(self,course_obj):
                self.course_obj=course_obj
                self.entry_code.change_contents(course_obj.course_code)
                self.entry_name.change_contents(course_obj.course_name)

                self.remove_button = ctk.CTkButton(self,text=f"Remove",command=self.remove_command)

                if not course_obj.get_valid()[0]:
                    self.see_errors_button = ctk.CTkButton(self,text=f"See errors",command=self.see_errors_command)
                    
                else:
                    self.see_info_button = ctk.CTkButton(self,text=f"See info",command=self.see_info_command)
                         

        def save_changes(self):
            cont= tk.messagebox.askokcancel(title="Warning",message="Changing the course type will restart the application. All unsaved changes will be lost. Are you sure you want to continue?")
            if cont == True:
                if self.selected_variable.get() in self.inverted_course_types:
                    self.settings.set_Course_values(self.inverted_course_types[self.selected_variable.get()])  
                    self.settings.commit_changes()
                else:
                    self.settings.set_Course_values(None)     
                    self.settings.commit_changes()  
                self.controller.mainline_obj.deep_reset()
            else: return

        def request_document_path(self,event=None):
            old_path = self.document_path
            new_path = tk.filedialog.askdirectory()
            if new_path == "":return
            import os
            if new_path != "" and os.path.isdir(new_path):
                cont= tk.messagebox.askyesno(title="Confirm change",message="Changing the exam document path will move all files currently loaded into the application. This may take some time, depending on the size of the database. \n\nAre you sure you would like to continue")
                if cont:
                    if old_path==new_path:
                        tk.messagebox.showwarning(title="Warning",message="The selected directory is the same as the old directory. The process will now be aborted.")
                        return
                    
                    cont = tk.messagebox.askokcancel(title="Warning",message="Changing the document path will restart the application. All unsaved changes will be lost. Would you like to continue?")
                    if cont == True:
                        self.document_path = new_path
                        self.settings.set_Configuration_path_values(self.document_path)
                        self.settings.commit_changes()
                        self.controller.mainline_obj.deep_reset()
                        if os.path.isdir(old_path):
                            fully_successful = CommonFunctions.clean_dir(os.path.join(old_path,"ExamDocumentManager"))
                            if fully_successful:
                                tk.messagebox.showinfo(title="Success",message="All files have been moved to the new path. The old file heirarchy has been completely destroyed as to save space on this computer.")
                            else:
                                tk.messagebox.showinfo(title="Success",message="All files have been moved to the new path. The old file heirarchy could not be fully destroyed. This most likely means files have been placed there manually (not through the application interface).\n\n To prevent wrongful file deletion, these files were left in the old file heirarchy. Click OK to view the old directory.")
                                CommonFunctions.open_file(os.path.join(old_path,"ExamDocumentManager"))
                        else:
                            tk.messagebox.showinfo(title="Success",message="The location of the exam document files has successfully been changed.")
                    else:
                        return

        def add_new_course(self,event=None):
            file_path = tk.filedialog.askopenfilename(initialdir = "Downloads",title = f"Select json file")
            self.controller.mainline_obj.course_handler.add_new_course(file_path)
            self.controller.mainline_obj.deep_reset()
            
        def open_courseconfiguration_directory_command(self,event=None):
            CommonFunctions.open_file(CommonFunctions.get_cwd_file("courses"))


        def make_grid(self,small=False):
            for row in self.course_rows:
                row.make_grid(small=small)

            row=3
            col=0

            if small:
                padx=15
                columnspan=2
            else:
                padx=(15,2)
                columnspan=1

            self.add_new_course_button.grid(row=row,column=col,padx=padx,pady=(0,5),sticky="new",columnspan=columnspan)

            if small:
                row+=1
                padx=15
            else:
                col+=1
                padx=(2,15)

            self.open_courseconfiguration_directory.grid(row=row,column=col,padx=padx,pady=(0,5),sticky="new",columnspan=columnspan)

        def __init__(self,controller,settings):
            self.course_rows=[]
            self.settings=settings
            self.controller=controller
            super().__init__(self.controller,fg_color=self.controller.mainline_obj.colors.bubble_background)

            self.columnconfigure(0,weight=1)
            self.columnconfigure(1,weight=1)

            self.course_types={}

            self.course_codes = self.controller.mainline_obj.course_objects.keys()

            for course_code in self.course_codes:
                self.course_types[course_code]=self.controller.mainline_obj.course_objects[course_code].course_name

            self.inverted_course_types = {v: k for k, v in self.course_types.items()}

            options = list(self.course_types.values())
            

            k=0

            self.course_settings_label = ctk.CTkLabel(self,text="Configuration",font=("Arial", 19))
            self.course_settings_label.grid(row=k,column=0,padx=15,pady=(15,7),sticky="nw")
            k=1

            if self.settings.get_initialconfig_flag()[0] or not self.controller.mainline_obj.current_course_config_exists():
                self.initial_config_label = ctk.CTkLabel(self,text="The application has opened in initial configuration mode, as one or more settings have not been configured. \nPlease configure them below to access the main features of the application.",fg_color="red")
                self.initial_config_label.grid(row=k,column=0,columnspan=3,padx=15,pady=15)
                k=2
            

            self.installed_courses_label = ctk.CTkLabel(self,text="Installed courses")
            self.installed_courses_label.grid(row=k,column=0,columnspan=3,padx=15,pady=15,sticky="nw")


            k=5

            # RESERVED row 3
            self.add_new_course_button = ctk.CTkButton(self,text="Add new",command=self.add_new_course)
            
            # RESERVED row 3 (col 1) or row 4 (col 0) in make_grid()
            self.open_courseconfiguration_directory = ctk.CTkButton(self,text="Open JSON file location",command=self.open_courseconfiguration_directory_command)
            

            course_errors=False
            for course in self.controller.mainline_obj.course_handler.all_courses_objects:
                course_row=self.CourseRow(self,bg_color="transparent",fg_color="transparent")
                self.course_rows.append(course_row)
                course_row.inject_functionality(course)
                course_row.grid(row=k,column=0,padx=15,pady=3,sticky="new",columnspan=3)
                if course_row.course_obj.get_valid()[0]==False:course_errors=True

                k+=1
            if course_errors:
                self.installed_courses_label.configure(text="Installed courses (fix errors)")
                self.installed_courses_label.configure(text_color="red")


            self.course_selection_label = ctk.CTkLabel(self,text="Course selection")
            self.course_selection_label.grid(row=k,column=0,columnspan=2,sticky="nw",padx=15,pady=(20,2))

            if "course_type" in self.settings.get_initialconfig_flag()[1] or not self.controller.mainline_obj.current_course_config_exists():
                self.course_selection_label.configure(text_color="red")
                self.course_selection_label.configure(text="Course selection (first install courses above)")


            k+=1


            self.selected_variable = tk.StringVar(self)
            if self.settings.course_type == "" or self.settings.course_type == None or not self.controller.mainline_obj.current_course_config_exists():
                options = ["None selected"]+ options
                self.selected_variable.set("None selected") # default value
            else:
                self.selected_variable.set(self.controller.mainline_obj.get_course_values().course_name) # default value

        

            optionmenu = ctk.CTkOptionMenu(self,values=options,variable=self.selected_variable)
            optionmenu.grid(row=k,column=0,sticky="new",padx=(15,4),pady=(0,15))

            save_changes_button = ctk.CTkButton(self, text="Save Changes",command=self.save_changes)
            save_changes_button.grid(row=k,column=1,sticky="new",padx=(4,15),pady=(0,15))
            k+=1

            self.document_path_label = ctk.CTkLabel(self,text="Exam document path (where documents are stored)")
            self.document_path_label.grid(row=k,column=0,columnspan=2,sticky="nw",padx=15,pady=2)
            if "document_path" in self.settings.get_initialconfig_flag()[1]:
                self.document_path_label.configure(text_color="red")
            k+=1

            self.browse_document_path = ctk.CTkButton(self,text="Browse",command=self.request_document_path)
            self.browse_document_path.grid(row=k,column=1,sticky="new",padx=(4,15),pady=2)

            import CommonFunctions
            self.document_path_textbox=CommonFunctions.NewEntry(self)
            self.document_path_textbox.grid(row=k,column=0,sticky="new",padx=(15,4),pady=(2 ,15))
            k+=1
            self.document_path_textbox.toggle_readonly_on()
            self.document_path_textbox.change_contents("Select path")

            if str(self.settings.get_Configuration_path()) != "None" and self.settings.get_Configuration_path() != "":
                self.document_path_textbox.change_contents(str(self.settings.get_Configuration_path()))
                self.document_path = str(self.settings.get_Configuration_path())
            else:
                self.document_path=""




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


    def make_grid(self,size):
        small=False
        if size <= 3: small=True

        self.course_settings_page.make_grid(small)


    def __init__(self,mainline_obj,scrollable_frame):
        super().__init__(scrollable_frame)
        self.mainline_obj=mainline_obj
        # setup_ui
        self.subject_row_counter=0

        self.columnconfigure(1,weight=1)
        #.columnconfigure(0,weight=1)

        self.settings_menu_frame = ctk.CTkFrame(self)
        self.settings_menu_frame.grid(row=1,column=0,sticky="nsew")

        self.settings = self.mainline_obj.settings
        self.course_settings_page=self.ConfigurationPage(self,self.mainline_obj.settings)
        self.subject_settings_page=self.SubjectSettingsPage(self,self.mainline_obj.settings)

        buttons=[{"code":"CourseSettings","text":"Configuration","command":self.show_settings_page,"param":"CourseSettings","position":"top"},]

        if not self.settings.get_initialconfig_flag()[0]:
            buttons.append({"code":"SubjectSettings","text":"Subjects","command":self.show_settings_page,"param":"SubjectSettings","position":"top"})
            

        self.navigation_menu = navigationmenu.NavigationMenu(self.settings_menu_frame,mainline_obj,buttons,text="Settings",fg_color=self.mainline_obj.colors.bubble_background,corner_radius=15,heading_font=("Arial", 22))
        self.navigation_menu.grid(row=0,column=0,padx=15,pady=15,sticky="nw")


        
        self.show_settings_page("CourseSettings")

