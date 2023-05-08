import datetime
import json
import shutil
import pandas as pd
import tkinter as tk
import numpy as np
from tkinter import ttk, filedialog, messagebox
import sys, os, scrollable_frame, UI_MainPage,UI_Settings,confighandler
import UI_Popup_Edit_Row, UI_DocumentViewer,import_data
import navigationmenu
import random
import values_and_rules
import customtkinter as ctk
import uuid
from database import Database



class GUI(ttk.Frame):

    def update_gui(self):
        self.parent.update()

    def clean_dir(self):
        # remove all empty directories

        root = os.path.join(os.getcwd(),"Papers")

        walk = list(os.walk(root))
        for path, _, _ in walk[::-1]:
            if len(os.listdir(path)) == 0:
                os.rmdir(path)
                #os.remove(path)
    def setupmenubar(self):
        """ Configure the navigation bar (menubar) """
        
        # initialise menu bar object
        self.menubar = tk.Menu(self.parent)

        # create the "Settings" menu
        self.options_menu = tk.Menu(self.menubar, tearoff=False)
        self.options_menu.add_command(label="Home", command=lambda: self.showwindow("MainPage"))
        self.options_menu.add_command(label="Settings", command=lambda: self.showwindow("SettingsPage"))

        self.menubar.add_cascade(label="Settings", menu=self.options_menu)

        # create the "Navigate" menu
        self.navigate_menu = tk.Menu(self.menubar, tearoff=False)
        self.navigate_menu.add_command(label="Placeholder", command=None)
        self.menubar.add_cascade(label="Navigate", menu=self.navigate_menu)

        # place menu bar onto the toplevel_frame widget
        self.parent.config(menu=self.menubar)


    def resetwindows(self, specificwindow="", showwindow=""):
        """
        Reset the entire application - all windows will be removed, and then re-generated
        """
        # remove all windows
        for frame in self.frames:
            self.frames[frame].grid_forget()
        # regenerate all windows
        self.setupwindows()

        if showwindow != "":
            self.showwindow(showwindow)

    def resetmainpage(self):
        self.frames["MainPage"].grid_forget()
        del self.frames["MainPage"]
        # initalise the GUI object. self is passed as the mainline class. It allows all other GUI objects to access attributes and methods from this mainline class.
        frame = UI_MainPage.MainPage(self, self.scrollable_frame, grid_preload = True)

        # for easy access, add the newly created object to a dictionary
        self.frames["MainPage"] = frame


    def setupwindows(self,pre_load="", specific_window=""):
        '''
        Initialise all GUI classes
        '''

        # when other GUI pages are initialised, they may begin trying to change the active page (using showwindow() method). this is prevented using the ignore_setup flag.
        self.ignore_setup=True 
        
        # store all GUI pages in a dictionary.
        self.frames={}

        # loop through all imported GUI objects (from other files)
        pages = [UI_MainPage.MainPage,UI_Settings.SettingsPage,UI_DocumentViewer.DocumentViewerPage,import_data.ImportDataPage]
        for page in pages:
            # if page already has been initalised, remove it
            if page.__name__ in self.frames:
                self.frames[page.__name__].grid_forget()
            

            # strore the name of the class (will be used as a key in the self.frames dict)
            page_name = page.__name__

            # initalise the GUI object. self is passed as the mainline class. It allows all other GUI objects to access attributes and methods from this mainline class.
            frame = page(self, self.scrollable_frame, grid_preload = True)

            # for easy access, add the newly created object to a dictionary
            self.frames[page_name] = frame

            self.current_frame_object = frame
           
        self.ignore_setup=False

    def showwindow(self, frame_name):
        '''
        Show a requested GUI class to the user. frame_name is the name of that GUI class which needs to be shown
        '''

        #if frame_name=="UIPopupEditRow":
        #    new_document_object = self.db_object.create_new_row()
        #    loadnew_window = UI_Popup_Edit_Row.UIPopupEditRow(self, self.scrollable_frame,paper_obj=new_document_object,type="create")
        #    loadnew_window.grid(row=0,column=0,sticky="nsew")

        # see setupwindows() method for description of self.ignore_setup
        if not self.ignore_setup:
            # remove current frame from the display
            self.current_frame_object.grid_forget()
            
            # place the requested frame on the display
            self.current_frame_object = self.frames[frame_name]
            self.current_frame_object.grid(row=0,column=0,sticky="nsew")

            self.navigation_frame.page_selected(frame_name)

            # update ALL widget elements
            self.scrollable_frame.update()

            #self.parent.geometry(f"{self.current_frame_object.winfo_width()+25}x{self.current_frame_object.winfo_height()+17}+25+25")


    def __init__(self, parent,root):
        super().__init__(parent)
        self.parent = parent
        self.root=root
        self.settings = confighandler.config_open()
        self.db_object = Database("database.csv",self)

        self.colors = values_and_rules.Colors()
        

        self.clean_dir()

        # set grid layout 1x2
        #self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self.parent,corner_radius=0,fg_color="gray90")
        self.scrollable_frame.grid(row=0,column=1,sticky="nsew")
        #self.scrollable_frame.pack(side="left",expand=True,anchor="nw")
        

        self.setupwindows()
        self.showwindow
        nav_buttons = [
            {"code":"MainPage","text":"Home","command":self.showwindow,"param":"MainPage","position":"top"},
            {"code":"DocumentViewerPage","text":"New Document","command":self.showwindow,"param":"DocumentViewerPage","position":"top"},
            {"code":"ImportDataPage","text":"Import","command":self.showwindow,"param":"ImportDataPage","position":"top"},
            {"code":"SettingsPage","text":"Settings","command":self.showwindow,"param":"SettingsPage","position":"bottom"},
        ]

        self.navigation_frame = navigationmenu.NavigationMenu(self.parent,self,nav_buttons,heading_font=("Arial", 25))
        self.navigation_frame.grid(row=0, column=0, sticky="nsw")
        #self.navigation_frame.pack(side="left",expand=True,anchor="nw")
        self.update_gui()

        self.setupmenubar()

        self.update_gui()

        import dill
        with open("std1.pkl", 'wb') as file:
            dill.dump({"TEST"}, file)
            print(f'Object successfully saved to "std1.pkl"')



        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.showwindow("MainPage")

def destroyer():
    """ Handle program exit - will close all windows and command lines to prevent the program from remaining open in the background"""
    root.quit()
    root.destroy()
    sys.exit()


def start(parent,root):
    gui_obj = GUI(parent,root)

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    parent = tk.Toplevel(master=root)

    parent.title("Past Paper Manager")

    parent.minsize(910,500)
    #parent.geometry("500x500+25+25")

    parent.grid_rowconfigure(0,weight=1)
    #parent.grid_columnconfigure(0,weight=1)
    
    #loading = ttk.Label(parent,text="Loading... please wait")
    #loading.grid(row=0,column=0)
    ctk.set_default_color_theme("theme.json")
    #ctk.set_widget_scaling(1.5)
    parent.update()
    # handle program exit protocol
    root.protocol("WM_DELETE_WINDOW", destroyer)
    parent.protocol("WM_DELETE_WINDOW", destroyer)
    
    parent.after_idle(start,parent,root)
    #loading.grid_remove()
    parent.mainloop()

    
