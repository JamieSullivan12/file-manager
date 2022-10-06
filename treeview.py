from tkinter import ttk
import tkinter as tk

class TreeView(ttk.Treeview):

    def double_click(self,event, double_click_function):
        # retrieving the id from the treeview row
        clicked_element_id = self.identify('item',event.x,event.y)
        
        clicked_object = self.link_iids[clicked_element_id]

        if double_click_function != None:
            double_click_function(clicked_object)

    def get_object(self,id):
        return self.link_iids[id]

    def __init__(self, frame, headings, row, column, columnspan=1, double_click_function=None, linked_object=None, height=25) -> None:
        """
        FUNCTION create a treeview object, using the following inputs:
        IN:
        - frame (ttk.Frame): the frame on which the treeview will be placed
        - headings (list[str]): the headings of the treeview
        - OPTIONAL double_click_function (any function): the function that will be called when one clicks on a treeview element
        - OPTIONAL linked_object (any object): an object that will be returned on a double click
        - OPTIONAL height (int): the number of rows the treeview will span for
        

        OUT:
        - on double click of a row on the treeview, the double_click_function (optional parameter) will be called. This function will return the OBJECT of the clicked row: defined during individual row creation - see insert_element()
        """

        super().__init__(frame, columns=list(range(1,len(headings)+1)), show="headings", height=height)


        self.link_iids = {}
        self.counter = 0

        for i,heading in enumerate(headings):
            self.heading(i+1,text=heading)

        self.bind("<Double-1>", lambda e: self.double_click(e, double_click_function))

        # Adding a vertical scrollbar to Treeview widget
        treeScroll = ttk.Scrollbar(frame)
        treeScroll.configure(command=self.yview)
        self.configure(yscrollcommand=treeScroll.set)
        treeScroll.grid(row=row,column=column + columnspan,sticky="ns")

        # Adding a vertical scrollbar to Treeview widget
        treexScroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        treexScroll.configure(command=self.xview)
        self.configure(xscrollcommand=treexScroll.set)
        treexScroll.grid(row=row+1,column=column,columnspan=3,sticky="ew")
        #   self.selection_get
        self.grid(row=row,column=column,columnspan=columnspan)

    def insert_element(self, linked_object, values):
        """
        Will insert an element into the treeview
        IN:
        - linked_object: an object to be linked to the row in the treeview (will be returned on the double click)
        - values: a LIST of values to populate each column in the new treeview row
        """
        


        self.insert(parent='', index=self.counter, iid=linked_object.db_index, values=values)

        self.link_iids[str(linked_object.db_index)] = linked_object

        self.counter = self.counter + 1

    def remove_all(self):
        for item in self.get_children():
            self.delete(item)
