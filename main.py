import tkinter as tk
from tkinter import ttk
import webbrowser
import customtkinter as ctk
import sys, custom_errors
import UI_main_page, UI_Settings, UI_documents_page, config_handler, UI_import_data
#from database_handler import PastPaperDatabase
from sql_handler import PastPaperDatabase
import course_handler
import navigationmenu
import CommonFunctions,appdirs,os
import updater, requests


class Colors:
    """Class to store color values used in the GUI."""

    def __init__(self):
        self.navbar_button_text = ("gray10", "gray90")
        self.navbar_button_hover = ("gray70", "gray30")
        self.navbar_frame_fg = "gray70"
        self.bubble_background = ("gray80", "gray20")
        self.secondary_bubble_background = ("gray75","gray25")


class GUI(ttk.Frame):
    """Main GUI class to handle the application's user interface."""

    def __init__(self, parent, root):
        super().__init__(parent)
        self.toplevel = parent
        self.toplevel_width = None
        self.toplevel_height = None
        self.root = root
        self.ignore_setup = True
        self.initial_setup = False
        self.frames = {}
        self.colors = Colors()
        self.size_level=0

        self.updater_obj = updater.Updater()



        #self.current_version = self.updater_obj.get_current_version_key
        self.current_version = self.updater_obj.get_current_version()

        self.appdata_directory = self.get_appdata_directory("ExamDocumentManager",["EDM","Exam Document Manager","ExamFileManager","EFM","Exam File Manager"],"EDM",self.current_version["major"],self.current_version["minor"],self.current_version["minor_minor"])
        self.courses_directory = os.path.join(self.appdata_directory,"courses")

        self.settings = config_handler.config_open(self,self.appdata_directory)
        self.toplevel.bind("<Configure>", self.toplevel_frame_resize_event)

        self.update_available = False   
        #self.toplevel.grid_columnconfigure(1, weight=1)  # Make toplevel resize with parent's width
        self.toplevel.grid_columnconfigure(2, weight=1)  # Make toplevel resize with parent's width

        self.top_frame = ctk.CTkFrame(self.toplevel, corner_radius=0)
        self.top_frame.grid(row=0, column=2, sticky="nsew")
        self.top_frame.bind("<Configure>",self.top_frame_resize_event)
        self.loading_label = ctk.CTkLabel(self.top_frame, text="Checking for updates...")
        self.pack_loading_label()
        self.loading_label_value("Checking for updates...")

        # set the window geometry and fullscreen status (based on when the application was last closed)
        geometry = self.settings.get_Window_geometry()
        fullscreen = self.settings.get_Window_fullscreen()
        if fullscreen != "None" and fullscreen == "True":
            parent.state('zoomed')
        elif geometry != "None":
            parent.geometry(geometry)



        # handle connection timeout
        try:
            self.github_latest_version = requests.get("https://api.github.com/repos/JamieSullivan12/Exam-Document-Manager/releases/latest",timeout=3)

            self.loading_label_value("Connected to server")

        
            self.github_latest_version.json()['name']
            
            latest_version_check = self.settings.get_latest_version_check()

            self.update_available = latest_version_check != self.current_version
            if self.update_available:
                

                self.latest_version = self.github_latest_version.json()['name']
            else:
                
                self.latest_version = None
            if latest_version_check != self.github_latest_version.json()['name']:
                self.loading_label_value("Update available")
                response = tk.messagebox.askyesno("New version available!",f"A new version of Exam Document Manager is available. Your current version is {self.current_version['major']}.{self.current_version['minor']}.{self.current_version['minor_minor']}. v{self.github_latest_version.json()['name']} is available. Please visit https://github.com/JamieSullivan12/Exam-Document-Manager to download it. Would you like to be taken to the download page?")
                if response == "yes" or response == True:
                    self.open_github_releases_page()
                self.settings.set_latest_version_check(self.github_latest_version.json()['name'])
            else:
                self.loading_label_value("Up to date")
        except requests.exceptions.ConnectionError as e:
            pass
        except requests.exceptions.JSONDecodeError as e:
            pass
        except Exception as e:
            pass
        


        self.size_level = None




        # Navigation menu to be shown on the left-hand side of the window
        nav_buttons = [
            {"code": "MainPage", "text": "Home", "command": self.show_frame, "param": "MainPage", "position": "top"},
            {"code": "DocumentViewerPage", "text": "Documents", "command": self.show_frame,
             "param": "DocumentViewerPage", "position": "top"},
            {"code": "ImportDataPage", "text": "Import", "command": self.show_frame, "param": "ImportDataPage",
             "position": "top"},
            {"code": "SettingsPage", "text": "Settings", "command": self.show_frame, "param": "SettingsPage",
             "position": "bottom"},
        ]
        self.navigation_menu = navigationmenu.NavigationMenu(self.toplevel, nav_buttons, self.colors.bubble_background, heading_font=("Arial", 18),
                                                            collapse_button=True)
        self.menubar_items = {
            "File": [
                {"name": "Restart", "command": restart_program, "params": self},
                {"name": "Quit", "command": self.quit_application, "params": ()},
            ],
            "Window": [
                {"name": "Maximise", "command": self.maximize_window, "params": ()},
                {"name": "Minimise", "command": self.minimize_window, "params": ()},
                {"name": "Restore Down", "command": self.restore_window, "params": ()},
            ],
            "Navigation": [
                {"name": "Home", "command": self.show_frame, "params": ("MainPage")},
                {"name": "Documents", "command": self.show_frame, "params": ("DocumentViewerPage")},
                {"name": "Import", "command": self.show_frame, "params": ("ImportDataPage")},
                {"name": "Settings", "command": self.show_frame, "params": ("SettingsPage")},
            ],
        }

        # Check if the application should start the final setup or show the SettingsPage
        if self.final_setup():
            self.show_frame("MainPage")
        else:
            self.show_frame("SettingsPage")
        self.initial_setup = False


        self.pack_forget_loading_label()

    def open_github_releases_page(self):
        webbrowser.open("https://github.com/JamieSullivan12/Exam-Document-Manager/releases/latest")


    def pack_forget_loading_label(self):
        self.loading_label.pack_forget()
    
    def pack_loading_label(self):
        self.loading_label_value()
        self.loading_label.pack(padx=10, pady=10,side=tk.TOP,anchor="nw")
        self.loading_label.update()

    def loading_label_value(self,value=""):
        if value == "" or value == "None":
            self.loading_label.configure(text="Loading...")
        else:
            self.loading_label.configure(text=str(value))
        self.loading_label.update()

    def create_semantic_version(self, major, minor, minor_minor):
        return f"{major}.{minor}.{minor_minor}"

    def get_appdata_directory(self,app_name, fallback_names=None, signature="EDM",version_major=1,verson_minor=0,version_minor_minor=0):
        """
        Get the directory path for application data files in the AppData folder.

        Args:
            app_name (str): The name of the application.
            fallback_names (list, optional): A list of fallback names to try if the primary app name is unavailable.
            signature (str): The expected content of the signature file.
            inner_folder (str): The name of the inner folder to use for the application data files.

        Returns:
            str: The directory path for application data files.
        """
        # Determine the appropriate AppData directory paths
        appdirs_dir = appdirs.user_data_dir(app_name, appauthor=False)

        full_inner_folder=f"user-data"
        full_appdirs_dir = os.path.join(appdirs_dir,full_inner_folder)

        counter=0
        while os.path.exists(appdirs_dir):
            # Check if the signature file is present and contains the expected signature
            signature_file_path = os.path.join(full_appdirs_dir, "app_signature.txt")
            # If the signature file does not exist, or the signature is invalid, a fallback AppData name must be used.
            if not os.path.exists(signature_file_path) or not self.verify_signature(signature_file_path, signature):
                appdirs_dir = appdirs.user_data_dir(fallback_names[counter], appauthor=False)
                full_appdirs_dir = os.path.join(appdirs_dir,full_inner_folder)
                counter+=1
            else:
                break

        # Now that an AppData folder name not in use or with a valid signature has been found,
        # Create the inner folder which will contain AppData for this specific version of the Application.
        if not os.path.exists(full_appdirs_dir):
            # Create the directory if it doesn't exist
            os.makedirs(full_appdirs_dir, exist_ok=True)

        # Check if the signature file is present and contains the expected signature
        signature_file_path = os.path.join(full_appdirs_dir, "app_signature.txt")
        if not os.path.exists(signature_file_path) or not self.verify_signature(signature_file_path, signature):
            self.create_signature_file(signature_file_path, signature)

        appdata_version = f"{version_major}.{verson_minor}.{version_minor_minor}"

        appdata_version = self.updater_obj.open_version_file(full_appdirs_dir, appdata_version)

        self.updater_obj.update(appdata_version)

        return full_appdirs_dir

    def verify_signature(self,signature_file_path, expected_signature):
        """
        Verify if the content of the signature file matches the expected signature.

        Args:
            signature_file_path (str): Path to the signature file.
            expected_signature (str): The expected content of the signature file.

        Returns:
            bool: True if the signature is valid, False otherwise.
        """
        if os.path.exists(signature_file_path):
            with open(signature_file_path, "r") as file:
                actual_signature = file.read().strip()
                return actual_signature == expected_signature
        return False

    def create_signature_file(self,signature_file_path, signature):
        """
        Create the signature file with the specified signature.

        Args:
            signature_file_path (str): Path to the signature file.
            signature (str): The content of the signature file.
        """
        with open(signature_file_path, "w") as file:
            file.write(signature)


    def quit_application(self,event=None):
        """Quit the application."""
        self.toplevel.destroy()

    def restore_window(self,event=None):
        """Restore the application window."""
        self.toplevel.state('normal')

    def maximize_window(self,event=None):
        """Maximize the application window."""
        self.toplevel.state('zoomed')

    def minimize_window(self,event=None):
        """Minimize the application window."""
        self.toplevel.iconify()

    def setup_frames(self, frame_classes, extra_arg = None):
        """Initialize all GUI classes lazily."""
        self.gui_classes = {}
        self.frames = {}

        self.loading_label_value("Initialising UI...")
        total = len(frame_classes)
        counter=0

        for page in frame_classes:
            percentage = counter
            self.loading_label_value("Initialising UI... "+str(percentage)+"%")
            frame_name = page.__name__
            if frame_name not in self.frames:
                frame = self.initialise_gui_class(page,extra_arg=extra_arg)
                self.frames[frame_name] = frame
                self.gui_classes[frame_name] = page
                self.current_frame_object = frame

        self.loading_label_value("UI initialisation complete")
        self.ignore_setup = False

    def initialise_gui_class(self, gui_class, extra_arg=None):
        """Create and return an instance of the given GUI class."""
        if extra_arg != None:
            return gui_class(self, self.top_frame, extra_arg)
        else:
            return gui_class(self, self.top_frame)

    def toplevel_frame_resize_event(self, event):
        """
        Record window size, location, and maximized status in the configuration file each time it is changed.
        """
        if event.widget == self.toplevel and (self.toplevel_width != event.width or
                                              self.toplevel_height != event.height):
            self.toplevel_width, self.toplevel_height = event.width, event.height
            self.settings.set_Window_values(f"{self.toplevel_width}x{self.toplevel_height}+"
                                            f"{self.toplevel.winfo_x()}+{self.toplevel.winfo_y()}",
                                            self.toplevel.state() == "zoomed")

    def check_top_frame_size(self, min_width, level):
        """
        Set the size_level based on the width of self.toplevel_frame.

        Args:
        - min_width (int): the minimum width required to achieve the specified level
        - level (int): the size level to set self.size_level to if the minimum width is reached

        Returns:
        - (bool): specifying whether the minimum size was reached by the toplevel_frame width
        """
        if self.top_frame.winfo_width() < min_width:
            if self.size_level != level:
                self.size_level = level
            return True
        return False

    def top_frame_resize_event(self, event=None, specific=None):
        """
        Send instructions to all frame objects to resize their widgets according to a new frame size.

        Args:
        - event (default: None): given through the tk.bind() command
        - specific (default: None, str): just send a resize command to a singular frame
        """
        original_level = self.size_level

        # Frame sizes can be one of 5 sizes (1=smallest, 5=largest).
        # These sizes determine the overall layout of widgets inside each frame.
        # The following code will set the size level of the toplevel_frame based on the current toplevel_frame size
        if not self.check_top_frame_size(400, 1):
            if not self.check_top_frame_size(600, 2):
                if not self.check_top_frame_size(800, 3):
                    if not self.check_top_frame_size(1000, 4):
                        self.check_top_frame_size(1000000, 5)

        if specific is not None:
            if specific in self.frames:
                self.frames[specific].make_grid(self.size_level)
            return

        # If the size level has changed
        if self.size_level != original_level:
            for frame in self.frames:
                try:
                    self.frames[frame].make_grid(self.size_level)
                except Exception as e:
                    pass



    def update_gui(self):
        """Update the GUI elements."""
        self.top_frame.update()

    def get_frame_object(self, frame_name):
        """Get the instance of a specific frame."""
        return self.frames[frame_name]

    def reset_frame(self, frame_name):
        """
        Delete and then create an entire object for a particular frame.

        Args:
        - frame_name (str): the name of the class of the frame being reset
        """
        self.frames[frame_name].grid_forget()
        del self.frames[frame_name]

        frame = self.initialise_gui_class(self.gui_classes[frame_name])
        self.frames[frame_name] = frame

    def resetwindows(self, move_path=None, show_frame=None):
        """
        Reset the entire application - all windows will be removed, and then re-generated.
        """
        if self.final_setup(move_path=move_path):
            if show_frame is not None:
                self.show_frame(show_frame)
            else:
                self.show_frame("MainPage")
        else:
            self.show_frame("SettingsPage")

    def show_frame(self, frame_name):
        """
        Show a requested GUI object to the user.

        Args:
        - frame_name (str): the name of the class which needs to be shown
        """
        print(self.current_frame_object,type(self.current_frame_object))
        if not self.ignore_setup:
            self.current_frame_object.remove_from_pack()
            self.current_frame_object = self.frames[frame_name]
            self.current_frame_object.add_to_pack(expand=True, anchor="nw", fill=tk.BOTH)
            self.navigation_menu.page_selected(frame_name)
            self.top_frame_resize_event(specific=frame_name)

    def deep_reset(self, move_path=None,show_frame="MainPage"):
        """Reset the application to the specified frame."""
        self.pack_loading_label()
        
        self.current_frame_object.remove_from_pack()
        self.top_frame.update()
        self.resetwindows(move_path=move_path,show_frame=show_frame)

        self.pack_forget_loading_label()

    def grid_navigation_menu(self):
        """Grid the navigation menu."""
        self.navigation_menu.grid(row=0, column=0, sticky="nsew")

    def get_course_values(self):
        """Get the course values."""
        return self.course_objects[self.settings.get_course_type()]

    def setup_courses(self):
        """Set up the course configurations."""
        self.course_handler = course_handler.CoursesHandler(CommonFunctions.get_cwd_file("courses"),os.path.join(self.appdata_directory,"courses"))
        self.course_objects = self.course_handler.course_objects

        if self.settings.get_course_type() not in self.course_handler.course_objects:
            if len(self.course_handler.course_objects) > 0:
                return True
            else:
                tk.messagebox.showwarning(title="Error", message="No course configurations exist. "
                                                                     "Please download and install a JSON "
                                                                     "configuration file from the web")
                return False
        return True

    def current_course_config_exists(self):
        """Check if the current course configuration exists."""
        if self.settings.get_course_type() and self.settings.get_course_type() in self.course_objects:
            return True
        return False

    def final_setup(self,move_path=None):
        """""
        Perform the final setup for the application.

        Returns:
        - bool: True if the setup is successful, False otherwise.
        """""
        if not self.initial_setup:
            self.setup_courses()
        if self.settings.get_initialconfig_flag()[0] is False and len(self.course_handler.course_objects) > 0:
            
            #try:
            # menu bar: the navigation menu shown at the top of the screen
            self.database_path=self.settings.get_Configuration_path()

            self.db_object = PastPaperDatabase(self, self.database_path,"pastpaperdatabase.db",move_path=move_path)
            self.updater_obj.link_database_object(self.db_object)
            self.db_object.load_database()
            self.setup_frames([UI_main_page.MainPage, UI_Settings.SettingsPage,
                            UI_documents_page.DocumentViewerPage, UI_import_data.ImportDataPage])
            self.menubar=CommonFunctions.setup_menubar(self.toplevel,self.menubar_items)
            self.grid_navigation_menu()
            #except Exception as e:
            #    self.toplevel.config(menu="")
            #    tk.messagebox.showwarning(title="Error occured",message=str(e))
            #    self.setup_frames([UI_Settings.SettingsPage],extra_arg = True)
            #    self.navigation_menu.grid_forget()
            #    return False
            return True
        else:
            try:
                self.navigation_menu.grid_forget()
            except Exception as e:
                pass
            try:
                self.toplevel.config(menu="")
            except Exception as e:
                pass
            self.navigation_menu.grid_forget()
            self.setup_frames([UI_Settings.SettingsPage])
            return False

    def destroyer(self,event=None):
        """
        Destroy the root window and exit the program.
        """
        self.root.quit()
        self.root.destroy()
        

