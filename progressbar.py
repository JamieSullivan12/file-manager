import tkinter as tk
import customtkinter as ctk

class ProgressBar(tk.Toplevel):

    def update_progress_bar(self,number):
        self.progress_bar.set(number/self.total_number)
        self.update()

    def __init__(self, appear_below_widget, total_number):
        super().__init__()
        self.total_number=total_number
        label=tk.Label(self, text="Importing")
        label.grid(row=0,column=0,sticky="new")
        self.lift()  # work around bug in Tk 8.5.18+ (issue #24570)
        
        # position_window
        x, y = 0, appear_below_widget.winfo_height() + 1
        root_x = appear_below_widget.winfo_rootx() + x
        root_y = appear_below_widget.winfo_rooty()
        self.wm_geometry("+%d+%d" % (root_x, root_y))

        self.minsize(appear_below_widget.winfo_width(), 1)
        self.wm_overrideredirect(1)
        try:
            # This command is only needed and available on Tk >= 8.4.0 for OSX.
            # Without it, call tips intrude on the typing process by grabbing the focus.
            self.tk.call("::tk::unsupported::MacWindowStyle",
                "style", self._w, "help", "noActivates")
        except tk.TclError:
            pass

        
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal")
        self.progress_bar.grid(row=1, column=0,sticky="new")#.pack(fill=tk.X, expand=1, side=tk.BOTTOM)
        self.progress_bar.set(0)
        self.progress_bar.stop()
        self.pack_slaves()

        return