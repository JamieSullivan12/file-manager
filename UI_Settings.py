from tkinter import ttk
import tkinter as tk
import values_and_rules


class SettingsPage(ttk.Frame):

    def save_changes(self):
        
        self.settings.course_type = self.inverted_course_types[self.selected_variable.get()]
        self.settings.commit_changes()
        self.mainline_obj.resetwindows("MainPage")

    def CourseSettingPage(self):

        self.course_frame = tk.LabelFrame(self,text="Course")

        self.course_types = values_and_rules.get_course_types()
        self.inverted_course_types = {v: k for k, v in self.course_types.items()}

        options = list(self.course_types.values())
        


        self.selected_variable = tk.StringVar(self)
        self.selected_variable.set(self.settings.course_type) # default value

        course_type_dropdown = tk.OptionMenu(self.course_frame, self.selected_variable,*options)
        course_type_dropdown.grid(row=0,column=0,sticky="nw")

        save_changes_button = ttk.Button(self.course_frame, text="Save Changes",command=self.save_changes)
        save_changes_button.grid(row=1,column=0,columnspan=2,sticky="nw")

        self.course_frame.grid(row=1,column=1,sticky="nw",padx=20,pady=25)


    def __init__(self,mainline_obj,scrollable_frame,grid_preload):
        super().__init__(scrollable_frame)
        self.mainline_obj=mainline_obj
        # setup_ui

        self.settings = self.mainline_obj.settings

        self.settings_selection_frame = tk.LabelFrame(self,text="Settings Menu")
        self.settings_selection_frame.grid(row=1,column=0,padx=15,pady=30)

        self.course_button = tk.Button(self.settings_selection_frame,text="Course",command=lambda:self.CourseSettingPage())
        self.course_button.grid(row=0,column=0,padx=30,pady=15)
