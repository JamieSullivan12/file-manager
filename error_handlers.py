import tkinter as tk
def warning(message=None,title=None):
    if message == None:
        message="An error has occured"
    if title == None:
        title="An error has occured"
    tk.messagebox.showwarning(title=title,message=message)