def restart_program(current_mainline_obj):
    current_mainline_obj.destroyer()
    initialisation()



def start(parent, root):
    try:
        gui_obj = GUI(parent, root)
    except custom_errors.CriticalError as e:
        # Display critical error message and exit the program
        tk.messagebox.showerror(title="Critical Error", message=str(e))
        sys.exit(1)

def initialisation():

    def destroyer(event=None):
        """
        Destroy the root window and exit the program.
        """
        root.quit()
        root.destroy()
        sys.exit()
    # Create and configure the root window
    root = tk.Tk()
    root.withdraw()
    parent = tk.Toplevel(master=root)
    parent.title("Exam Document Manager")
    parent.minsize(450, 350)



    try:
        ctk.set_default_color_theme(CommonFunctions.get_cwd_file("theme.json"))
    except Exception as e:
        pass
    # Update the window to get the correct .winfo_width() and .winfo_height() values
    parent.update() 

    # Check if the application is in a random location - this is a security feature of MacOS when running for the first time
    if CommonFunctions.check_in_random_location():
        tk.messagebox.showwarning(title="MacOS security error",
                                  message="MacOS Gatekeeper has prevented the application from opening properly. "
                                          "\n\nPlease try moving your app to a different location, then re-opening "
                                          "it (do not use your Downloads folder). \n\nIf the error persists, "
                                          "contact support.")
        destroyer()

    parent.grid_rowconfigure(0, weight=1)

    # Handle program exit protocol
    root.protocol("WM_DELETE_WINDOW", destroyer)
    parent.protocol("WM_DELETE_WINDOW", destroyer)

    parent.after_idle(start, parent, root)
    parent.mainloop()

if __name__ == '__main__':
    
    initialisation()