import tkinter as tk
from tkinter import ttk
import customtkinter


class ScrollableFrameCT(customtkinter.CTkScrollableFrame):
    def __init__(self,mainline,toplevel_frame):
        super().__init__(toplevel_frame)

        self.toplevel_frame = toplevel_frame

        # scrollbars can only be made on canvases
        self.scrollable_canvas = tk.Canvas(self.toplevel_frame, bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.toplevel_frame, orient="vertical", command=self.scrollable_canvas.yview)
        self.hscrollbar = ttk.Scrollbar(self.toplevel_frame, orient="horizontal", command=self.scrollable_canvas.xview)

        # create the scrollable frame widget and place it on the canvas
        # Note: the act of creating the scrollable_frame widget is simply extending the ttk.Frame class 
        
        # place the frame on the canvas
        self.scrollable_canvas.create_window((0,0), window=self, anchor='nw')

        # setup the scrolling actions
        self.bind("<Configure>", lambda e: self.scrollable_canvas.configure(scrollregion = self.scrollable_canvas.bbox("all")))
        self.scrollable_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_canvas.configure(xscrollcommand=self.hscrollbar.set)
        self.hscrollbar.grid(row=1, column=0, sticky="ew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.scrollable_canvas.grid(row=0, column=0, sticky="nsew")

        # bind mousewheel to scrolling action
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.update()


    '''
    Link scrolling of the mouse wheel to the scrollbar
    - _bound_to_mousewheel: called whenever the pointer enters the canvas
    - _unbound_to_mousewheel: called whenever the pointer leaves the canvas
    - _on_mousewheel: called whenever the mousewheel scroll is detected (unless pointer is 
        outside of canvas)
    '''
    def _bound_to_mousewheel(self, event):
        self.scrollable_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    def _unbound_to_mousewheel(self, event):   
        self.scrollable_canvas.unbind_all("<MouseWheel>")
    def _on_mousewheel(self, event):
        if self.vscrollable:
            self.scrollable_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    
    def update(self):
        """
        Update the scrollwheels on the scrollable frame to match contents
        """
        self.toplevel_frame.update_idletasks()
        if self.toplevel_frame.winfo_height() >= self.winfo_height()+20:
            self.vscrollable=False
        else:
            self.vscrollable=True

        self.scrollable_canvas.update_idletasks()
        self.scrollable_canvas.config(scrollregion=self.bbox())
    


class ScrollableFrame(ttk.Frame):
    """
    Create a container frame that has vertical AND horizontal scrolling.
    Note: this class requires a container frame to be passed as a parameter.
    Note: this class extends the ttk.Frame class. The scrollable frame IS this class
    """
    def __init__(self,toplevel_frame):
        self.toplevel_frame = toplevel_frame

        # scrollbars can only be made on canvases
        self.scrollable_canvas = tk.Canvas(self.toplevel_frame, bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.toplevel_frame, orient="vertical", command=self.scrollable_canvas.yview)
        self.hscrollbar = ttk.Scrollbar(self.toplevel_frame, orient="horizontal", command=self.scrollable_canvas.xview)

        # create the scrollable frame widget and place it on the canvas
        # Note: the act of creating the scrollable_frame widget is simply extending the ttk.Frame class 
        super().__init__(self.scrollable_canvas)
        
        # place the frame on the canvas
        self.scrollable_canvas.create_window((0,0), window=self, anchor='nw')

        # setup the scrolling actions
        self.bind("<Configure>", lambda e: self.scrollable_canvas.configure(scrollregion = self.scrollable_canvas.bbox("all")))
        self.scrollable_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_canvas.configure(xscrollcommand=self.hscrollbar.set)
        self.hscrollbar.grid(row=1, column=0, sticky="ew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.scrollable_canvas.grid(row=0, column=0, sticky="nsew")

        # bind mousewheel to scrolling action
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.update()


    '''
    Link scrolling of the mouse wheel to the scrollbar
    - _bound_to_mousewheel: called whenever the pointer enters the canvas
    - _unbound_to_mousewheel: called whenever the pointer leaves the canvas
    - _on_mousewheel: called whenever the mousewheel scroll is detected (unless pointer is 
        outside of canvas)
    '''
    def _bound_to_mousewheel(self, event):
        self.scrollable_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    def _unbound_to_mousewheel(self, event):   
        self.scrollable_canvas.unbind_all("<MouseWheel>")
    def _on_mousewheel(self, event):
        if self.vscrollable:
            self.scrollable_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    
    def update(self):
        """
        Update the scrollwheels on the scrollable frame to match contents
        """
        self.toplevel_frame.update_idletasks()
        if self.toplevel_frame.winfo_height() >= self.winfo_height()+20:
            self.vscrollable=False
        else:
            self.vscrollable=True

        self.scrollable_canvas.update_idletasks()
        self.scrollable_canvas.config(scrollregion=self.bbox())
    