import tkinter as tk
from tkinter import ttk

class ModifiableLabel():

    def bindframe(self,frame,sequence,func):
        frame.bind(sequence, func)
        for child in frame.winfo_children():
            child.bind(sequence, func)


    def textchangerequest(self, frame, label, getter, setter, value="", prefix="", suffix=""):
        """
        Generalised code for a text field which can be edited (through a double click)
        - frame: the frame in which this event is occuring
        - label: the text (Label) field which needs to be made mofifiable
        - getter: a function which will return the current value for that field
        - setter: a function which will take (and apply) whatever the user has entered within the Entry box
        - prefix (OPTIONAL): when the user has finished entering the new value, it will be placed back into a text box - with a prefix if selected
        - suffix (OPTIONAL): when the user has finished entering the new value, it will be placed back into a text box - with a suffix if selected 
        """

        def cancel(label, entry, row, column, padx, pady, sticky):
            """
            Will destroy the entry box, and replace the label widget onto the screen (as it was initially)
            NOTE: this is called either when the user presses <Escape> or after the user presses <Enter> and the changes have been saved
            """
            entry.destroy()
            label.grid(row=row,column=column,sticky=sticky,padx=padx,pady=pady)
                    
        def apply(label, entry, row, column, padx, pady, sticky, prefix, suffix):
            """
            Will look at the Entry box for any changes, and write them to a desired lcoation (the setter method)
            """
            try:
                setter(entry.get())
            except Exception as e:
                tk.messagebox.showerror(message="Unknown error occured:\n\n" + str(e))
                cancel(label, entry, row, column, padx, pady, sticky)
                return
            
            # insert the newly entered value into the label widget which was grid forgot from the screen
            label["text"] = f"{prefix}{entry.get()}{suffix}"
            cancel(label, entry, row, column, padx, pady, sticky)

        # remember details of the current textbox (which will need to be removed for the Entry box)
        row    = label.grid_info()['row']
        column = label.grid_info()['column']
        padx = label.grid_info()['padx']
        pady = label.grid_info()['pady']
        sticky= label.grid_info()['sticky']
        # delete the label
        label.grid_forget()

        # create and place an Entry box into the location where the label was deleted
        current_value = str(getter())
        entry = ttk.Entry(frame)
        entry.grid(row=row,column=column,sticky=sticky,padx=padx,pady=pady)
        # pre-insert the value from the getter function
        entry.insert(tk.END, current_value)

        # bind return (save changes) and escape (cancel changes) keys
        entry.bind("<Return>",lambda e:apply(label, entry, row, column, padx, pady, sticky,prefix,suffix))
        entry.bind("<Escape>",lambda e:cancel(label, entry, row, column, padx, pady, sticky))


    def __init__(self, frame, text, row, column, getter, setter, padx=0, pady=0, width=20):
        """
        FUNCTION: Create a label that can switch to an entry box upon being double-clicked
        IN:
        - frame (ttk.Frame): the frame on which the label will be placed
        - text (string): the default text which the label will take (will format like "{text}{variable}") where text is the user-defined default text, and variable is the custom element defined by the getter parameter
        - row (int): row to place on the grid (on frame)
        - column (int): column to place on the grid (on frame)
        - getter (function): the function which will return the variable value being edited using this label
        - setter (function): the function which will accept a modified value for the variable being edited using this label
        - padx (int): default 0
        - pady (int): default 0
        - width (int): default 0
        """


        self.frame=frame
        self.text=text
        self.row=row
        self.column=column
        self.padx=padx
        self.pady=pady
        self.getter=getter
        self.setter=setter
        self.width=width

        self.modifiable_button = tk.Label(frame,text=self.text + ": " + str(getter()), width=self.width)
        self.modifiable_button.grid(row=self.row,column=self.column,sticky="nw",padx=padx,pady=pady)
        self.bindframe(self.modifiable_button,"<Double-Button-1>",lambda e:self.textchangerequest(self.frame,self.modifiable_button,self.getter, self.setter, prefix=self.text))


