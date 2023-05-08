from tkinter import ttk
import tkinter as tk
import datetime
import customtkinter as ctk
class TreeView(ctk.CTkFrame):

    def get_data(self):

        return self.data

    def copy(self,cut_flag=False):
        self.clipboard = []
        leaves = self.tv_obj.selection()

        self.cut_flag=cut_flag

        self.cut_ids=[]
        for i in leaves:

            sub_leaves = [i]
            if self.has_children(i):
                sub_leaves = self.tv_obj.get_children(i)
                self.cut_ids.append(i)
            for sub_leaf in sub_leaves:
                self.clipboard.append(self.data[sub_leaf])
                self.cut_ids.append(sub_leaf)

    def cut(self):
        self.copy(cut_flag=True)
        


    def paste(self):
        selected_leaf = self.tv_obj.selection()[0]
        
        if self.tv_obj.parent(selected_leaf)!="":
            selected_leaf=self.tv_obj.parent(selected_leaf)
        pasted_ids = []
        for i in self.clipboard:
            new_id = self.insert_element(self.data[selected_leaf]["linked_object"],i["contents"],text=i["tree_column_text"],message=i["message"],childobject=i["childobject"],childobject_level=i["childobject_level"],childobject_parent_id=selected_leaf)
            pasted_ids.append(new_id)
            self.child_add_action(parent=self.data[selected_leaf],child=self.data[new_id])

        self.tv_obj.selection_set(pasted_ids)

        if self.cut_flag==True:
            
            self.remove_treeview_row(self.cut_ids)
            self.cut_flag=False
            self.cut_ids=[]
            self.clipboard=[]

    def moveUp(self):
        leaves = self.tv_obj.selection()
        for i in leaves:
            self.tv_obj.move(i, self.tv_obj.parent(i), self.index(i)-1)

    def double_click(self,event, double_click_function):
        # retrieving the id from the treeview row
        clicked_element_id = self.tv_obj.identify('item',event.x,event.y)
        
        clicked_item_data = self.data[clicked_element_id]
        #clicked_object = clicked_item_data["linked_object"]

        if double_click_function != None:
            double_click_function(clicked_item_data)

    def get_object(self,id):
        return self.data[id]["linked_object"]

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
        for i, heading in enumerate(self.tv_obj.headings):
            self.tv_obj.heading(i+1, text=heading[0])


    def treeview_sort_column(self,tv, col, columns, reverse):
        self.pre_filter_stored = [{"Name":col,"Reverse":reverse}]
        self.reset_treeview_headings()
        type_of_datatype = columns[col][1]
        index = columns[col][0]
        l = [(tv.set(k, index), k) for k in tv.get_children('')]

        l = self.convert_treeview_set(l,type_of_datatype)

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
            tv.item(k,tags=str(index1%2))

        # reverse sort next time
        if reverse: sorted_text = "∨"
        else: sorted_text="∧"
        tv.heading(index, text=col + " (" + sorted_text + ")", command=lambda _col=col: self.treeview_sort_column(tv, _col, columns, not reverse))



    def edit_treeview_width(self,width):
        self.tv_obj.grid_forget()
        for i,column_and_type in enumerate(self.columns):
            if self.show_editing_buttons: width_offset=200
            else:width_offset=70
            self.tv_obj.column(i+1,width=int(self.columns[column_and_type][2]*(width-width_offset)))
            
        self.tv_obj.grid(row=1,column=0,sticky="new",rowspan=10)

    def keypress(self,event):
        if self.show_editing_buttons:
            if event.state==4 and event.keysym == "c":
                self.copy()
            if event.state==4 and event.keysym == "x":
                self.cut()
            if event.state==4 and event.keysym == "v":
                self.paste()
            if event.state==262144 and event.keysym == "Delete":
                self.remove_treeview_row()

            if event.state==4 and event.keysym == "f":
                self.control_f_pressed()
        if event.state==4 and event.keysym == "a":
            self.select_all()



    def select_all(self):
        self.tv_obj.selection_set(list(self.data.keys()))


    def __init__(self, mainline_obj,frame, headings, row, column, columnspan=1, alternating_colors=None, double_click_function=None, linked_object=None, height=25,padx=25,pady=25,show_tree=False,show_tree_heading="",show_tree_width=0,show_editing_buttons=False,child_remove_action=None,child_add_action=None) -> None:
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
        
        if show_tree==True:
            show_tree_text="tree headings"
        else:
            show_tree_text="headings"

        self.mainline_obj=mainline_obj

        super().__init__(frame,fg_color="transparent")
        self.columnconfigure(0,weight=1)
        self.grid(row=row,column=column,padx=padx,pady=pady,sticky="new")

        self.tv_obj = ttk.Treeview(self, columns=list(range(1,len(headings)+1)), show=show_tree_text, height=height)
        self.child_remove_action=child_remove_action
        self.child_add_action=child_add_action

        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 12))
        style.configure("Treeview", font=(None, 9))
        

        self.data = {}
        self.link_iids = {}
        self.counter = 0
        self.headings = headings
        self.alternating_colors = alternating_colors
        self.alternate_colors = alternating_colors != None

        self.row=row
        self.col=column
        self.padx=padx
        self.pady=pady

        self.cut_flag=False

        self.show_editing_buttons=show_editing_buttons

        #self.up_button = ctk.CTkButton(self,text="up",command=self.moveUp)
        #self.up_button.grid(row=2,column=0)

        row = 1
        col = 2
        pady=4
        padx=(4,0)
        sticky="nw"


        self.tv_obj.bind('<KeyPress>', self.keypress)

        if self.show_editing_buttons:
            
            self.search_frame = ctk.CTkFrame(self,fg_color="transparent")
            self.search_frame.grid(row=row,column=col,columnspan=1,sticky=sticky,padx=padx,pady=(0,pady))

            self.searchentry = ctk.CTkEntry(self.search_frame,placeholder_text="Search items")
            self.searchentry.grid(row=0,column=0)
            self.searchentry.bind("<Return>",lambda e:self.select_search(self.searchentry.get()))

            self.find_button = ctk.CTkButton(self.search_frame,text="Search",command=lambda:self.select_search(self.searchentry.get()))
            self.find_button.grid(row=1,column=0)

            self.searched_text = ctk.CTkLabel(self.search_frame,text="",fg_color="transparent")
            self.searched_text.grid(row=2,column=0,sticky="nw")

            row += 1


            self.copy_button = ctk.CTkButton(self,text="Copy selected",command=self.copy)
            self.copy_button.grid(row=row,column=col,padx=padx,pady=pady,sticky=sticky)

            row += 1



            self.paste_button = ctk.CTkButton(self,text="Paste",command=self.paste)
            self.paste_button.grid(row=row,column=col,padx=padx,pady=pady,sticky=sticky)
            
            row += 1


            self.cut_button = ctk.CTkButton(self,text="Cut selected",command=self.cut)
            self.cut_button.grid(row=row,column=col,padx=padx,pady=pady,sticky=sticky)
            row += 1

            self.delete_button = ctk.CTkButton(self,text="Remove selected",command=self.remove_treeview_row)
            self.delete_button.grid(row=row,column=col,padx=padx,pady=pady,sticky=sticky)

            row += 1

            self.select_empty_button = ctk.CTkButton(self,text="Select empty items",command=self.select_empty)
            self.select_empty_button.grid(row=row,column=col,padx=padx,pady=pady,sticky=sticky)


            #searchentry_tracker = tk.StringVar()
            #searchentry_tracker.trace("w", lambda name, index, mode, sv=searchentry_tracker: self.entry_filter_callback(searchentry_tracker, type))
        



        if show_tree: 
            self.tv_obj.heading('#0',text=show_tree_heading)
            self.tv_obj.column('#0',width=int(show_tree_width*650*2))


        self.columns = {}
        
        self.treeview_counter = 0

        i = 1
        for column_and_type in headings:
            self.columns[column_and_type[0]]=[i,column_and_type[1],column_and_type[2]]
            self.tv_obj.heading(i,text=column_and_type[0],command=lambda _col=column_and_type[0]: self.treeview_sort_column(self, _col, self.columns, False))


            if len(column_and_type)==3:
                self.tv_obj.column(i, width=int(column_and_type[2]*650*2)) 
            else:
                pass
            i += 1



        self.tv_obj.bind("<Double-1>", lambda e: self.double_click(e, double_click_function))


        # Adding a vertical scrollbar to Treeview widget
        treeScroll = ttk.Scrollbar(self)
        treeScroll.configure(command=self.tv_obj.yview)
        self.tv_obj.configure(yscrollcommand=treeScroll.set)
        treeScroll.grid(row=1,column=1,sticky="nse",pady=1,rowspan=10)

        self.tv_obj.grid(row=1,column=0,sticky="new",rowspan=10)
        self.pre_filter_stored = []

    def pre_filter(self):
        if len(self.pre_filter_stored) != 0:
            self.tv_obj.treeview_sort_column(self, self.pre_filter_stored[-1]["Name"], self.columns, self.pre_filter_stored[-1]["Reverse"])

    def control_f_pressed(self):
        self.searchentry.focus()
        self.searchentry.select_range(0,tk.END)

    def insert_element(self, linked_object, contents, text="", iid=None, message=[],childobject=False,childobject_parent_id=None,childobject_level=0):
        """
        Will insert an element into the treeview
        IN:
        - linked_object: an object to be linked to the row in the treeview (will be returned on the double click)
        - values: a LIST of values to populate each column in the new treeview row
        - evenoddcounter: a counter pertraining to the elements currently being added to the treeview
        """

        self.counter += 1

        iid_new=None
        if iid != None:
            iid_new = iid
        else:
            iid_new = self.counter


        self.data[str(iid_new)]={
            "linked_object":linked_object,
            "contents":contents,
            "tree_column_text":text,
            "message":message,
            "childobject":childobject,
            "childobject_parent_id":childobject_parent_id,
            "childobject_level":childobject_level
        }
            
        self.tv_obj.insert(parent='', index=self.counter, iid=iid_new,text=text, values=contents,tags=str(self.counter % 2),open=True)

        if childobject:
            self.tv_obj.move(iid_new, childobject_parent_id, childobject_level)

        return str(iid_new)

    def reset_selections(self):
        for item in self.tv_obj.selection():
            self.tv_obj.selection_remove(item)


    def select_empty(self):
        self.reset_selections()
        to_add = []
        
        for iid in self.data:
            if self.data[iid]["childobject"]==False:
                if not self.has_children(iid):
                    to_add.append(iid)
        self.tv_obj.selection_add(to_add[0])
        self.tv_obj.see(iid) # make sure the current row is shown - from /10155153/

    def searched_text_update(self,amount):
        self.searched_text.configure(text="Found:" + str(amount))
    
    def select_search(self,search):
        self.reset_selections()
        to_add = []
        
        for iid in self.data:
            search_string = "".join(self.data[iid]["contents"]) + self.data[iid]["tree_column_text"]
            if search.lower() in search_string.lower():
                to_add.append(iid)

        self.tv_obj.selection_add(to_add)
        self.tv_obj.see(to_add[0]) # make sure the current row is shown - from /10155153/

        self.tv_obj.focus_set()

        self.searched_text_update(len(to_add))

    def oddevenconfigure(self,color_odd,color_even):
        """
        Set the alternating colours of the treeview
        """
        self.tv_obj.tag_configure('1', background=color_odd)
        self.tv_obj.tag_configure('0', background=color_even)

    def remove_all(self):
        for item in self.tv_obj.get_children():
            self.tv_obj.delete(item)
    def has_children(self,iid):
        if len(self.tv_obj.get_children(iid)) > 0:
            return True
        else:
            return False
    def remove_treeview_row(self,iids=None):


        parent_iids = []
        if iids==None:iids=self.tv_obj.selection()
        for iid in iids:
            if self.has_children(iid): parent_iids.append(iid)
            else:
                self.tv_obj.delete(iid)
                self.child_remove_action(child=self.data[iid])
                self.data.pop(iid)
        for iid in parent_iids:
            self.tv_obj.delete(iid)
            self.data.pop(iid)

            


