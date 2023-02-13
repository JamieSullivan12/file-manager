import tkinter as tk
from tkinter import ttk
import treeview, UI_Popup_Edit_Row, bulk_load
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scrollable_frame
import plotly.express as px

class MainPage(ttk.Frame):

    class CreateNewPopup(tk.Toplevel):
        def __init__(self,parent,mainline_obj,clicked_object,type):
            super().__init__(parent.mainline_obj.parent)
            self.geometry("1400x900")
            if type == "update":
                self.title("Edit " + clicked_object.get_name())
            else:
                self.title("Create new paper object")
            self.grid_rowconfigure(0,weight=1)
            self.grid_columnconfigure(0,weight=1)
            self.scrollable_frame = scrollable_frame.ScrollableFrame(self)
            self.scrollable_frame.update()
            UI_Popup_Edit_Row.UIPopupEditRow(self,parent,self.scrollable_frame,mainline_obj,clicked_object,type)



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

        self.total_marks = 0
        self.total_maximum = 0
        self.total_marks_avg_counter = 0

        self.total_gb7 = [0,0,0]
        self.total_gb6 = [0,0,0]
        self.total_gb5 = [0,0,0]
        self.total_gb4 = [0,0,0]
        self.total_gb3 = [0,0,0]
        self.total_gb2 = [0,0,0]
        self.total_gb1 = [0,0,0]




        filtered_objects = []
        # populate the treeview with items from the database
        for row in self.db_object.paper_objects:
            def filter(param_a_list,param_b):
                param_elements = param_a_list.split(",")

                filter = False
                for item in param_elements:

                    if len(item.split("-")) > 1:
                        range_split = item.split("-")
                        try:
                            for i,range_split_item in enumerate(range_split):
                                range_split[i]=int(range_split_item)
                            range_split.sort()
                            min = range_split[0]
                            max = range_split[-1]
                            range_values = range(min,max+1,1)
                            for range_item in range_values:
                                if str(range_item).lower() in param_b.lower():
                                    filter = True
                        except Exception as e:
                            pass

                    if item.lower() in param_b.lower():
                        filter = True
                    

                    if len(item.split(" ")) > 1:
                        filter = True
                        space_split = item.split(" ")
                        for space_item in space_split:
                                if str(space_item).lower() not in param_b.lower():
                                    filter = False
                return filter

            if row != None:
                valid = True     
                if not filter(self.filters["name"],row.get_name()): valid = False           
                if not filter(self.filters["year"],row.get_year()): valid = False
                if not filter(self.filters["session"],row.get_session()): valid = False
                if not filter(self.filters["timezone"],row.get_timezone()): valid = False
                if not filter(self.filters["paper"],row.get_paper()): valid = False
                if not filter(self.filters["subject"],row.get_subject()): valid = False
                if not filter(self.filters["level"],row.get_level()): valid = False




                if self.filters["printed"].lower() != str(row.get_printed()).lower() and self.filters["printed"].strip() != "": valid = False
                if self.filters["completed"].lower() != str(row.get_completed()).lower() and self.filters["completed"].strip() != "": valid = False
                if self.filters["partial"].lower() != str(row.get_partial()).lower() and self.filters["partial"].strip() != "": valid = False

                if self.filters["notes"].lower() not in str(row.get_notes()).lower() and self.filters["notes"].strip() != "": valid = False


                if self.filters["original_valid"].lower() != str(row.get_original_valid(-1)).lower() and self.filters["original_valid"].strip() != "": valid = False
                if self.filters["markscheme_valid"].lower() != str(row.get_markscheme_valid(-1)).lower() and self.filters["markscheme_valid"].strip() != "": valid = False
                if self.filters["scanned_valid"].lower() != str(row.get_scanned_valid(-1)).lower() and self.filters["scanned_valid"].strip() != "": valid = False

                def is_na_type(date):
                    try:
                        if pd.isnull(date):
                            return True
                        else:
                            return False
                    except Exception as e:
                        return False


                if valid:
                    def add_row_percentage(gb,gbmax, array):
                        if float(gbmax) > 0 and float(gb) > 0:
                            gb = gb + array[0]
                            gbmax = gbmax + array[1]
                            counter = 1 + array[2]
                            return gb,gbmax,counter
                        else:
                            return array[0],array[1],array[2]



                    self.total_marks += row.get_mark()
                    self.total_maximum += row.get_maximum()

                    if float(row.get_percentage()) != 0:
                        self.total_marks_avg_counter += 1

                    self.total_gb7[0],self.total_gb7[1],self.total_gb7[2] = add_row_percentage(row.get_gb7(),row.get_gbmax(),self.total_gb7)
                    self.total_gb6[0],self.total_gb6[1],self.total_gb6[2] = add_row_percentage(row.get_gb6(),row.get_gbmax(),self.total_gb6)
                    self.total_gb5[0],self.total_gb5[1],self.total_gb5[2] = add_row_percentage(row.get_gb5(),row.get_gbmax(),self.total_gb5)
                    self.total_gb4[0],self.total_gb4[1],self.total_gb4[2] = add_row_percentage(row.get_gb4(),row.get_gbmax(),self.total_gb4)
                    self.total_gb3[0],self.total_gb3[1],self.total_gb3[2] = add_row_percentage(row.get_gb3(),row.get_gbmax(),self.total_gb3)
                    self.total_gb2[0],self.total_gb2[1],self.total_gb2[2] = add_row_percentage(row.get_gb2(),row.get_gbmax(),self.total_gb2)
                    self.total_gb1[0],self.total_gb1[1],self.total_gb1[2] = add_row_percentage(row.get_gb1(),row.get_gbmax(),self.total_gb1)
                    

                    filtered_objects.append(row)
        
        def calculate_percentage_average(param1,param2):
            average = 0
            if param2 != 0:
                average = round((param1/param2)*100)
            return average



        self.total_gb7[2] = calculate_percentage_average(self.total_gb7[0],self.total_gb7[1])
        self.total_gb6[2] = calculate_percentage_average(self.total_gb6[0],self.total_gb6[1])
        self.total_gb5[2] = calculate_percentage_average(self.total_gb5[0],self.total_gb5[1])
        self.total_gb4[2] = calculate_percentage_average(self.total_gb4[0],self.total_gb4[1])
        self.total_gb3[2] = calculate_percentage_average(self.total_gb7[0],self.total_gb7[1])
        self.total_gb2[2] = calculate_percentage_average(self.total_gb2[0],self.total_gb2[1])
        self.total_gb1[2] = calculate_percentage_average(self.total_gb1[0],self.total_gb1[1])
        

        if self.total_maximum != 0:
            self.percentage_average = round((self.total_marks/self.total_maximum)*100)

        else: self.percentage_average = 0

        #self.percentage_average = calculate_average(percentage_mark,self.total_marks_avg_counter)


        self.filtered_grade = None
        
        # NOTE: fix logic for grade that is zero
        if self.percentage_average >= self.total_gb7[2] and self.total_gb7[2] != 0: self.filtered_grade=7
        elif self.percentage_average >= self.total_gb6[2] and self.total_gb6[2] != 0: self.filtered_grade=6
        elif self.percentage_average >= self.total_gb5[2] and self.total_gb5[2] != 0: self.filtered_grade=5
        elif self.percentage_average >= self.total_gb4[2] and self.total_gb4[2] != 0: self.filtered_grade=4
        elif self.percentage_average >= self.total_gb3[2] and self.total_gb3[2] != 0: self.filtered_grade=3
        elif self.percentage_average >= self.total_gb2[2] and self.total_gb2[2] != 0: self.filtered_grade=2
        elif self.percentage_average >= self.total_gb1[2] and self.total_gb1[2] != 0: self.filtered_grade=1
        else: self.filtered_grade=None

        self.mark_label_edit(self.percentage_average,self.filtered_grade,self.total_gb7,self.total_gb6,self.total_gb5,self.total_gb4,self.total_gb3,self.total_gb2,self.total_gb1)


        for filtered_row in filtered_objects:
            if type(filtered_row.get_completed_date()) == pd._libs.tslibs.timestamps.Timestamp:
                completed_date = str(filtered_row.get_completed_date().strftime("%d/%m/%Y"))
            else:
                completed_date = ""
            notes_split = filtered_row.get_notes().strip().split("\n")
            notes_join = "; ".join(notes_split)
            grade = filtered_row.get_grade()
            if grade == -1:
                grade = ""
            else:
                grade = str(grade)
            self.paper_tv.insert_element(filtered_row,[filtered_row.get_name(),filtered_row.get_year(), filtered_row.get_printed(), filtered_row.get_completed(), completed_date, str(round(filtered_row.get_percentage()*100)) + "%" , grade, notes_join])

        self.paper_tv.pre_filter()

    def dropdown_handler(self, combo, type, event=None):
        self.filters[type.lower()]=combo.get()
        self.populate_treeview()


    def entry_filter_callback(self, sv, filter_type):
        self.filters[filter_type]=sv.get()
        self.populate_treeview()
    

    def create_selection_input(self,frame,pretty_print,type,row,column,values,pady=0):


        filter_label = ttk.Label(frame,text=f"{pretty_print} filter")
        filter_label.grid(row=row,column=column,sticky="nw",pady=pady)

        filter_combo = ttk.Combobox(frame, values=[""] + values,state="readonly")
        filter_combo.grid(row=row,column=column+1,sticky="nw",pady=pady)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.dropdown_handler(filter_combo, type))

    def create_filter_input(self, frame, type, row, column,pady=0):


        self.filter_label = ttk.Label(frame,text=f"{type.title()} Filter")
        self.filter_label.grid(row=row,column=column,sticky="nw",pady=pady)


        entry_tracker = tk.StringVar()
        entry_tracker.trace("w", lambda name, index, mode, sv=entry_tracker: self.entry_filter_callback(entry_tracker, type))
        self.filter_entry = ttk.Entry(frame, textvariable=entry_tracker)
        self.filter_entry.grid(row=row,column=column+1,sticky="nw",pady=pady)


    def delete_command(self,event=None):
        continue_messagebox = tk.messagebox.askyesno(message=f"Are you sure you would like to delete {len(self.paper_tv.selection())} items?")
        if continue_messagebox:
            for selected_item in self.paper_tv.selection():
                self.paper_tv.get_object(selected_item).delete_item()
                self.paper_tv.delete(selected_item)


    def plot_selected_items(self,grade_boundaries = False,event=None):
        plot_df_dict = {"Name":[],"CompletedDate":[],"Percentage":[],"Grade":[]}
        for selected_item in self.paper_tv.selection():
            paper_obj = self.paper_tv.get_object(selected_item)
            if type(paper_obj.get_completed_date()) == pd._libs.tslibs.timestamps.Timestamp and (paper_obj.get_percentage() != 0):
                if grade_boundaries == True and paper_obj.get_grade() != -1:
                    plot_df_dict["Name"].append(paper_obj.get_name())
                    plot_df_dict["CompletedDate"].append(paper_obj.get_completed_date())
                    plot_df_dict["Percentage"].append(round(paper_obj.get_percentage()*100))
                    plot_df_dict["Grade"].append(paper_obj.get_grade())
                elif grade_boundaries == False:
                    plot_df_dict["Name"].append(paper_obj.get_name())
                    plot_df_dict["CompletedDate"].append(paper_obj.get_completed_date())
                    plot_df_dict["Percentage"].append(round(paper_obj.get_percentage()*100))
                    plot_df_dict["Grade"].append(paper_obj.get_grade())

        plot_df = pd.DataFrame(plot_df_dict)
        #plot_df.plot(kind="line",x="CompletedDate",y="Percentage",ylim=(0,1))
        plot_df['CompletedDate'] = pd.to_datetime(plot_df['CompletedDate']).dt.date
        plot_df.sort_values(by='CompletedDate', inplace=True)
        if grade_boundaries == True:
            fig = px.line(plot_df, x="CompletedDate", y="Grade",hover_name="Name", text="Name", markers=True)
            fig.update_layout(yaxis_range=[0,8])

        else:
            fig = px.line(plot_df, x="CompletedDate", y="Percentage",hover_name="Name", text="Name", markers=True)
            fig.update_layout(yaxis_range=[0,100])


        fig.update_layout(xaxis=dict(tickformat="%d/%m/%Y"))
        fig.update_traces(textposition="bottom right")
        fig.show()


    def change_sort_type(self,sort_combo):
        self.sort_type=sort_combo.get()
        self.populate_treeview()
    
    def mark_label_edit(self,percentage, grade_boundary, gb7,gb6,gb5,gb4,gb3,gb2,gb1):
        self.mark_label["text"]="Average percentage: " + str(percentage) + "%\nAverage grade: " + str(grade_boundary) + f"\n\nGrade boundary averages\nGB 7: {gb7[2]}%\nGB 6: {gb6[2]}%\nGB 5: {gb5[2]}%\nGB 4: {gb4[2]}%\nGB 3: {gb3[2]}%\nGB 2: {gb2[2]}%\nGB 1: {gb1[2]}%"
    

    

    def __init__(self, mainline_obj, scrollable_frame, grid_preload=  False):
        super().__init__(scrollable_frame)

        self.filters = {"year":"","session":"","timezone":"","paper":"","printed":"","subject":"","completed":"","partial":"","original_valid":"","markscheme_valid":"","scanned_valid":"","level":"","notes":"","name":""}
        self.mainline_obj=mainline_obj
        self.db_object = self.mainline_obj.db_object
        self.paper_tv = treeview.TreeView(self,[["Name","name_str",250],["Year","year_int",125],["Printed","printed_bool",135],["Completed","completed_bool",135],["Completed Date","completed_date",175],["Mark","mark_percentage",125],["Grade","grade_int",125],["Notes","notes_str",275]],row=1,column=0,columnspan=5,double_click_function=self.tree_double_clicked,height=20)


        self.sort_type = "Year Descending"

        
        self.plot_button = ttk.Button(self,text="Plot selected items (percentages)", width=35,command=self.plot_selected_items)
        self.plot_button.grid(row=3,column=4,sticky="n")
        
        self.plot_button_grade = ttk.Button(self,text="Plot selected items (grades)", width=35,command=lambda:self.plot_selected_items(grade_boundaries=True))
        self.plot_button_grade.grid(row=4,column=4,sticky="n",pady=5)
        self.delete_button = ttk.Button(self,text="Delete selected items",width=35,command=self.delete_command)
        self.delete_button.grid(row=3,column=3)
        
        i=5
        
        #self.create_selection_input(self,"Filter type","scanned_valid",row=i,column=0,values=["True","False"])

        self.mark_label = ttk.Label(self,text="Marks")
        self.mark_label.grid(row=i,column=2,padx=20,pady=10,sticky="nw",rowspan=10)
        
        

        i+=1
        for j,filter in enumerate(["name","year","session","timezone","paper","subject","level","notes"]):
            self.create_filter_input(self,filter,row=i,column=0,pady=2)
            i+=1

        i = i + 1

        self.create_selection_input(self,"Printed","printed",row=i,column=0,values=["True","False"],pady=(10,0))
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


        self.bulk_load_button = ttk.Button(self, text="Bulk Load",width=35,command=self.bulk_load)
        self.bulk_load_button.grid(row=3,column=0)
        self.load_button = ttk.Button(self,text="Load New",width=35,command=self.load)
        self.load_button.grid(row=3,column=1)

        #self.mainline_obj.parent.update()
        #self.populate_treeview()


        self.after_idle(self.populate_treeview)