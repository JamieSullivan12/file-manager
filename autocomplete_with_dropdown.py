#!/usr/bin/env python3

# TODO: popup width should match entry width
# TODO: add scroll with mousewheel when hovering over canvas
# TODO: add scroll with arrow key movement
# TODO: add fake scroll for very long data lists
# TODO: optional show all options dropdown trigger

import tkinter as tk
import customtkinter as ctk

# default color palette
COLORS = dict(
    hover_color = 'gray70',
    selected_text_color="blue"
    )

class SelectLabel(ctk.CTkFrame):
    """this widget is a single row item in the result list
    turn color when hovered, allow for selection"""
    def __init__(self, master, controller, colors=COLORS, **kwargs):
        self.text = kwargs.pop('text','')
        self.command = kwargs.pop('command', None)
        self.colors = colors
        self.controller = controller
        super().__init__(master,fg_color="transparent", **kwargs)
        self.prefix = ctk.CTkLabel(self)
        self.prefix.pack(side=tk.LEFT, padx=(0,0))
        self.select_core = ctk.CTkLabel(self)
        self.select_core.pack(side=tk.LEFT, padx=0)
        self.rest = ctk.CTkLabel(self, text=self.text, anchor=tk.W)
        self.rest.pack(fill=tk.X, expand=True, padx=(0,0))
        

        self.prefix.bind('<Enter>', self.highlight)
        self.select_core.bind('<Enter>', self.highlight)
        self.rest.bind('<Enter>', self.highlight)

        self.prefix.bind('<Leave>', self.lowlight)
        self.select_core.bind('<Leave>', self.lowlight)
        self.rest.bind('<Leave>', self.lowlight)

        self.hovering=False

        self.next = None
        self.previous = None


    def choose(self, event=None):
        if self.command:
            self.command(self.text)

    def highlight(self, event=None):
        self.hovering=True
        self.controller.master.in_focus=True
        if self.controller.selected is not None:
            self.controller.selected.lowlight()
        self.controller.selected = self

        #self.prefix.configure(bg_color=self.colors['hover_color'])
        #self.select_core.configure(bg_color=self.colors['hover_color'])
        #self.rest.configure(bg_color=self.colors['hover_color'])
        self.configure(fg_color=self.colors['hover_color'])
        self.select_core.configure(text_color=self.colors['selected_text_color'])


    def lowlight(self, event=None):
        # will be called twice
        # by the mouse leave AND other.mouse enter ... i'm ok with this (for now)
        #self.prefix.configure(bg_color=self.colors['normal_color'])
        self.hovering=False
        if self.select_core.cget("text"):
            self.select_core.configure(text_color=self.colors['selected_text_color'])

            #self.select_core.configure(bg_color=self.colors['selected_color'])
        else:
            # this case should never happen, zero matches should delete the label.
            #self.select_core.configure(bg_color=self.colors['normal_color'])
            self.select_core.configure(text_color="black")
        self.controller.master.in_focus=False

        #self.rest.configure(bg_color=self.colors['normal_color'])
        #self.configure(bg_color=self.colors['normal_color'])
        self.configure(fg_color="transparent")

    def select(self, start=None, end=None):
        """
        select(int) ==>
        select((start, end)) OR select(start, end) ==>
        """
        try:
            start, end = start
        except:
            pass
        if start is None:
            start, end = 0, 0
        if end is None:
            start, end = 0, start
        self.prefix.configure(text=self.text[:start])
        self.select_core.configure(text=self.text[start:end])
        self.rest.configure(text=self.text[end:])
        self.select_core.configure(text_color=self.colors['selected_text_color'])

def startswith_keepcase(whole_phrase, search_phrase):
    if whole_phrase.startswith(search_phrase):
        return 0, len(search_phrase)

def startswith(whole_phrase, search_phrase):
    if whole_phrase.casefold().startswith(search_phrase.casefold()):
        return len(search_phrase)

def contains(whole_phrase, search_phrase):
    idx = whole_phrase.casefold().find(search_phrase.casefold())
    if idx >= 0:
        return idx, len(search_phrase) + idx

functions = dict(
    startswith = startswith,
    contains = contains,
    startswith_keepcase = startswith_keepcase,
    )

