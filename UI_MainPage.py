import tkinter as tk
from tkinter import ttk
import treeview, UI_Popup_Edit_Row, bulk_load
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scrollable_frame
import plotly.express as px
import values_and_rules
import customtkinter as ctk

class MainPage(ctk.CTkFrame):

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



    def tree_double_clicked(self,item):
        clicked_object = item["linked_object"]
        #loadnew_window = UI_Popup_Edit_Row.UIPopupEditRow(self.mainline_obj, self.mainline_obj.scrollable_frame,paper_obj=clicked_object,type="update")
        #loadnew_window.grid(row=0,column=0,sticky="nsew")
        self.mainline_obj.frames["DocumentViewerPage"].open_existing_document(clicked_object)
        self.mainline_obj.showwindow("DocumentViewerPage")



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


        import values_and_rules

        course_boundaries_list = values_and_rules.get_course_grade_boundaries()[self.mainline_obj.settings.course_type]
        course_boundaries_dict = {}
        course_boundaries_averages = {}
        for course_boundary in course_boundaries_list:
            course_boundaries_dict[course_boundary]=[]
            course_boundaries_averages[course_boundary]=0


        percentages_list = []

        filtered_objects = []
        # populate the treeview with items from the database
        for row in self.db_object.paper_objects:
            if row != None and row.get_course_type() == self.mainline_obj.settings.course_type:
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

                valid = True     
                if not filter(self.filters["Name"],row.get_name()): valid = False           
                if not filter(self.filters["Year"],row.get_year()): valid = False
                if not filter(self.filters["Session"],row.get_session()): valid = False
                if not filter(self.filters["Timezone"],row.get_timezone()): valid = False
                if not filter(self.filters["Paper"],row.get_paper()): valid = False
                if not filter(self.filters["Subject"],row.get_subject()): valid = False
                if not filter(self.filters["Level"],row.get_level()): valid = False




                #if self.filters["printed"].lower() != str(row.get_printed()).lower() and self.filters["printed"].strip() != "": valid = False
                #if self.filters["completed"].lower() != str(row.get_completed()).lower() and self.filters["completed"].strip() != "": valid = False
                #if self.filters["partial"].lower() != str(row.get_partial()).lower() and self.filters["partial"].strip() != "": valid = False

                if self.filters["Notes"].lower() not in str(row.get_notes()).lower() and self.filters["notes"].strip() != "": valid = False

                def is_na_type(date):
                    try:
                        if pd.isnull(date):
                            return True
                        else:
                            return False
                    except Exception as e:
                        return False



                if valid:

                    self.total_marks += row.get_mark()
                    self.total_maximum += row.get_maximum()

                    if float(row.get_percentage()) != 0:
                        self.total_marks_avg_counter += 1
                        percentages_list.append(row.get_percentage())


                    
                    for grade_boundary in course_boundaries_dict:
                        if row.get_grade_boudary_percentage(grade_boundary)>0:course_boundaries_dict[grade_boundary].append(row.get_grade_boudary_percentage(grade_boundary))

                    


                    filtered_objects.append(row)
        
        def calculate_percentage_average(param1,param2):
            average = 0
            if param2 != 0:
                average = round((param1/param2)*100)
            return average


        for grade_boundary in course_boundaries_dict:
            if len(course_boundaries_dict[grade_boundary]) > 0:
                course_boundaries_averages[grade_boundary]=round((sum(course_boundaries_dict[grade_boundary])/len(course_boundaries_dict[grade_boundary]))*100)

        average_percentage=0
        if len(percentages_list) > 0:
            average_percentage = round((sum(percentages_list)/len(percentages_list))*100)

        
        self.mark_label_edit(average_percentage,course_boundaries_averages)
        counter=0
        for filtered_row in filtered_objects:
            if filtered_row.get_course_type() == self.mainline_obj.settings.course_type:
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
                
                self.paper_tv.insert_element(filtered_row,[filtered_row.get_name(),filtered_row.get_year(), completed_date, str(round(filtered_row.get_percentage()*100)) + "%" , grade, notes_join])
                counter += 1


        self.paper_tv.pre_filter()
        self.paper_tv.oddevenconfigure("white","gray80")

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

        if self.terminology["show_" + type.lower()]:

            self.filter_label = ctk.CTkLabel(frame,text=f"FILTER {self.terminology[type].title()}")
            self.filter_label.grid(row=row,column=column,sticky="nw",pady=pady,padx=(15,10))


            entry_tracker = tk.StringVar()
            entry_tracker.trace("w", lambda name, index, mode, sv=entry_tracker: self.entry_filter_callback(entry_tracker, type))
            self.filter_entry = ctk.CTkEntry(frame, textvariable=entry_tracker)
            self.filter_entry.grid(row=row,column=column+1,sticky="nw",pady=pady,padx=(15,20))


    def delete_command(self,event=None):
        continue_messagebox = tk.messagebox.askyesno(message=f"Are you sure you would like to delete {len(self.paper_tv.tv_obj.selection())} items?")
        if continue_messagebox:
            for selected_item in self.paper_tv.tv_obj.selection():
                self.paper_tv.get_object(selected_item).delete_item()
                self.paper_tv.tv_obj.delete(selected_item)


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
    
    def mark_label_edit(self, average_percentage, average_grade_boundaries):
        text = "Average percentage: " + str(average_percentage) + "%\n\nAverage " + self.terminology["Grades"].lower() + ":"
        
        for grade_boundary in average_grade_boundaries:
            text +=f"\n{grade_boundary}: {average_grade_boundaries[grade_boundary]}%"


        self.mark_label["text"]=text
    

    def test(self,event):
        self.paper_tv.edit_treeview_width(event.width)

    def __init__(self, mainline_obj, scrollable_frame, grid_preload=  False):
        super().__init__(scrollable_frame)
        self.terminology = values_and_rules.get_terminology(mainline_obj.settings.get_course_type())
        self.filters = {"Year":"","Session":"","Timezone":"","Paper":"","Subject":"","Level":"","Notes":"","Name":""}
        self.mainline_obj=mainline_obj
        self.db_object = self.mainline_obj.db_object

        bubble_padx=20
        bubble_pady=10

        self.grid_columnconfigure(0, weight=1)
        

        self.tv_frame = ctk.CTkFrame(self,corner_radius=15,fg_color=self.mainline_obj.colors.bubble_background)
        self.grid_columnconfigure(0, weight=1)


        self.paper_tv = treeview.TreeView(self.mainline_obj,self.tv_frame,[[self.terminology["Name"],"name_str",0.3],[self.terminology["Year"],"year_int",0.1],["Completed Date","completed_date",0.1],["Percentage","mark_percentage",0.1],[self.terminology["Grade"],"grade_str",0.1],["Notes","notes_str",0.3]],row=1,column=0,columnspan=1,double_click_function=self.tree_double_clicked,height=20)

        self.tv_frame.grid(row=1,column=0,sticky="new",padx=bubble_padx,pady=bubble_pady)

        self.tv_frame.bind("<Configure>",self.test)

        self.filter_frame = ctk.CTkFrame(self,corner_radius=15,fg_color=self.mainline_obj.colors.bubble_background)
        self.filter_frame.grid_columnconfigure(1, weight=1)
        self.filter_frame.grid_columnconfigure(2, weight=1)
        self.filter_frame.grid_columnconfigure(3, weight=1)
        self.filter_frame.grid_columnconfigure(0, weight=1)


        self.filter_frame.grid(row=0,column=0,sticky="new",padx=bubble_padx,pady=bubble_pady)

        self.information_frame = ctk.CTkFrame(self,corner_radius=15,fg_color=self.mainline_obj.colors.bubble_background)
        self.information_frame.grid(row=2,column=0,sticky="new",padx=bubble_padx,pady=bubble_pady)
        self.information_frame.grid_columnconfigure(0, weight=1)

        self.actions_frame = ctk.CTkFrame(self,corner_radius=15,fg_color=self.mainline_obj.colors.bubble_background)
        self.actions_frame.grid(row=3,column=0,sticky="new",padx=bubble_padx,pady=bubble_pady)
        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid_columnconfigure(1, weight=1)
        self.actions_frame.grid_columnconfigure(2, weight=1)

        self.plot_button = ctk.CTkButton(self.actions_frame,text="Plot selected items (percentages)", width=35,height=40,command=self.plot_selected_items)
        self.plot_button.grid(row=0,column=0,padx=10,pady=15,sticky="ew")
        
        self.plot_button_grade = ctk.CTkButton(self.actions_frame,text="Plot selected items (grades)", width=35,height=40,command=lambda:self.plot_selected_items(grade_boundaries=True))
        self.plot_button_grade.grid(row=0,column=1,pady=15,padx=10,sticky="ew")
        self.delete_button = ctk.CTkButton(self.actions_frame,text="Delete selected items",width=35,height=40,command=self.delete_command)
        self.delete_button.grid(row=0,column=2,padx=10,pady=15,sticky="ew")
        
        i=5

        self.mark_label = ctk.CTkLabel(self.information_frame,text="Marks")
        self.mark_label.grid(row=0,column=0,padx=10,pady=10,sticky="nw")
        
        

        i+=1
        col = -2
        row=0

        for j,filter in enumerate(self.filters.keys()):
            if j%4 == 0:
                col += 2
            row = j%4

            self.create_filter_input(self.filter_frame,filter,row=row,column=col,pady=2)
            i+=1

        i = i + 1


        self.after_idle(self.populate_treeview)