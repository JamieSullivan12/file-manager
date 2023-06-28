import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import pandas as pd
import plotly.express as px
import treeview, values_and_rules

class MainPage(ctk.CTkScrollableFrame):


    def tree_double_clicked_event(self,item):
        """
        Row on the treeview is clicked twice. This will cause the user to be directed to the page where they can
        view the double clicked Paper
        """

        # find the class of the clicked object
        clicked_object = item.linked_object
        # open the DocumentViewerPage with the clicked object
        self.mainline_obj.get_frame_object("DocumentViewerPage").open_existing_document(clicked_object)
        self.mainline_obj.show_frame("DocumentViewerPage")


    def removed_treeview_row_event(self,tv_row_obj):
        tv_row_obj.linked_object.delete_past_paper_obj()


    def populate_treeview(self):
        """
        Completely re-fill the treeview object. This involves wiping all current rows, and then re-filling based on the Paper objects
        stored in the database
        """

        self.treeview_obj.remove_all()


        # used for average statistics shown, concerning all items shown in the treeview
        self.total_marks = 0
        self.total_maximum = 0
        self.total_marks_avg_counter = 0
        
        # get the grade boundary levels for the currently selected course - used for average statistics
        course_boundaries_list = values_and_rules.get_course_grade_boundaries()[self.mainline_obj.settings.course_type]
        course_boundaries_dict = {}
        course_boundaries_averages = {}

        # setup dict of all grade boundaries with value 0. Dict used to add up grade boundaries of all 
        # Papers shown (to calculate an average for each grade boundadry)
        for course_boundary in course_boundaries_list:
            course_boundaries_dict[course_boundary]=[]
            course_boundaries_averages[course_boundary]=0


        percentages_list = []

        filtered_objects = []

        filtered_paper_objects=self.mainline_obj.db_object.get_filtered_paper_items(name_filter=self.filters["Name"],year_filter=self.filters["Year"],session_filter=self.filters["Session"],timezone_filter=self.filters["Timezone"],paper_filter=self.filters["Paper"],subject_filter=self.filters["Subject"],level_filter=self.filters["Level"])



        def calculate_percentage_average(param1,param2):
            average = 0
            if param2 != 0:
                average = round((param1/param2)*100)
            return average


        
        counter=0
        for filtered_paper_object_id in filtered_paper_objects:
            filtered_paper_object = filtered_paper_objects[filtered_paper_object_id]

            # create summary (average) data for all objects (marks and grade boundaries)
            if float(filtered_paper_object.get_percentage()) != 0:
                self.total_marks_avg_counter += 1
                percentages_list.append(filtered_paper_object.get_percentage())
                self.total_marks += filtered_paper_object.get_mark()
                self.total_maximum += filtered_paper_object.get_maximum()
            for grade_boundary in course_boundaries_dict:
                if filtered_paper_object.get_grade_boudary_percentage(grade_boundary)>0:
                    course_boundaries_dict[grade_boundary].append(filtered_paper_object.get_grade_boudary_percentage(grade_boundary))

            # add row to the treeview
            # make notes readable on a single treeview line
            notes_split = filtered_paper_object.get_notes().strip().split("\n")
            notes_join = "; ".join(notes_split)

            grade = filtered_paper_object.get_grade()
            if grade == -1:
                grade = ""
            else:
                grade = str(grade)
            
            self.treeview_obj.insert_element(filtered_paper_object,column_data=[filtered_paper_object.get_name(),filtered_paper_object.get_year(), filtered_paper_object.get_completed_date_pretty(), str(round(filtered_paper_object.get_percentage()*100)) + "%" , grade, notes_join],double_clicked_function=self.tree_double_clicked_event, remove_function=self.removed_treeview_row_event)
            counter += 1


        for grade_boundary in course_boundaries_dict:
            if len(course_boundaries_dict[grade_boundary]) > 0:
                course_boundaries_averages[grade_boundary]=round((sum(course_boundaries_dict[grade_boundary])/len(course_boundaries_dict[grade_boundary]))*100)

        average_percentage=0
        if len(percentages_list) > 0:
            average_percentage = round((sum(percentages_list)/len(percentages_list))*100)
        self.summary_label_edit(average_percentage,course_boundaries_averages)


        self.treeview_obj.pre_sort()
        self.treeview_obj.oddevenconfigure("white","gray80")

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


        filter_label = ctk.CTkLabel(frame,text=f"FILTER {self.terminology[type].title()}")
        filter_label.grid(row=row,column=column,sticky="nw",pady=pady,padx=(15,10))


        entry_tracker = tk.StringVar()
        entry_tracker.trace("w", lambda name, index, mode, sv=entry_tracker: self.entry_filter_callback(entry_tracker, type))
        filter_entry = ctk.CTkEntry(frame, textvariable=entry_tracker)
        filter_entry.grid(row=row,column=column+1,sticky="nw",pady=pady,padx=(15,20))

        return filter_label,filter_entry


    def delete_command(self,event=None):
        continue_messagebox = tk.messagebox.askyesno(message=f"Are you sure you would like to delete {len(self.treeview_obj.tv_obj.selection())} items?")
        if continue_messagebox:
            for selected_item in self.treeview_obj.tv_obj.selection():
                self.treeview_obj.remove_treeview_row([selected_item])


    def plot_selected_items(self,grade_boundaries = False,event=None):
        plot_df_dict = {"Name":[],"CompletedDate":[],"Percentage":[],"Grade":[]}
        for selected_item in self.treeview_obj.tv_obj.selection():
            paper_obj = self.treeview_obj.tv_obj.get_object(selected_item)
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


    def grid_apply(self,item,rc,cc,c_mod,r_mod,**kwargs):
        """
        Grid an item onto the screen based on the row count (rc) and column count (cc). Increment rc and cc accordingly to match the 
        modulus requirements defined by c_mod and r_mod

        IN
        - rc (int): row for grid
        - cc (int): column for grid
        - c_mod (int): the column value for which row is incremented and column count (cc) is reset
        - r_mod (int): the row value for which column is incremented and row count (rc) is reset
        
        """

        try:
            item.grid_forget()
        except Exception as e:
            pass

        item.grid(row=rc,column=cc,**kwargs)
        cc+=1
        if cc%c_mod==0:
            rc+=1
            cc-=c_mod
        
        if rc%r_mod==0 and rc!=0:
            cc+=c_mod
            rc-=r_mod
        
        return rc,cc
    

    
    def summary_label_edit(self, average_percentage, average_grade_boundaries):
        text = "Average percentage: " + str(average_percentage) + "%\n\nAverage " + self.terminology["Grades"].lower() + ":"
        
        for grade_boundary in average_grade_boundaries:
            text +=f"\n{grade_boundary}: {average_grade_boundaries[grade_boundary]}%"


        self.summary_label.configure(text=text)
    
    def colconfig(self,widget,colrangestart,colrangeend,weight):
        """
        Configure the weight of columns inside a widget

        IN:
        - widget (tkinter or customtkinter Frame): the widget to be configured
        - colrangestart (int): the first column to configure
        - colrangeend (int): the last column (inclusive) to configure
        - weight (int): the weight to apply to the columns between and including colrangestart and colrangeend
        """
        
        i = colrangestart
        while i<=colrangeend:
            widget.grid_columnconfigure(i, weight=weight)
            i+=1

    def make_grid_filter(self,critical):
        

        rc=0 # row counter
        cc=0 # column counter
        c_mod=2
        r_mod=4
        if critical <=2:
            r_mod=10000
            self.colconfig(self.filter_inner_frame,0,1,1)
            self.colconfig(self.filter_inner_frame,2,7,0)
        elif critical <=4:
            r_mod=4
            self.colconfig(self.filter_inner_frame,0,3,1)
            self.colconfig(self.filter_inner_frame,4,7,0)
        else:
            r_mod=2
            self.colconfig(self.filter_inner_frame,0,7,1)
        print(len(self.filter_widgets))
        for item in self.filter_widgets:
            rc,cc=self.grid_apply(item[0],rc=rc,cc=cc,c_mod=c_mod,r_mod=r_mod,sticky="nw",padx=2,pady=2)
            rc,cc=self.grid_apply(item[1],rc=rc,cc=cc,c_mod=c_mod,r_mod=r_mod,sticky="nw",padx=2,pady=2)

    def make_grid_buttons(self,critical):
        
        rc=0 # row counter
        cc=0 # column counter
        c_mod=100
        r_mod=1

        if critical <=2:
            r_mod=100
            c_mod=1

        rc,cc=self.grid_apply(self.plot_button,rc=rc,cc=cc,c_mod=c_mod,r_mod=r_mod,sticky="ew",padx=10,pady=15)
        rc,cc=self.grid_apply(self.plot_button_grade,rc=rc,cc=cc,c_mod=c_mod,r_mod=r_mod,sticky="ew",padx=10,pady=15)
        rc,cc=self.grid_apply(self.delete_button,rc=rc,cc=cc,c_mod=c_mod,r_mod=r_mod,sticky="ew",padx=10,pady=15)


        

    def make_grid(self,critical):
        """
        Resize MainPage event
        """

        # resize treeview
        if critical <=2:self.treeview_obj.apply_width_state(True)
        else:self.treeview_obj.apply_width_state(False)
        
        
        self.make_grid_filter(critical=critical)
        self.make_grid_buttons(critical=critical)



    def __init__(self, mainline_obj, parent_frame):
        super().__init__(parent_frame)
        self.terminology = values_and_rules.get_terminology(mainline_obj.settings.get_course_type())
        self.filters = {"Year":"","Session":"","Timezone":"","Paper":"","Subject":"","Level":"","Notes":"","Name":""}
        self.mainline_obj=mainline_obj

        bubble_padx=20
        bubble_pady=10

        self.grid_columnconfigure(0, weight=1)

        # create treeview viewer
        self.treeview_frame = ctk.CTkFrame(self,corner_radius=15,fg_color=self.mainline_obj.colors.bubble_background)
        self.treeview_obj = treeview.TreeView(self.treeview_frame,{"name":[self.terminology["Name"],0.3,0.4],"year":[self.terminology["Year"],0.1,0.3],"completed_date":["Completed Date",0.2,0],"percentage":["Percentage",0.1,0.3],"grade":[self.terminology["Grade"],0.1,0],"notes":["Notes",0.2,0]},height=20)
        self.treeview_obj.grid(row=0,column=1,padx=25,pady=25,sticky="new")

        self.treeview_frame.grid(row=1,column=0,sticky="new",padx=bubble_padx,pady=bubble_pady)

        # create filter inputs
        self.filter_frame = ctk.CTkFrame(self,corner_radius=15,fg_color=self.mainline_obj.colors.bubble_background)
        self.filter_frame.grid_columnconfigure(0, weight=1)
        self.filter_frame.grid(row=0,column=0,sticky="new",padx=bubble_padx,pady=bubble_pady)
        self.filter_label=ctk.CTkLabel(self.filter_frame,text="Filter options",font=(None,15))
        self.filter_label.grid(row=0,column=0,columnspan=1,padx=10,pady=(5,0),sticky="nw")
        self.filter_inner_frame = ctk.CTkFrame(self.filter_frame,fg_color="transparent")
        self.filter_inner_frame.grid(row=1,column=0,padx=10,pady=(0,10))

        # display all filter inputs accounting for resizing

        self.filter_widgets=[]
        for j,filter in enumerate(self.filters.keys()):
            if self.terminology["show_" + filter.lower()]:
                self.filter_widgets.append(self.create_filter_input(self.filter_inner_frame,filter,row=0,column=0,pady=2))

        # create information summary displayer
        self.information_frame = ctk.CTkFrame(self,corner_radius=15,fg_color=self.mainline_obj.colors.bubble_background)
        self.information_frame.grid(row=2,column=0,sticky="new",padx=bubble_padx,pady=bubble_pady)
        self.information_frame.grid_columnconfigure(0, weight=1)
        self.summary_label = ctk.CTkLabel(self.information_frame,text="Marks")
        self.summary_label.grid(row=0,column=0,padx=10,pady=10,sticky="nw")
        
        # create frame for action buttons (e.g. delete selected items)
        self.actions_frame = ctk.CTkFrame(self,corner_radius=15,fg_color=self.mainline_obj.colors.bubble_background)
        self.actions_frame.grid(row=3,column=0,sticky="new",padx=bubble_padx,pady=bubble_pady)
        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid_columnconfigure(1, weight=1)
        self.actions_frame.grid_columnconfigure(2, weight=1)
        self.plot_button = ctk.CTkButton(self.actions_frame,text="Plot selected items (percentages)", width=35,height=40,command=self.plot_selected_items)
        self.plot_button_grade = ctk.CTkButton(self.actions_frame,text="Plot selected items (grades)", width=35,height=40,command=lambda:self.plot_selected_items(grade_boundaries=True))
        self.delete_button = ctk.CTkButton(self.actions_frame,text="Delete selected items",width=35,height=40,command=self.delete_command)
        

        self.after_idle(self.populate_treeview)
        self.mainline_obj.top_frame_resize_event(specific="MainPage")