import customtkinter as ctk
import os, sys, subprocess




def clean_dir(root_directory):
    """
    Remove all empty directories
    """

    walk = list(os.walk(root_directory,topdown=False))
    fully_successful =True
    
    for path,name,file in walk:

        if len(os.listdir(path)) == 0:
            os.rmdir(path)
        else:
            fully_successful=False
    return fully_successful

def open_file(filename):
    """
    Opens the specified file using the default application based on the user's operating system.

    Parameters:
        filename (str): The path of the file to be opened.

    Returns:
        None
    """
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])
        

class NewEntry(ctk.CTkEntry):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.readonly=False

    
    def toggle_readonly_on(self):
        self.readonly=True
        self.configure(state="readonly")

    def change_contents(self,new_content):
        if new_content == None or new_content == "":
            self.clear()
        else:
            self.configure(state="normal")
            self.delete(0,ctk.END)
            self.insert(0,new_content)
            if self.readonly:
                self.configure(state="readonly")

    def clear(self):
        self.configure(state="normal")
        self.delete(0,ctk.END)
        if self.readonly:
            self.configure(state="readonly")

def setup_menubar(toplevel_frame,menubar_items):

    class MenuBarItem():
        def __init__(self,cascade,name,command,params):
            self.name=name
            self.command=command
            self.params=params
            cascade.add_command(label=self.name, command=lambda: self.command(self.params))

    import tkinter as tk

    """
    Create and configure the menubar 
    IN:
    - toplevel_frame (tk.Toplevel): on which the menubar is placed
    - menubar_items (dict): a dictionary in the form

    {
        key: menubar cascade name
        value: array of dicts [{"name":str,"command":func,"params":set}]
    }

    OUT:
    - menubar (tk.Menu): menubar object
    """
    
    # initialise menu bar object
    menubar = tk.Menu(toplevel_frame)


    for cascade_name in menubar_items:
        cascade = tk.Menu(menubar, tearoff=False)
        for menu_item in menubar_items[cascade_name]:
            menu_item_name = menu_item["name"]
            menu_item_command = menu_item["command"]
            menu_item_params = menu_item["params"]
            MenuBarItem(cascade,menu_item_name,menu_item_command,menu_item_params)
        menubar.add_cascade(label=cascade_name, menu=cascade)

    # place menu bar onto the toplevel_frame widget
    toplevel_frame.config(menu=menubar)

    return menubar




def is_int(element) -> bool:
    try:
        int(element)
        return True
    except ValueError:
        return False
def is_float(element) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False
    


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception as e:
        base_path = os.path.abspath(".")
    return os.path.join(base_path,relative_path)


def check_in_random_location():
    """
    https://developer.apple.com/forums/thread/724969
    App translocation (occurs when app bypasses macos system security). This opens the app in a random working directory on the Mac. 
    This will result in the resources folder (based on the working directory) being in the random folder, rather than in the correct app location.
    The user should be warned of this and be made to move the application before opening it (this bypasses security).
    """

    import platform
    import os

    if platform.system() == "Darwin": # MacOS
        # working directory for app on MacOS
        from AppKit import NSBundle
        file = NSBundle.mainBundle().pathForResource_ofType_("test", "py")
        actual_file = file or os.path.realpath("test.py")
        if (actual_file.startswith("private/var/folders") or actual_file.startswith("/private/var/folders")) and ("AppTranslocation" in actual_file):
            return True
    return False

def format_date(date):
    if date == None:return ""
    return date.strftime("%d/%m/%Y")


def get_cwd_file(filename):
    """Get working directory path (system specific for macos/windows)"""

    import platform

    name = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[1]
    if platform.system() == "Darwin": # MacOS
        # working directory for app on MacOS
        from AppKit import NSBundle
        file = NSBundle.mainBundle().pathForResource_ofType_(name, ext)
        return file or os.path.realpath(filename)
    else:
        return os.path.realpath(filename)


def grid_apply(widget,rc,cc,c_mod,r_mod,**kwargs):
    """
    Grid an widget onto the screen based on the row count (rc) and column count (cc). Increment rc and cc accordingly to match the 
    modulus requirements defined by c_mod and r_mod

    IN
    - widget (tk.Widget or ctk.Widget): the widget to be gridded
    - rc (int): row for grid
    - cc (int): column for grid
    - c_mod (int): the column value for which row is incremented and column count (cc) is reset
    - r_mod (int): the row value for which column is incremented and row count (rc) is reset
    
    Helpful trick:  
    - a higher r_mod than c_mod will reslt in a restricted number of rows (and unrestricted number of columns given enough widgets)
    - a higher c_mod than r_mod will reslt in a restricted number of columns (and unrestricted number of rows given enough widgets)
    """

    try:
        widget.grid_forget()
    except Exception as e:
        pass

    widget.grid(row=rc,column=cc,**kwargs)
    cc+=1
    if cc%c_mod==0:
        rc+=1
        cc-=c_mod
    
    if rc%r_mod==0 and rc!=0:
        cc+=c_mod
        rc-=r_mod
    
    return rc,cc