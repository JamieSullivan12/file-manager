from tkinter import ttk
import tkinter as tk
import customtkinter as ctk
import values_and_rules
import navigationmenu


class SettingsPage(ctk.CTkFrame):

    def save_changes(self):
        
        self.settings.course_type = self.inverted_course_types[self.selected_variable.get()]
        self.settings.commit_changes()
        self.mainline_obj.resetwindows("MainPage")

    def CourseSettingPage(self):

        self.navigation_menu.page_selected("CourseSettings")
        self.course_frame = ctk.CTkFrame(self,fg_color=self.mainline_obj.colors.bubble_background)

        self.course_types = values_and_rules.get_course_types()
        self.inverted_course_types = {v: k for k, v in self.course_types.items()}

        options = list(self.course_types.values())
        
        self.course_settings_label = ctk.CTkLabel(self.course_frame,text="Course Selection",font=("Arial", 19))
        self.course_settings_label.grid(row=0,column=0,padx=15,pady=(15,7),sticky="nw")

        self.selected_variable = tk.StringVar(self)
        self.selected_variable.set(values_and_rules.get_course_types()[self.settings.course_type]) # default value


        #optionmenu_var = ctk.StringVar(value="option 2")
        optionmenu = ctk.CTkOptionMenu(self.course_frame,values=options,variable=self.selected_variable)
        optionmenu.grid(row=1,column=0,sticky="nw",padx=15,pady=7)
        #course_type_dropdown = tk.OptionMenu(self.course_frame, self.selected_variable,*options)
        #course_type_dropdown.grid(row=0,column=0,sticky="nw")

        save_changes_button = ctk.CTkButton(self.course_frame, text="Save Changes",command=self.save_changes)
        save_changes_button.grid(row=2,column=0,sticky="nw",padx=15,pady=7)

        self.course_frame.grid(row=0,column=1,sticky="nsew",padx=(0,15),pady=15)

    def show_settings_page(self,page):
        if page == "CourseSettings":
            self.CourseSettingPage()



    def __init__(self,mainline_obj,scrollable_frame,grid_preload):
        super().__init__(scrollable_frame)
        self.mainline_obj=mainline_obj
        # setup_ui

        self.columnconfigure(1,weight=1)
        #.columnconfigure(0,weight=1)

        self.settings_menu_frame = ctk.CTkFrame(self)
        self.settings_menu_frame.grid(row=1,column=0,sticky="nsew")

        self.settings = self.mainline_obj.settings

        buttons=[
            {"code":"CourseSettings","text":"Course","command":self.show_settings_page,"param":"CourseSettings","position":"top"},
            {"code":"OtherSettings","text":"Other","command":self.show_settings_page,"param":"Other","position":"top"},
        ]

        self.navigation_menu = navigationmenu.NavigationMenu(self.settings_menu_frame,mainline_obj,buttons,text="Settings",fg_color=self.mainline_obj.colors.bubble_background,corner_radius=15,heading_font=("Arial", 22))
        self.navigation_menu.grid(row=0,column=0,padx=15,pady=15,sticky="nw")

