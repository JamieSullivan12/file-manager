import customtkinter as ctk
import tkinter as tk

class Label(ctk.CTkLabel):
    def on_change(self,event=None):
        print("CHANGE",self.winfo_width())
        #self.configure(wraplength=self.winfo_width())
    
    def __init__(self,root_window,**kwargs):
        super().__init__(root_window,**kwargs)
        #root_window.bind("<Configure>",self.on_change)
