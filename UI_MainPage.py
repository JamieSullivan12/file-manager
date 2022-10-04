import tkinter as tk
from tkinter import ttk
import treeview, UI_Popup_Edit_Row, bulk_load
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scrollable_frame
class MainPage(ttk.Frame):

    class CreateNewPopup(tk.Toplevel):
        def __init__(self,parent,mainline_obj,clicked_object,type):
            super().__init__(parent.mainline_obj.parent)
            self.geometry("1100x900")
            self.title("PDF Viewer")
            self.grid_rowconfigure(0,weight=1)
            self.grid_columnconfigure(0,weight=1)
            self.scrollable_frame = scrollable_frame.ScrollableFrame(self)
            self.scrollable_frame.update()
            UI_Popup_Edit_Row.UIPopupEditRow(parent,self.scrollable_frame,mainline_obj,clicked_object,type)

            

    def tree_double_clicked(self,clicked_object):
        self.CreateNewPopup(self,self.mainline_obj,clicked_object, type="update")
        


    def bulk_load(self,event=None):
        bulk_load.get_past_papers(self.mainline_obj)

    def load(self,event=None):
        """
        Add a past paper to the database
        """
        
        new_paper_object = self.db_object.create_new_row()
        self.CreateNewPopup(self,self.mainline_obj,new_paper_object, type="create")


    def populate_treeview(self):
        self.paper_tv.remove_all()
        # populate the treeview with items from the database
        for row in self.db_object.paper_objects:
            valid = True                
            if self.filters["year"].lower() not in row.get_year().lower() and self.filters["year"].strip().lower() != "": valid = False
            if self.filters["session"].lower() not in row.get_session().lower() and self.filters["session"].strip().lower() != "": valid = False
            if self.filters["timezone"].lower() not in row.get_timezone().lower() and self.filters["timezone"].strip().lower() != "": valid = False
            if self.filters["paper"].lower() not in row.get_paper().lower() and self.filters["paper"].strip().lower() != "": valid = False
            if self.filters["subject"].lower() not in row.get_subject().lower() and self.filters["subject"].strip().lower() != "": valid = False

            # print(self.filters["printed"].lower(),str(row.get_printed()).lower())
            if self.filters["printed"].lower() != str(row.get_printed()).lower() and self.filters["printed"].strip() != "": valid = False
            if self.filters["completed"].lower() != str(row.get_completed()).lower() and self.filters["completed"].strip() != "": valid = False
            if self.filters["partial"].lower() != str(row.get_partial()).lower() and self.filters["partial"].strip() != "": valid = False


            if self.filters["original_valid"].lower() != str(row.get_original_valid(-1)).lower() and self.filters["original_valid"].strip() != "": valid = False
            if self.filters["markscheme_valid"].lower() != str(row.get_markscheme_valid(-1)).lower() and self.filters["markscheme_valid"].strip() != "": valid = False
            if self.filters["scanned_valid"].lower() != str(row.get_scanned_valid(-1)).lower() and self.filters["scanned_valid"].strip() != "": valid = False

            if valid:
                if type(row.get_completed_date()) == pd._libs.tslibs.timestamps.Timestamp:
                    completed_date = str(row.get_completed_date().strftime("%d/%m/%Y"))
                else:
                    completed_date = ""
                self.paper_tv.insert_element(row,[row.get_name(), row.get_printed(), row.get_completed(), completed_date, row.get_scanned_valid(-1), row.get_notes()])

    
    def dropdown_handler(self, combo, type, event=None):
        self.filters[type.lower()]=combo.get()
        self.populate_treeview()


    def entry_filter_callback(self, sv, filter_type):
        self.filters[filter_type]=sv.get()
        self.populate_treeview()
    

    def create_selection_input(self,frame,pretty_print,type,row,column,values):


        filter_label = ttk.Label(frame,text=f"{pretty_print} filter")
        filter_label.grid(row=row,column=column,sticky="nw")

        filter_combo = ttk.Combobox(frame, values=[""] + values,state="readonly")
        filter_combo.grid(row=row,column=column+1,sticky="nw")
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.dropdown_handler(filter_combo, type))

    def create_filter_input(self, frame, type, row, column):


        self.filter_label = ttk.Label(frame,text=f"{type.title()} Filter")
        self.filter_label.grid(row=row,column=column,sticky="nw")


        entry_tracker = tk.StringVar()
        entry_tracker.trace("w", lambda name, index, mode, sv=entry_tracker: self.entry_filter_callback(entry_tracker, type))
        self.filter_entry = ttk.Entry(frame, textvariable=entry_tracker)
        self.filter_entry.grid(row=row,column=column+1,sticky="nw")


    def delete_command(self,event=None):
        continue_messagebox = tk.messagebox.askyesno(message=f"Are you sure you would like to delete {len(self.paper_tv.selection())} items?")
        if continue_messagebox:
            for selected_item in self.paper_tv.selection():
                self.paper_tv.get_object(selected_item).delete_item()
                self.paper_tv.delete(selected_item)


    def plot_selected_items(self,event=None):
        plot_df_dict = {"Name":[],"CompletedDate":[],"Percentage":[]}

        for selected_item in self.paper_tv.selection():
            paper_obj = self.paper_tv.get_object(selected_item)
            if type(paper_obj.get_completed_date()) == pd._libs.tslibs.timestamps.Timestamp:
                print("I got here")
                plot_df_dict["Name"].append(paper_obj.get_name())
                plot_df_dict["CompletedDate"].append(paper_obj.get_completed_date())
                plot_df_dict["Percentage"].append(paper_obj.get_percentage())
        plot_df = pd.DataFrame(plot_df_dict)
        print(plot_df)
        plot_df.plot(kind="scatter",x="CompletedDate",y="Percentage")
        #self.db.plot(kind = 'scatter', x = 'Duration', y = 'Maxpulse')
        plt.show()
    def __init__(self, mainline_obj, scrollable_frame):
        super().__init__(scrollable_frame)
        self.filters = {"year":"","session":"","timezone":"","paper":"","printed":"","subject":"","completed":"","partial":"","original_valid":"","markscheme_valid":"","scanned_valid":""}
        self.mainline_obj=mainline_obj
        self.db_object = self.mainline_obj.db_object
        self.paper_tv = treeview.TreeView(self,["Name","Printed","Completed","Completed Date","Scanned","Notes"],row=1,column=0,columnspan=5,double_click_function=self.tree_double_clicked,height=20)

        self.populate_treeview()
        
        self.plot_button = ttk.Button(self,text="Plot Filtered Items", command=self.plot_selected_items)
        self.plot_button.grid(row=3,column=4)
        self.delete_button = ttk.Button(self,text="Delete Selected",command=self.delete_command)
        self.delete_button.grid(row=3,column=3)

        for i,filter in enumerate(["year","session","timezone","paper","subject"]):
            self.create_filter_input(self,filter,row=i+5,column=0)

        i = i + 6

        self.create_selection_input(self,"Printed","printed",row=i,column=0,values=["True","False"])
        i+=1
        self.create_selection_input(self,"Completed","completed",row=i,column=0,values=["True","False"])
        i+=1
        self.create_selection_input(self,"Partial","partial",row=i,column=0,values=["True","False"])
        i+=1
        self.create_selection_input(self,"Original document valid","original_valid",row=i,column=0,values=["True","False"])
        i+=1
        self.create_selection_input(self,"Markscheme document valid","markscheme_valid",row=i,column=0,values=["True","False"])
        i+=1
        self.create_selection_input(self,"Scanned document valid","scanned_valid",row=i,column=0,values=["True","False"])
        
        self.bulk_load_button = ttk.Button(self, text="Bulk Load",command=self.bulk_load)
        self.bulk_load_button.grid(row=3,column=0)
        self.load_button = ttk.Button(self,text="Load New",command=self.load)
        self.load_button.grid(row=3,column=1)


        