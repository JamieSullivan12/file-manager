import tkinter as tk




class ExceptionWarning(Exception):
    def __init__(self,message=None,title=None):
        if message==None:message=""
        if title==None:title=""
        self.result=tk.messagebox.showwarning(title=title,message=message)
    def get_result(self):
        return self.result