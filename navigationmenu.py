import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

class NavigationMenu(ctk.CTkFrame):
    """
    A custom navigation menu implemented using customtkinter.
    """

    def __init__(self, frame, buttons, bubble_background, text="Navigation", corner_radius=0, height=40, border_spacing=20, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("#325882", "#14375e"), heading_font=("Arial", 21), collapse_button=False):
        """
        Initialize the NavigationMenu.

        Args:
            frame (tkinter.Frame): The parent frame for the navigation menu.
            bubble_background (str): The background color for the navigation menu.
            buttons (list of dict): A list containing dictionaries, where each dictionary represents a button's details.
                Each button dictionary should have the following structure:
                {
                    "text": str,         # The text displayed on the button.
                    "command": callable, # The function to be executed when the button is clicked.
                    "param": Any,        # Optional parameter to be passed to the command function. (Can be None)
                    "position": str      # The position of the button, either "top" or "bottom".
                }            
            text (str): Text to be displayed as the heading of the menu.
            corner_radius (int): The corner radius for buttons.
            height (int): The height of buttons.
            border_spacing (int): The spacing between buttons.
            fg_color (str): The foreground color for buttons.
            text_color (tuple): Tuple containing normal and hover text colors.
            hover_color (tuple): Tuple containing normal and hover button colors.
            heading_font (tuple): Tuple representing the font for the heading.
            collapse_button (bool): Whether to include collapse button or not.
        """
        super().__init__(frame, corner_radius=0, border_width=0, fg_color=bubble_background)
        self.bubble_background = bubble_background
        self.collapse_button_flag = collapse_button

        if self.collapse_button_flag:
            # Collapse and expand buttons for the navigation menu
            self.expand_button = ctk.CTkButton(self, text="≡", command=self.expand, border_spacing=0, width=30, font=(None, 35), fg_color="transparent", bg_color="transparent")
            self.collapse_button = ctk.CTkButton(self, text="✕", command=self.collapse, border_spacing=0, width=15, font=(None, 20), fg_color="transparent", bg_color="transparent")

        self.height = height
        self.border_spacing = border_spacing
        self.fg_color = fg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.buttons = buttons
        self.grid_rowconfigure(1, weight=1)
        self.navigation_frame = ctk.CTkFrame(self, fg_color="transparent",border_width=0)
        self.navigation_label = ctk.CTkLabel(self, text_color=self.text_color, anchor="w", height=40, text=text, font=heading_font)
        self.expand()

        row = 0

        separator = ttk.Separator(self.navigation_frame, orient='horizontal')
        separator.grid(row=row, column=0, padx=0, sticky="ew", pady=(0, 10))
        row += 1

        for i, button_details in enumerate(self.buttons):
            # Create a navigation button for each button_details in the buttons list
            button_obj = NavigationMenu.NavigationButton(self.navigation_frame, self, button_details, corner_radius=0, height=self.height, border_spacing=self.border_spacing, fg_color=self.fg_color, text_color=self.text_color)

            if i == len(self.buttons) - 1:
                pady = (0, 15)
            else:
                pady = 0

            if button_details["position"] == "bottom":
                self.navigation_frame.grid_rowconfigure(row-1, weight=1)
                button_obj.grid(row=row, column=0, sticky="sew", pady=0)

            if button_details["position"] == "top":
                button_obj.grid(row=row, column=0, sticky="new", pady=0)

            button_details["object"] = button_obj

            row += 1


    def expand(self, event=None):
        """
        Expand the navigation menu.

        Args:
            event: The event triggering the expand. Not used.
        """
        self.navigation_frame.grid(row=1, column=0, sticky="nsew", columnspan=3)
        self.navigation_label.grid(row=0, column=0, sticky="nw", padx=(self.border_spacing, 0), pady=(0, 0))

        if self.collapse_button_flag:
            try:
                self.expand_button.grid_forget()
            except Exception as e:
                pass
            self.collapse_button.grid(row=0, column=1, sticky="nsw",padx=0,pady=(4,4))

    def collapse(self, event=None):
        """
        Collapse the navigation menu.

        Args:
            event: The event triggering the collapse. Not used.
        """
        self.navigation_frame.grid_forget()
        self.navigation_label.grid_forget()

        if self.collapse_button_flag:
            try:
                self.collapse_button.grid_forget()
            except Exception as e:
                pass
            self.expand_button.grid(row=0, column=0, sticky="nw")

    def reset_buttons_text(self):
        """
        Reset the text of all buttons in the navigation menu to their initial state.
        """
        for button in self.buttons:
            button["object"].reset_text()

    def page_selected(self, selected):
        """
        Highlight the clicked button when a page is selected.

        Args:
            selected (str): The code of the selected button.
        """
        for button in self.buttons:
            if button["code"] == selected:
                button["object"].clicked_handler()

    class NavigationButton(ctk.CTkButton):
        """
        Custom navigation button class.
        """

        def __init__(self, parent, controller, button_details, corner_radius=0, height=40, border_spacing=20, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("#325882", "#14375e")):
            """
            Initialize the NavigationButton.

            Args:
                parent (tkinter.Frame): The parent frame for the button.
                controller (NavigationMenu): The NavigationMenu instance.
                button_details (dict): Dictionary containing button details.
                corner_radius (int): The corner radius for the button.
                height (int): The height of the button.
                border_spacing (int): The spacing between the button text and edges.
                fg_color (str): The foreground color for the button.
                text_color (tuple): Tuple containing normal and hover text colors.
                hover_color (tuple): Tuple containing normal and hover button colors.
            """
            self.clicked = False
            self.controller = controller
            self.button_details = button_details
            self.parent = parent
            super().__init__(parent, corner_radius=corner_radius, height=height, border_spacing=border_spacing, text=button_details["text"], fg_color=fg_color, text_color=text_color, anchor="ew", command=self.click_event)

        def clicked_handler(self):
            """
            Handle the button click event.
            """
            self.controller.reset_buttons_text()
            self.configure(text="> " + self.button_details["text"] + " <")

        def click_event(self):
            """
            Handle the click event and execute the command associated with the button.
            """
            self.button_details["command"](self.button_details["param"])

        def reset_text(self):
            """
            Reset the button text to its initial state.
            """
            self.configure(text=self.button_details["text"])
