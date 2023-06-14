from tkinter import ttk
import tkinter as tk
import datetime
import customtkinter as ctk
import copy as copymodule
class TreeView(ctk.CTkFrame):


    class TreeViewRow():

        def double_click(self):
            """
            Function to be called on double click event (event is binded to function in parent class)
            """
            if self.double_clicked_function!=None:
                self.double_clicked_function(self)

        def call_add_function(self):
            if self.add_function!=None:
                self.add_function(self,self.parent)
        
        def call_remove_function(self):
            if self.remove_function!=None:
                self.remove_function(self.iid)

        def __init__(self,treeview,linked_object,text,column_data,iid,index,tags=None,open=True,level=0,parent=None,double_clicked_function=None,add_function=None,remove_function=None):
            self.linked_object=linked_object
            self.text=text
            self.column_data=column_data
            self.iid=iid
            self.tags=tags
            self.open=open
            self.index=index
            self.level=level
            self.double_clicked_function=double_clicked_function
            self.add_function=add_function
            self.remove_function=remove_function
            self.parent=parent
            self.treeview=treeview

            self.treeview.insert(parent='', index=index, iid=self.iid,text=self.text, values=self.column_data,tags=tags,open=open)
            if self.level!=0:
                self.treeview.move(self.iid, parent.iid, self.level)

        
        
   

    def get_data(self):
        return self.data

    def copy(self,cut_flag=False):
        """
        Add the selected rows in the treeview to a memory 'clipboard'.

        Note: if a row is selected with child rows, ALL child rows will be selected too
        """

        # reset clipboard
        self.clipboard = []

        self.cut_flag=cut_flag
        self.cut_ids=[]

        selected_leaves = self.tv_obj.selection()

        for i in selected_leaves:
            # create a list with 1 element ([i]): this allows child rows to be added
            # and then dealt with in a uniform manner
            sub_leaves = [i]
            if self.has_children(i):
                # add child rows of the selected leaf
                sub_leaves = self.tv_obj.get_children(i)
                # ensure rows are not added twice
                if i not in self.cut_ids:
                    self.cut_ids.append(i)
            
            # add the selected row and child rows to the clipboard
            for sub_leaf in sub_leaves:
                self.clipboard.append(self.data[sub_leaf])
                # avoid duplicate rows
                if sub_leaf not in self.cut_ids:
                    self.cut_ids.append(sub_leaf)
    
    def cut(self):
        self.copy(cut_flag=True)
        
    def paste(self):
        """
        Paste all rows from the clipboard under a selected parent
        """

        # find the paste location. One of two options:
        # - under a selected parent
        # - under the parent of a selected child (i.e. next to a selected child)
        selected_leaf = self.tv_obj.selection()[0]
        if self.data[selected_leaf].level>0:
            selected_parent_leaf=self.data[selected_leaf].parent.iid
        else: selected_parent_leaf=selected_leaf

        pasted_ids = []
        # loop through memory of copied/cut items, inserting them into the desired location
        for row_obj in self.clipboard:
            new_row = self.insert_element(linked_object=row_obj.linked_object,column_data=row_obj.column_data,text=row_obj.text,childobject_level=row_obj.level,childobject_parent=self.data[selected_parent_leaf], add_function=row_obj.add_function,remove_function=row_obj.remove_function,double_clicked_function=row_obj.double_clicked_function)
            pasted_ids.append(new_row.iid)
            self.data[new_row.iid].call_add_function()

        self.tv_obj.selection_set(pasted_ids)

        # delete all copied items if they were copied using the cut functionaliy
        if self.cut_flag==True:
            self.remove_treeview_row(self.cut_ids)
            self.cut_flag=False
            self.cut_ids=[]
            self.clipboard=[]

    def double_click(self,event, double_click_function):
        # retrieving the id from the selected treeview row
        clicked_element_id = self.tv_obj.identify('item',event.x,event.y)
        # activate double click method for the selected treeview row
        self.data[clicked_element_id].double_click()