class OptionBox(ctk.CTkFrame):
    """the popup widget"""
    def __init__(self,controller, master, options=[], command=None, colors=COLORS, **kwargs):
        super().__init__(master,border_width=1,border_color="black",corner_radius=5,fg_color="transparent",bg_color="transparent", **kwargs)
        self.controller=controller
        self.colors = colors
        self.items = [] # a list of SelectLabel objects
        self.command = command
        self.selected = None
        self.disp_frame = self
        self.label_frame=ctk.CTkFrame(self.disp_frame,fg_color="transparent",bg_color="transparent",border_width=0)

    def move_down(self):
        if self.selected is None and self.items:
            self.items[0].highlight()
        elif self.selected is not None:
            self.selected.next.highlight()

    def move_up(self):
        if self.selected is None and self.items:
            self.items[0].previous.highlight()
        elif self.selected is not None:
            self.selected.previous.highlight()

    def lowlight(self):
        if self.selected is not None:
            self.selected.lowlight()
        self.selected = None

    def remake(self, options):
        current = {lbl.text:lbl for lbl in self.items}
        self.items = []
        self.label_frame.pack(expand=True,fill=tk.X,padx=2,pady=2)


        for text, match in options:
            if text in current:
                lbl = current.pop(text)
                lbl.pack_forget()
            else:
                lbl = SelectLabel(self.label_frame, controller=self, command=self.command, text=text, colors=self.colors)

            
            lbl.pack(expand=True, fill=tk.X,padx=0,pady=0)
            lbl.select(match)
            self.items.append(lbl)

        # delete all remaining labels
        for child in current.values():
            child.destroy()

        # set up linked list
        if self.items:
            for a, b, c in zip(self.items, self.items[1:] + [self.items[0]], [self.items[-1]] + self.items[:-1]):
                a.next, a.previous = b, c

        self.master.update_idletasks()  # Needed on MacOS -- see #34275.

class OptionBoxScroll(OptionBox):
    def __init__(self,controller, master,options=[], command=None, colors=COLORS, **kwargs):
        super().__init__(master, **kwargs)

        WIDTH = 130
        HEIGHT = 200
        canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT)
        canvas.pack(side=tk.LEFT)
        vsb = ctk.CTkScrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
        canvas.configure(yscrollcommand = vsb.set)
        self.disp_frame = ctk.CTkFrame(canvas)
        self.disp_frame.columnconfigure(0, minsize=WIDTH)
        canvas.create_window(0, 0, window=self.disp_frame, anchor='nw')

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))

        canvas.bind('<Configure>', on_configure)

class OptionBoxWarn(OptionBox):
    # subclass OptionBox instead of Frame simply to consume kwargs and populate vars
    def __init__(self, controller,master,options=[], command=None, colors=COLORS, **kwargs):
        super().__init__(controller,master, **kwargs)

        self.lbl = ctk.CTkLabel(self,bg_color="transparent")
        self.lbl.pack(expand=True,padx=2,pady=2)

    def remake(self, options):
        self.lbl.configure(text=f"<{len(options)} items match>")

