from tkinter import ttk
import tkinter as tk
import datetime
class TreeView(ttk.Treeview):

    def double_click(self,event, double_click_function):
        # retrieving the id from the treeview row
        clicked_element_id = self.identify('item',event.x,event.y)
        
        clicked_object = self.link_iids[clicked_element_id]

        if double_click_function != None:
            double_click_function(clicked_object)

    def get_object(self,id):
        return self.link_iids[id]

    def convert_treeview_set(self,array_of_sets, type1):
        
        for i,set_item in enumerate(array_of_sets):
            tuple_as_a_list = list(set_item)

            #print(self.link_iids[tuple_as_a_list[1]].get_completed_date())

            if type1 == "name_str":
                array_of_sets[i]=tuple([self.link_iids[tuple_as_a_list[1]].get_name(),int(tuple_as_a_list[1])])
        
            if type1 == "printed_bool":
                array_of_sets[i]=tuple([self.link_iids[tuple_as_a_list[1]].get_printed(),int(tuple_as_a_list[1])])
        
            if type1 == "completed_bool":
                array_of_sets[i]=tuple([self.link_iids[tuple_as_a_list[1]].get_completed(),int(tuple_as_a_list[1])])
        
            if type1 == "completed_date":
                array_of_sets[i]=tuple([self.link_iids[tuple_as_a_list[1]].get_completed_date_datetime(),int(tuple_as_a_list[1])])
        
            if type1 == "mark_percentage":
                array_of_sets[i]=tuple([self.link_iids[tuple_as_a_list[1]].get_percentage(),int(tuple_as_a_list[1])])
        
            if type1 == "grade_int":
                array_of_sets[i]=tuple([self.link_iids[tuple_as_a_list[1]].get_grade(),int(tuple_as_a_list[1])])

            if type1 == "notes_str":
                array_of_sets[i]=tuple([self.link_iids[tuple_as_a_list[1]].get_notes().strip(),int(tuple_as_a_list[1])])
        
        
            if type1 == "year_int":
                array_of_sets[i]=tuple([self.link_iids[tuple_as_a_list[1]].get_year(),int(tuple_as_a_list[1])])
        
        return array_of_sets
    
    def remove_none(self,x):
        
        missing = x[0] is None
        #print(x[0],missing)
        #print((missing, x if not missing else datetime.datetime(9999, 12, 31)))
        return (missing, x if not missing else datetime.datetime(9999, 12, 31))
    
    def remove_none_by_resetting_datetime(self,x):
        
        missing = x[0] is None
        return x[0] if not missing else datetime.datetime(1, 1, 1)

    def remove_zero_percentage(self,x):
        missing = x[0] == 0
        return x[0] if not missing else 999

    def remove_empty_string(self,x):
        missing = x[0] == ""
        return (missing,x[0] if not missing else 999)

    def reset_treeview_headings(self):
        for i, heading in enumerate(self.headings):
            self.heading(i+1, text=heading[0])


    def treeview_sort_column(self,tv, col, columns, reverse):
        self.pre_filter_stored = [{"Name":col,"Reverse":reverse}]
        self.reset_treeview_headings()
        type_of_datatype = columns[col][1]
        index = columns[col][0]
        l = [(tv.set(k, index), k) for k in tv.get_children('')]
        #print(tv.set(k, index))
        #print(l)
        #self.paper_tv = treeview.TreeView(self,[["Name","name_str"],["Printed","printed_bool"],["Completed","completed_bool"],["Completed Date","completed_date"],["Mark","mark_percentage"],["Grade","grade_int"],["Notes","notes_str"]],row=1,column=0,columnspan=5,double_click_function=self.tree_double_clicked,height=20)

        l = self.convert_treeview_set(l,type_of_datatype)
        #print(l)

        #if type_of_datatype == "date":

        if type_of_datatype == "mark_percentage" or type_of_datatype == "grade_int":
            if reverse:
                l.sort(reverse=reverse)
            else:
                l.sort(reverse=reverse,key=self.remove_zero_percentage)
       
        elif type_of_datatype == "notes_str":
            if reverse:
                l.sort(reverse=reverse)
            else:
                l.sort(reverse=reverse,key=self.remove_empty_string)
        
        elif type_of_datatype == "completed_date":
            if reverse:
                #print("completed reverse")
                l.sort(reverse=reverse,key=self.remove_none_by_resetting_datetime)
            else:

                l.sort(reverse=reverse,key=self.remove_none)
        else:
            #print("ELSE")
            l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index1, (val, k) in enumerate(l):
            tv.move(k, '', index1)

        # reverse sort next time
        if reverse: sorted_text = "descending"
        else: sorted_text="ascending"
        tv.heading(index, text=col + " (" + sorted_text + ")", command=lambda _col=col: self.treeview_sort_column(tv, _col, columns, not reverse))


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
        self.headings = headings

        #for i,heading in enumerate(headings):
        #    self.heading(i+1,text=heading)
        self.columns = {}
        for i,column_and_type in enumerate(headings):
            self.columns[column_and_type[0]]=[i+1,column_and_type[1]]
            self.heading(i+1,text=column_and_type[0],command=lambda _col=column_and_type[0]: self.treeview_sort_column(self, _col, self.columns, False))


            if len(column_and_type)==3:
                self.column(i+1, minwidth=100, width=column_and_type[2], stretch=tk.YES) 
            else:
                self.column(i+1, minwidth=100, width=150, stretch=tk.YES) 



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
        self.pre_filter_stored = []

    def pre_filter(self):
        if len(self.pre_filter_stored) != 0:
            self.treeview_sort_column(self, self.pre_filter_stored[-1]["Name"], self.columns, self.pre_filter_stored[-1]["Reverse"])


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
