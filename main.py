import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

import sys, os, UI_MainPage,UI_Settings,UI_DocumentViewer,confighandler,import_data,navigationmenu,CommonFunctions
import values_and_rules
from database import PastPaperDatabase



class GUI(ttk.Frame):

    def toplevel_frame_resize_event(self,event):
        """
        Record window size, location and maximised status in the configuration file each time it is changed
        """
        if(event.widget == self.toplevel and
           (self.toplevel_width != event.width or self.toplevel_height != event.height)):
            self.toplevel_width, self.toplevel_height = event.width, event.height
            self.settings.set_Window_values(f"{self.toplevel_width}x{self.toplevel_height}+{self.toplevel.winfo_x()}+{self.toplevel.winfo_y()}",self.toplevel.state()=="zoomed")


    def check_top_frame_size(self,min,level):
        """
        Set the size_level based onthe width of self.toplevel_frame
        
        IN:
        - min (int): the minimum width required to achieve the specified level
        - level (int): the size level to set self.size_level to if the minimum width is reached
        
        OUT:
        - (bool) specifying whether the minimum size was reached by the toplevel_frame width
        """

        if self.top_frame.winfo_width()<min:
            if self.size_level!=level:
                self.size_level=level
            return True
        return False


    def top_frame_resize_event(self, event=None, specific=None):
        """
        Sends instructions to all frame objects to resize their widgets according to a new frame size
        
        IN:
        - event (default: None): given through the tk.bind() command
        - specific (default: None, str): just send a resize command to a singular frame
        """
                    
        original_level=self.size_level

        # frame sizes can be one of 5 sizes (1=smallest,5=largest).
        # these sizes determine the overall layout of widgets inside each frame.
        # the following code will set the size level of the toplevel_frame based on the current toplevel_frame size

        if not self.check_top_frame_size(400,1):
            if not self.check_top_frame_size(600,2):
                if not self.check_top_frame_size(800,3):
                    if not self.check_top_frame_size(1000,4):
                        self.check_top_frame_size(1000000,5)

        
        if specific != None:
            if specific in self.frames:
                self.frames[specific].make_grid(self.size_level)
            return

        # if the size level has changed
        if self.size_level!=original_level:
            for frame in self.frames:
                try:
                    self.frames[frame].make_grid(self.size_level)
                except Exception as e:
                    pass


    def update_gui(self):
        self.top_frame.update()


    def clean_dir(self):
        """
        Remove all empty directories
        """
        root = os.path.join(os.getcwd(),"Papers")

        walk = list(os.walk(root))
        for path,name,file in walk:
            if len(os.listdir(path)) == 0:
                os.rmdir(path)


    def initialise_gui_class(self,gui_class):
        return gui_class(self, self.top_frame)


    def get_frame_object(self,frame_name):
        return self.frames[frame_name]


    def reset_frame(self,frame_name):
        """
        Delete and then create an entire object for a particular frame
        IN:
        - frame_name: the name of the class of the frame being reset
        """
        self.frames[frame_name].grid_forget()
        del self.frames[frame_name]

        # initalise the GUI object
        
        frame = self.initialise_gui_class(self.gui_classes[frame_name])
        self.frames[frame_name] = frame


    def resetwindows(self, show_frame=None):
        """
        Reset the entire application - all windows will be removed, and then re-generated
        """
        for frame_name in self.frames:
            self.reset_frame(frame_name)
        
        if show_frame != None:
            self.show_frame(show_frame)


    def setup_frames(self,frame_classes):
        '''
        Initialise all GUI classes
        '''

        # when GUI frames are initialised, they begin trying to change the active page (using show_frame() method). 
        # this is prevented using the ignore_setup flag.
        self.ignore_setup=True 
        
        # store all GUI pages in a dictionary.
        self.frames={}
        self.gui_classes={}

        # loop through all imported GUI objects (from other files)
        pages = frame_classes
        for page in pages:
            # if page already has been initalised, remove it
            if page.__name__ in self.frames:
                self.frames[page.__name__].pack_forget()
            

            # store the name of the class (will be used as a key in the self.frames dict)
            frame_name = page.__name__

            # initalise the GUI object.
            # TODO account for manually raised errors that track back to the mainline
            frame = self.initialise_gui_class(page)

            self.frames[frame_name] = frame
            self.gui_classes[frame_name]=page
            self.current_frame_object = frame
           
        self.ignore_setup=False


    def show_frame(self, frame_name):
        '''
        Show a requested GUI class to the user. frame_name is the name of that GUI class which needs to be shown
        '''

        # see setup_frames() method for description of self.ignore_setup
        if not self.ignore_setup:

            # remove current frame from the display
            self.current_frame_object.pack_forget()

            # place the requested frame on the display
            self.current_frame_object = self.frames[frame_name]
            self.current_frame_object.pack(expand=True,fill=tk.BOTH)

            # update shown page on the navigation menu
            self.navigation_menu.page_selected(frame_name)

            # update ALL widget elements

            self.top_frame_resize_event(specific=frame_name)


    def __init__(self, parent,root):
        super().__init__(parent)
        self.toplevel = parent
        self.toplevel_width=None
        self.toplevel_height=None
        self.root=root


        # read config file
        self.settings = confighandler.config_open()
        # set window size to last saved state
        geometry = self.settings.get_Window_geometry()
        fullscreen = self.settings.get_Window_fullscreen()
        if fullscreen != "None" and fullscreen == "True":
            parent.state('zoomed')
        elif geometry != "None":
            parent.geometry(geometry)

        # read database
        self.db_object = PastPaperDatabase(self,"pastpaperdatabase.csv")

        # default colours
        self.colors = values_and_rules.Colors()
        
        # remove all empty folders from the Past Papers directory
        self.clean_dir()


        self.toplevel.grid_columnconfigure(1, weight=1)

        self.top_frame = ctk.CTkFrame(self.toplevel,corner_radius=0,fg_color="gray90")
        self.top_frame.grid(row=0,column=1,sticky="nsew")
        self.size_level=None


        self.setup_frames([UI_MainPage.MainPage,UI_Settings.SettingsPage,UI_DocumentViewer.DocumentViewerPage,import_data.ImportDataPage])
    
        # track all size changes of the parent_frame -> any changes will be passed along to individual pages to 
        # ensure widget sizes are kept in accordance with window size restraints
        self.top_frame.bind("<Configure>",self.top_frame_resize_event)

        #            

        # navigation menu to be shown on the left hand side of the window
        nav_buttons = [
            {"code":"MainPage","text":"Home","command":self.show_frame,"param":"MainPage","position":"top"},
            {"code":"DocumentViewerPage","text":"Documents","command":self.show_frame,"param":"DocumentViewerPage","position":"top"},
            {"code":"ImportDataPage","text":"Import","command":self.show_frame,"param":"ImportDataPage","position":"top"},
            {"code":"SettingsPage","text":"Settings","command":self.show_frame,"param":"SettingsPage","position":"bottom"},
        ]
        self.navigation_menu = navigationmenu.NavigationMenu(self.toplevel,self,nav_buttons,heading_font=("Arial", 18),collapse_button=True)
        self.navigation_menu.grid(row=0, column=0, sticky="nsw")

        #                 

        menubar_items = {
            "Settings":[
                {"name":"Home","command":self.show_frame,"params":("MainPage")},
                {"name":"Documents","command":self.show_frame,"params":("DocumentViewerPage")},
                {"name":"Import","command":self.show_frame,"params":("ImportDataPage")},
                {"name":"Settings","command":self.show_frame,"params":("SettingsPage")}
            ]
        }

        # menu bar: the navigation menu shown at the top of the screen
        self.menubar=CommonFunctions.setup_menubar(self.toplevel,menubar_items)
        self.toplevel.bind("<Configure>",self.toplevel_frame_resize_event)

        self.show_frame("MainPage")






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

    parent.minsize(600,500)
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

    