class Autocomplete(ctk.CTkEntry):
    """
    A type of tk.Entry that will pop up a list of matching choices as you type
    options: list of options for the user to choose from
    hitlimit: max number of hits to show
    limit_action: One of "nothing", "warn", "scrollbar"
    func: one of "startswith", "contains" or a function to use to determine if an option matches
    kwargs: passed on to the underlying Entry
    """
    def __init__(self, master, options=None, hitlimit=10, limit_action="warn", func="startswith",placeholder_text="", **kwargs):
        self.in_focus=False
        self.ignore_startup=True
        self.colors = {key:kwargs.pop(key, COLORS[key]) for key in COLORS}
        super().__init__(master,placeholder_text=placeholder_text, **kwargs)
        self.options = options or []
        self.hitlimit = hitlimit
        self.limit_action = limit_action
        if limit_action not in ("warn", "nothing", "scrollbar"):
            raise TypeError(f'limit_action must be one of "warn", "nothing", "scrollbar", got {limit_action!r}')
        self.func = functions.get(func,func)
        self.optionbox = None
        self.ignore_next_focus_in=False
        self.ignore_flag=False

        self.counter=0
        self.bind("<Configure>",self.binded_method)


        self.ignore_startup=False
    
    def temp_deativate(self):
        self.ignore_flag=True
    def re_activate(self):
        self.ignore_flag=False


    def activate(self):
        self.bind('<Down>', self.move_down)
        self.bind('<Up>', self.move_up)
        self.bind('<Return>', self.on_return)
        self.bind('<Tab>', self.on_return)
        self.bind('<FocusOut>', self._close_popup)
        self.bind('<FocusIn>',lambda e:self._on_change(self.get()))
        self.bind('<Escape>',self._close_popup)
        vcmd = self.register(self._on_change), '%P'
        self.configure(validate="key", validatecommand=vcmd)


    def on_return(self, event=None):
        if self.optionbox and self.optionbox.selected:
            self.optionbox.selected.choose()

    def move_down(self, event=None):
        if self.optionbox:
            self.optionbox.move_down()

    def move_up(self, event=None):
        if self.optionbox:
            self.optionbox.move_up()

    def set(self, value):
        self.delete(0, tk.END)
        self.insert(0, value)
        self._close_popup()
        self.icursor(len(value))

    def insert_readonly(self,index,value):

            self.configure(state="normal")
            
            self.insert(index,value)
            self.configure(state="readonly")
    def _on_change(self, P, *args):
        if not self.ignore_flag:
            if P and not self.ignore_next_focus_in: # something was typed
                self._update_popup(P)
                self.move_down()
            else:
                self._close_popup()
            self.ignore_next_focus_in=False
            return True
        return False

    def binded_method(self,event=None):
        self.counter += 1

    def test_click(self,event=None):
        print("TEST CLICK")

    def _update_popup(self, P):
        if self.optionbox:
            self.optionbox.lowlight()

        matches = []
        for option in self.options:
            match = self.func(option, P)
            if match or P == "":
                matches.append((option, match))
        
        # sort by how well the match is (closer to the start of the string prioritised)
        matches.sort(key=lambda x: x[1][0])

        if len(matches) == 0:
            self._close_popup()
        elif len(matches) > self.hitlimit:
            if self.limit_action == 'nothing':
                self._close_popup()
            elif self.limit_action == 'warn':
                self._open_popup(OptionBoxWarn)
            elif self.limit_action == 'scrollbar':
                self._open_popup(OptionBoxScroll)
            else:
                raise TypeError(f"unknown limit action: {self.limit_action!r}")
        else:
            self._open_popup(OptionBox)

        if self.optionbox:
            self.optionbox.remake(matches)
            self.optionbox.bind("<Button-1>",self.test_click)

    def _close_popup(self, event=None):
        if self.optionbox and not self.in_focus:
            self.optionbox.master.destroy()
            self.optionbox = None
            self.ignore_next_focus_in=True

    def _open_popup(self, popup_type):
        if self.optionbox and type(self.optionbox) == popup_type:
            return # already open
        else:
            self._close_popup()

        if not self.ignore_startup:
            popup = tk.Toplevel(self, width=200)
            popup.minsize(self.winfo_width(), 1)
            popup.wm_overrideredirect(1)
            try:
                # This command is only needed and available on Tk >= 8.4.0 for OSX.
                # Without it, call tips intrude on the typing process by grabbing the focus.
                popup.tk.call("::tk::unsupported::MacWindowStyle",
                    "style", popup._w, "help", "noActivates")
            except tk.TclError:
                pass


        self.optionbox = popup_type(self,popup, command=self.set, colors=self.colors)
        self.optionbox.pack(fill=tk.BOTH, expand=True)
        popup.lift()  # work around bug in Tk 8.5.18+ (issue #24570)

        # position_window
        x, y = 0, self.winfo_height() + 1
        root_x = self.winfo_rootx() + x
        root_y = self.winfo_rooty() + y
        popup.wm_geometry("+%d+%d" % (root_x, root_y))

    def replace(self,value):
        self.delete(0,tk.END)
        self.insert(0,value)
        #self.update()

if __name__ == "__main__":
    Autocomplete.demo()
