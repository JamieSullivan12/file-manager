

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
        menubar.add_cascade(label="Settings", menu=cascade)

    # place menu bar onto the toplevel_frame widget
    toplevel_frame.config(menu=menubar)

    return menubar



def is_float(element) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False