### INOPERATIVE SORTING ALGORITHM
    def convert_treeview_set(self,array_of_sets, type1):
        
        for i,set_item in enumerate(array_of_sets):
            tuple_as_a_list = list(set_item)

            if type1 == "name_str":
                array_of_sets[i]=tuple([self.data[tuple_as_a_list[1]]["linked_object"].get_name(),int(tuple_as_a_list[1])])
        
            if type1 == "printed_bool":
                array_of_sets[i]=tuple([self.data[tuple_as_a_list[1]]["linked_object"].get_printed(),int(tuple_as_a_list[1])])
        
            if type1 == "completed_bool":
                array_of_sets[i]=tuple([self.data[tuple_as_a_list[1]]["linked_object"].get_completed(),int(tuple_as_a_list[1])])
        
            if type1 == "completed_date":
                array_of_sets[i]=tuple([self.data[tuple_as_a_list[1]]["linked_object"].get_completed_date_datetime(),int(tuple_as_a_list[1])])
        
            if type1 == "mark_percentage":
                array_of_sets[i]=tuple([self.data[tuple_as_a_list[1]]["linked_object"].get_percentage(),int(tuple_as_a_list[1])])
            if type1 == "grade_int":
                array_of_sets[i]=tuple([self.data[tuple_as_a_list[1]]["linked_object"].get_grade(),int(tuple_as_a_list[1])])

            if type1 == "notes_str":
                array_of_sets[i]=tuple([self.data[tuple_as_a_list[1]]["linked_object"].get_notes().strip(),int(tuple_as_a_list[1])])
        
        
            if type1 == "year_int":
                array_of_sets[i]=tuple([self.data[tuple_as_a_list[1]]["linked_object"].get_year(),int(tuple_as_a_list[1])])
        
        return array_of_sets
    def reset_column_headings(self):
        for i, column_code in enumerate(self.columns):
            self.tv_obj.heading(column_code, text=self.columns[column_code][0])
    def treeview_sort_column(self,tv, col, columns, reverse):
    
        def remove_none(self,x):
            """
            
            """
            
            missing = x[0] is None

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

        # each time the treeview is refreshed, the same 
        self.sort_memory = [{"Name":col,"Reverse":reverse}]
        
        self.reset_column_headings()
        
        
        #type_of_datatype = columns[col][1]
        index = columns[col][0]
        
        
        
        l = [(tv.set(k, index), k) for k in tv.get_children('')]

        #l = self.convert_treeview_set(l,type_of_datatype)

        print(l)

        l.sort(reverse=reverse)

        """

        if type_of_datatype[-10:] == "percentage":
            if reverse:
                l.sort(reverse=reverse)
            else:
                l.sort(reverse=reverse,key=self.remove_zero_percentage)
       
        elif type_of_datatype[-3:] == "str":
            if reverse:
                l.sort(reverse=reverse)
            else:
                l.sort(reverse=reverse,key=self.remove_empty_string)
        
        elif type_of_datatype[-4:] == "date":
            if reverse:
                l.sort(reverse=reverse,key=self.remove_none_by_resetting_datetime)
            else:

                l.sort(reverse=reverse,key=self.remove_none)
        else:
            l.sort(reverse=reverse)
        """
        # rearrange items in sorted positions
        for index1, (val, k) in enumerate(l):
            tv.move(k, '', index1)
            tv.item(k,tags=str(index1%2))

        # reverse sort next time
        if reverse: sorted_text = "∨"
        else: sorted_text="∧"
        tv.heading(index, text=col + " (" + sorted_text + ")", command=lambda _col=col: self.treeview_sort_column(tv, _col, columns, not reverse))    
    def pre_sort(self):
        """
        Re-apply the most recent sort that was applied to the treeview (this is required when the treeview is refreshed).
        This ensures the existing sort is not broken, even when new rows are added or rows are removed.
        """
        if len(self.sort_memory) != 0:
            self.tv_obj.treeview_sort_column(self.tv_obj, self.sort_memory[-1]["Name"], self.columns, self.sort_memory[-1]["Reverse"])





    def apply_width_state(self,reduced_size=False):
        """
        The treeview has two width states passed as the reduced_size parameter (default False):
        - reduced_size == False: the first width state is applied 
        - reduced_size == True: the second width state is applied

        Usually, when reduced_size == True (i.e. the treeview is displayed on a smaller frame), certain
        columns should not be shown (this is done by passing a 0 as the column width for a particular column
        in the constructor - see constructor method for more information)  
        """

        display_columns=[]
        for column_code in self.columns:
            # if the secondary width value is greater than 0 (e.g. 0.2 / 20%, add the column to an array of columns t)
            if self.columns[column_code][2] > 0 and reduced_size:
                display_columns.append(column_code)
            # show all columns if not reduced_size
            elif not reduced_size:
                display_columns.append(column_code)
        # display only the colluns appended to the list in the prior for loop
        self.tv_obj["displaycolumns"]=display_columns
        # save reduced_size to memory (this is used in edit_treeview_width)
        self.reduced_size=reduced_size
       
    def edit_treeview_width(self,event=None):
        """
        Modify the width of columns in the treeview according to the weightings given in the columns variable in the
        constructor.
        """
        
        # weightings will be applied to the frame width (thus ensuring a fair distribution of column widths over available pixels)
        width=self.master_frame.winfo_width()

        # two weighting are given in the constructor depending on the reduced_size variable (see apply_width_state() method for more information)
        if self.reduced_size==True: width_index=2
        else: width_index=1

        
        self.tv_obj.grid_forget()
        for column_code in self.columns:
            # apply a width offset (i.e. less pixels will be used to give padding - extra padding is required if there
            # are editing buttons)
            if self.show_editing_buttons: width_offset=200
            else:width_offset=70
            self.tv_obj.column(column_code,width=int(self.columns[column_code][width_index]*(width-width_offset)))
        self.tv_obj.grid(row=1,column=0,sticky="new",rowspan=10)


    def select_all(self):
        """
        Select all rows in the treeview
        """
        self.tv_obj.selection_set(list(self.data.keys()))

    
    def keypress(self,event):
        """
        Handle keyboard shortcuts for copying (CTRL+c), cutting (CTRL+x), pasting (CTRL+v), deleting (Del key), 
        search finding (CTRL+f) and select all (CTRL+a)
        """

        # the nested events are only bound if the respective editing buttons are displayed
        if self.show_editing_buttons:
            # copy
            if event.state==4 and event.keysym == "c":
                self.copy()
            # cut
            if event.state==4 and event.keysym == "x":
                self.cut()
            # paste
            if event.state==4 and event.keysym == "v":
                self.paste()
            # delete
            if event.state==262144 and event.keysym == "Delete":
                self.remove_treeview_row()
            # find (search)
            if event.state==4 and event.keysym == "f":
                self.control_f_pressed()
        
        # select all (always bound)
        if event.state==4 and event.keysym == "a":
            self.select_all()


    def invert_selected(self):
        # TODO REMOVE

        for iid in self.data:
            
            if self.data[iid].level>0==True:
                self.tv_obj.selection_toggle(iid)
            else:
                self.tv_obj.selection_remove(iid)

        




    def control_f_pressed(self):
        self.searchentry.focus()
        self.searchentry.select_range(0,tk.END)

    def insert_element(self, linked_object, column_data, text="", iid=None, message=[],childobject=False,childobject_parent=None,childobject_level=0,double_clicked_function=None,add_function=None,remove_function=None):
        """
        Will insert an element into the treeview
        IN:
        - linked_object: an object to be linked to the row in the treeview (will be returned on the double click)
        - values: a LIST of values to populate each column in the new treeview row
        - evenoddcounter: a counter pertraining to the elements currently being added to the treeview
        """

        self.counter += 1

        iid_new=None
        if iid != None and iid != "":
            iid_new = iid
        else:
            iid_new = self.counter



        new_treeview_row=self.TreeViewRow(self.tv_obj,linked_object=linked_object,index=self.counter,text=text,column_data=column_data,iid=iid_new,tags=str(self.counter % 2),open=True,level=childobject_level,parent=childobject_parent,add_function=add_function,remove_function=remove_function,double_clicked_function=double_clicked_function)
        self.data[str(iid_new)]=new_treeview_row

        return new_treeview_row

    def reset_selections(self):
        for item in self.tv_obj.selection():
            self.tv_obj.selection_remove(item)

    def exists_valid_check(self,iid):
        if not self.tv_obj.exists(iid):
            del self.data[iid]
            return False
        return True

    def select_empty(self):
        """
        Select all empty parent nodes on the treeview (rows that have no child nodes)
        """

        self.reset_selections()

        nodes_to_add = []
        

        for iid in self.data:
            if self.data[iid]["childobject"]==False:
                # if the parent node has no child nodes, add it to the array
                if not self.has_children(iid):
                    nodes_to_add.append(iid)
        
        # select in the treeview the array of nodes
        self.tv_obj.selection_add(nodes_to_add)
        # make sure a selected row is shown on the treeview
        self.tv_obj.see(iid) 

    def searched_text_update(self,amount):
        self.searched_text.configure(text="Found:" + str(amount))
    
    def select_search(self,search):
        """
        Search the treeview using a search prompt from the search box
        """
        self.reset_selections()
        nodes_to_add = []
        keys=self.data.keys()
        for iid in keys:
            # the search string must be matched inside of the the contents of the data element
            search_string = "".join(self.data[iid]["contents"]) + self.data[iid]["tree_column_text"]
            if search.lower() in search_string.lower() and self.data[iid]["childobject"]:
                nodes_to_add.append(iid)
                
                if self.exists_valid_check(iid):
                    self.tv_obj.selection_add(iid)
        # make sure the current row is shown
        self.tv_obj.see(nodes_to_add[0]) 
        # set focus on the treeview (take focus away from the search entry box)
        self.tv_obj.focus_set()
        # show the search results on a label
        self.searched_text_update(len(nodes_to_add))

    def oddevenconfigure(self,color_odd,color_even):
        """
        Set the alternating colours of the treeview
        """
        self.tv_obj.tag_configure('1', background=color_odd)
        self.tv_obj.tag_configure('0', background=color_even)

    def remove_all(self):
        """
        Remove all rows from the treeview
        """
        for item in self.data:
            if not self.data[item]["childobject"]:
                if self.tv_obj.exists(item):
                    self.tv_obj.delete(item)
        self.data={}

    def has_children(self,iid):
        if len(self.tv_obj.get_children(iid)) > 0:
            return True
        else:
            return False
    
    def remove_treeview_row(self,iids=None):
        """
        Remove selected rows from the treeview

        IN:
        - iids (=None): override iids to be removed from the treeview. Default setting will read selected rows from the treeview
        """
        if iids==None:iids=self.tv_obj.selection()
        # remove all iids selected from the treeview
        for iid in iids:

            if self.tv_obj.exists(iid):
                # remove row from the treeview
                self.tv_obj.delete(iid)



            # call on a given function to execute the delete method
            self.data[iid].call_remove_function()



    def __init__(self, master_frame, columns, double_click_function=None, show_editing_buttons=False,height=25,padx=25,pady=25,show_tree=False,show_tree_heading="",show_tree_width=0) -> None:
        """
        Create and manage a ctk.CTkTreeview object.
        
        IN:
        - master_frame (ttk.Frame): the master frame on which the treeview is placed
        - columns: list of lists defining columns placed on the treeview in the following format: [[heading text (str),heading code (str), width (wide display) (float 0-1), width (narrow display) (float 0-1)]], ...]
        - OPTIONAL double_click_function (any function): the function that will be called when a row on the treeview is double clicked
        - OPTIONAL show_editing_buttons (bool): show the following buttons which can be used to manipulate the treeview: Search, Invert Selected, Copy Selected, Paste, Cut, Remove, Select empty items
        - OPTIONAL show_tree (bool, default False): show the expand/collapse column (the 'tree')
        - OPTIONAL show_tree_heading (str, default None): the heading of the tree column
        - OPTIONAL show_tree_width (float 0-1,default 0): the proportional width as a decimal of the tree column
        OUT:
        - on double click of a row on the treeview, the double_click_function (optional parameter) will be called. This function will return the OBJECT of the clicked row: defined during individual row creation - see insert_element()
        """

        self.master_frame=master_frame

        
        super().__init__(self.master_frame,fg_color="transparent")
        self.columnconfigure(0,weight=1)

        
        if show_tree==True:
            show_tree_text="tree headings"
        else:
            show_tree_text="headings"

        self.reduced_size=False

        # used during user modification of treeview
        self.cut_flag=False
        
        # create the treeview using the given columns data
        list_of_columns=[]
        for column_code in columns:
            list_of_columns.append(column_code)
        self.tv_obj = ttk.Treeview(self, columns=list_of_columns, show=show_tree_text, height=height)
        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 10))
        style.configure("Treeview", font=(None, 9))
        

        self.data = {}
        self.link_iids = {}
        self.counter = 0
        self.columns = columns

        self.show_editing_buttons=show_editing_buttons

        row = 2
        col = 2
        pady=4
        padx=(4,0)
        sticky="nw"

        # setup keyboard shortcuts binding
        self.tv_obj.bind('<KeyPress>', self.keypress)

        # create and place all editing buttons onto the grid (if show_editing_buttons is passed as True in the constructor)
        if self.show_editing_buttons:
            
            # create search input
            self.search_frame = ctk.CTkFrame(self,fg_color="transparent")
            self.search_frame.grid(row=row,column=col,columnspan=1,sticky=sticky,padx=padx,pady=(0,pady))
            self.searchentry = ctk.CTkEntry(self.search_frame,placeholder_text="Search items")
            self.searchentry.grid(row=0,column=0)
            self.searchentry.bind("<Return>",lambda e:self.select_search(self.searchentry.get()))
            self.find_button = ctk.CTkButton(self.search_frame,text="Search",command=lambda:self.select_search(self.searchentry.get()))
            self.find_button.grid(row=1,column=0)
            self.searched_text = ctk.CTkLabel(self.search_frame,text="",fg_color="transparent")
            self.searched_text.grid(row=row,column=0,sticky="nw")
            
            #row += 1

            #self.invert_button = ctk.CTkButton(self.search_frame,text="Invert selected",command=lambda:self.invert_selected())
            #self.invert_button.grid(row=row,column=0,padx=padx,pady=pady,sticky=sticky)

            # copy
            self.copy_button = ctk.CTkButton(self,text="Copy selected",command=self.copy)
            self.copy_button.grid(row=row,column=col,padx=padx,pady=pady,sticky=sticky)
            row += 1

            # paste
            self.paste_button = ctk.CTkButton(self,text="Paste",command=self.paste)
            self.paste_button.grid(row=row,column=col,padx=padx,pady=pady,sticky=sticky)
            row += 1

            # cut
            self.cut_button = ctk.CTkButton(self,text="Cut selected",command=self.cut)
            self.cut_button.grid(row=row,column=col,padx=padx,pady=pady,sticky=sticky)
            row += 1
            
            # delete
            self.delete_button = ctk.CTkButton(self,text="Remove selected",command=self.remove_treeview_row)
            self.delete_button.grid(row=row,column=col,padx=padx,pady=pady,sticky=sticky)
            row += 1

            # select empty parents
            self.select_empty_button = ctk.CTkButton(self,text="Select empty items",command=self.select_empty)
            self.select_empty_button.grid(row=row,column=col,padx=padx,pady=pady,sticky=sticky)

        # show the expand/collapse button column (the 'tree') if requested
        if show_tree: 
            self.tv_obj.heading('#0',text=show_tree_heading)
            self.tv_obj.column('#0',width=int(show_tree_width*650*2))


        for column_code in self.columns:
            self.tv_obj.heading(column_code,text=self.columns[column_code][0],command=lambda _col=self.columns[column_code][0]: self.treeview_sort_column(self.tv_obj, _col, self.columns, False))
            self.tv_obj.column(column_code, width=int(self.columns[column_code][1]*650*2)) 

        # bind double click
        self.tv_obj.bind("<Double-1>", lambda e: self.double_click(e, double_click_function))
        self.master_frame.bind("<Configure>",self.edit_treeview_width)

        # Adding a vertical scrollbar to Treeview widget
        treeScroll = ttk.Scrollbar(self)
        treeScroll.configure(command=self.tv_obj.yview)
        self.tv_obj.configure(yscrollcommand=treeScroll.set)
        treeScroll.grid(row=1,column=1,sticky="nse",pady=1,rowspan=10)


        self.tv_obj.grid(row=1,column=0,sticky="new",rowspan=10)
        self.sort_memory = []
        self.edit_treeview_width()

