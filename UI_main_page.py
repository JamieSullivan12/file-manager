import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import pandas as pd
import plotly.express as px
import treeview, dropdown_autocomplete, CommonFunctions


class MainPage(ctk.CTkScrollableFrame):

    def __init__(self, mainline_obj, parent_frame):
        super().__init__(parent_frame)

        # Reference to the mainline_obj to access shared data and methods
        self.mainline_obj = mainline_obj
        self.course_values = mainline_obj.get_course_values()

        # Filters for filtering data in the treeview
        self.filters = {
            "Year": "", "Session": "", "Timezone": "", "Paper": "", "Subject": "",
            "Level": "", "Notes": "", "Name": ""
        }

        # Padding values for bubbles
        bubble_padx = 20
        bubble_pady = 10

        # Configure column weight for resizing
        self.grid_columnconfigure(0, weight=1)

        # Create treeview viewer
        self.treeview_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=self.mainline_obj.colors.bubble_background)
        # instantiate the treeview object. The treeview object is a custom tkinter widget that is used to display the PastPaper objects (this is inherited in a dev-defined class)
        # the treeview object is instantiated with the following parameters:
        # note: the columns are defined with the following list: [column_name, column_width (wide), column_width (narrow), daatatype, None]
        self.treeview_obj = treeview.TreeView(self.treeview_frame, {
            "name": [self.course_values.name, 0.3, 0.4, "str", None],
            "year": [self.course_values.year, 0.1, 0.3, "int", None],
            "completed_date": ["Completed Date", 0.2, 0, "date", None],
            "percentage": ["Percentage", 0.1, 0.3, "percentage", None],
            "grade": [self.course_values.grade, 0.1, 0, "str", None],
            "notes": ["Notes", 0.2, 0, "str", None]
        }, height=20)
        self.treeview_obj.grid(row=0, column=1, padx=25, pady=25, sticky="new")
        self.treeview_frame.grid(row=1, column=0, sticky="new", padx=bubble_padx, pady=bubble_pady)

        # Dictionary to store visibility flags for filter inputs
        # Visibility of certain inputs depends on the selected course
        self.terminology_visible_flags = {
            "name": [self.course_values.show_name, self.course_values.name, {}],
            "year": [self.course_values.show_year, self.course_values.year, {}],
            "notes": [self.course_values.show_notes, self.course_values.notes, {}],
            "session": [self.course_values.show_session, self.course_values.session, self.course_values.dict_session],
            "timezone": [self.course_values.show_timezone, self.course_values.timezone, self.course_values.dict_timezone],
            "paper": [self.course_values.show_paper, self.course_values.paper, self.course_values.dict_paper],
            "subject": [self.course_values.show_subject, self.course_values.subject, {}],
            "level": [self.course_values.show_level, self.course_values.level, self.course_values.dict_level]
        }


        # Create filter inputs
        self.filter_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=self.mainline_obj.colors.bubble_background)
        self.filter_frame.grid_columnconfigure(0, weight=1)
        self.filter_frame.grid(row=0, column=0, sticky="new", padx=bubble_padx, pady=bubble_pady)
        self.filter_label = ctk.CTkLabel(self.filter_frame, text="Filter options", font=(None, 15))
        self.filter_label.grid(row=0, column=0, columnspan=1, padx=10, pady=(5, 0), sticky="nw")
        self.filter_inner_frame = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        self.filter_inner_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nw")


        # Create filter widgets
        self.filter_widgets = []
        for j, filter in enumerate(self.filters.keys()):
            if self.terminology_visible_flags[filter.lower()][0]:
                if self.terminology_visible_flags[filter.lower()][2] != {}:
                    autofill = self.terminology_visible_flags[filter.lower()][2].values()
                elif filter.lower() == "subject":
                    autofill = list(self.mainline_obj.settings.subjects.values())
                else:
                    autofill = []
                self.filter_widgets.append(
                    self.create_filter_input(
                        self.terminology_visible_flags[filter.lower()][1], self.filter_inner_frame,
                        filter, row=0, column=0, autofill=autofill, pady=2
                    )
                )

        # Create information summary displayer
        self.information_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=self.mainline_obj.colors.bubble_background)
        self.information_frame.grid(row=2, column=0, sticky="new", padx=bubble_padx, pady=bubble_pady)
        self.information_frame.grid_columnconfigure(0, weight=1)
        self.summary_label_1 = ctk.CTkLabel(self.information_frame, text="Marks")
        self.summary_label_1.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nw")
        self.summary_label_2 = ctk.CTkLabel(self.information_frame, text="Marks")
        self.summary_label_2.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nw")

        # Create frame for action buttons (e.g. delete selected items)
        self.actions_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=self.mainline_obj.colors.bubble_background)
        self.actions_frame.grid(row=3, column=0, sticky="new", padx=bubble_padx, pady=bubble_pady)
        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid_columnconfigure(1, weight=1)
        self.plot_button = ctk.CTkButton(
            self.actions_frame, text="Plot selected items (percentages)", width=35, height=40, command=self.plot_selected_items
        )
        self.delete_button = ctk.CTkButton(
            self.actions_frame, text="Delete selected items", width=35, height=40, command=self.delete_command
        )

        
        self.after_idle(self.populate_treeview)
        

    def tree_double_clicked_event(self,item):
        """
        Row on the treeview is clicked twice. This will cause the user to be directed to the page where they can
        view the double clicked PastPaper object
        """

        # find the class of the clicked object
        clicked_object = item.linked_object
        # open the DocumentViewerPage with the clicked object
        self.mainline_obj.get_frame_object("DocumentViewerPage").open_existing_document(clicked_object)
        self.mainline_obj.show_frame("DocumentViewerPage")

    def removed_treeview_row_event(self,tv_row_obj):
        tv_row_obj.linked_object.remove_past_paper()

    def delete_command(self,event=None):
        """
        Delete all selected items from the treeview. This will also delete the corresponding PastPaper objects
        """

        continue_messagebox = tk.messagebox.askyesno(message=f"Are you sure you would like to delete {len(self.treeview_obj.tv_obj.selection())} past papers?")
        if continue_messagebox:
            for selected_item in self.treeview_obj.tv_obj.selection():
                # remove the PastPaper object from the database
                self.treeview_obj.remove_treeview_row([selected_item])

    def summary_label_edit(self, average_percentage, average_grade_boundaries):
        text1 = f"Average percentage: {average_percentage}%"

        text2 = "Average " + self.course_values.grades.lower() + ":"
        for grade_boundary in average_grade_boundaries:
            text2 +=f"\n{grade_boundary}: {average_grade_boundaries[grade_boundary]}%"
        
        self.summary_label_1.configure(text=text1)
        self.summary_label_2.configure(text=text2)

    def add_to_pack(self,expand=False,anchor="n",fill="both"):
        self.pack(expand=expand, anchor=anchor, fill=fill)

    def remove_from_pack(self):
        self.pack_forget()

    def populate_treeview(self):
        """
        Completely re-fill the treeview object. This involves wiping all current rows, and then re-filling based on the Paper objects
        stored in the database and the filters currently applied

        Note: this is an efficient process and is repeatedly called whenever a new filter is applied
        """

        self.treeview_obj.remove_all()

        # get the grade boundary levels for the currently selected course - used for average statistics
        course_boundaries_list = self.mainline_obj.get_course_values().grade_boundaries
        course_boundaries_dict = {}
        course_boundaries_averages = {}

        # setup dict of all grade boundaries with default value 0. Dict used to add up grade boundaries of all 
        # Papers shown (to calculate an average for each grade boundary of shown papers)
        for course_boundary in course_boundaries_list:
            course_boundaries_dict[course_boundary]=[]
            course_boundaries_averages[course_boundary]=0

        percentages_list = []

        for subject_filter in self.filters["Subject"].split(","):
            if subject_filter.casefold() in list(value.casefold() for value in self.mainline_obj.settings.get_subjects()):
                if not self.mainline_obj.settings.get_subjects()[subject_filter.upper()] in self.filters["Subject"]:
                    self.filters["Subject"] = ",".join([self.filters["Subject"],self.mainline_obj.settings.get_subjects()[subject_filter.upper()]])

        filtered_paper_objects=self.mainline_obj.db_object.get_filtered_paper_items(name_filter=self.filters["Name"],year_filter=self.filters["Year"],session_filter=self.filters["Session"],timezone_filter=self.filters["Timezone"],paper_filter=self.filters["Paper"],subject_filter=self.filters["Subject"],level_filter=self.filters["Level"])

        # loop through all filtered Paper objects and add them to the treeview (also add to average statistics)
        for filtered_paper_object in filtered_paper_objects:
            # create summary (average) data for all objects (percentage and grade boundaries)
            # only include objects with valid percentage (i.e. not -1 which is the default set when percentage invalid)
            if float(filtered_paper_object.get_percentage()) >= 0:
                percentages_list.append(filtered_paper_object.get_percentage())
            for grade_boundary in course_boundaries_dict:
                if filtered_paper_object.get_grade_boundary_percentage(grade_boundary)>0:
                    course_boundaries_dict[grade_boundary].append(filtered_paper_object.get_grade_boundary_percentage(grade_boundary))

            # get the PastPaper object "notes" value, making it readable for the single-line treeview row
            notes_split = filtered_paper_object.get_notes().strip().split("\n")
            notes_join = "; ".join(notes_split)

            # get the PastPaper object "grade" value, making it readable for the single-line treeview row (default value for no grade is -1, which is set to "")
            grade = filtered_paper_object.get_grade()
            if grade == -1:
                grade = ""
            else:
                grade = str(grade)
            
            # add the Paper object to the treeview
            self.treeview_obj.insert_element(filtered_paper_object,column_data=[filtered_paper_object.get_name(),filtered_paper_object.get_year(), filtered_paper_object.get_completed_date_pretty(), filtered_paper_object.get_percentage_pretty(), grade, notes_join],double_clicked_function=self.tree_double_clicked_event, remove_function=self.removed_treeview_row_event)


        # create average statistics for grade boundaries and percentages for all shown Papers
        for grade_boundary in course_boundaries_dict:
            if len(course_boundaries_dict[grade_boundary]) > 0:
                course_boundaries_averages[grade_boundary]=round((sum(course_boundaries_dict[grade_boundary])/len(course_boundaries_dict[grade_boundary]))*100)
        average_percentage=0
        if len(percentages_list) > 0:
            average_percentage = round((sum(percentages_list)/len(percentages_list))*100)
        self.summary_label_edit(average_percentage,course_boundaries_averages)

        self.treeview_obj.pre_sort() # sort the treeview
        self.treeview_obj.oddevenconfigure("white","gray80") # configure odd/even rows to be different colours

    def entry_filter_callback(self, sv, filter_type):
        """
        Set the filter value for the filter type (e.g. "Name") to the value of the entry box for that filter type
        
        IN:
        - sv: entry box variable tracker
        - filter_type (str): the filter type of that entry box (e.g. "Name")
        """

        self.filters[filter_type]=sv.get()
        # apply the filters to the treeview
        self.populate_treeview()
    

    def create_filter_input(self,label_text, frame, type, row, column,autofill = [],pady=0):
        """
        Create a filter input (label and entry box) for a given filter type

        IN:
        - label_text (str): the text to display on the label
        - frame (tkinter or customtkinter Frame): the frame to place the filter input on
        - type (str): the filter type (e.g. "Name")
        - row (int): the row to place the filter input on
        - column (int): the column to place the filter input on
        - autofill (list): the list of autofill options for the entry box
        - pady (int): the vertical padding to apply to the filter input
        """

        filter_label = ctk.CTkLabel(frame,text=f"FILTER {label_text.title()}")
        filter_label.grid(row=row,column=column,sticky="nw",pady=pady,padx=(15,10))

        entry_tracker = tk.StringVar()
        entry_tracker.trace("w", lambda name, index, mode, sv=entry_tracker: self.entry_filter_callback(entry_tracker, type))
        filter_entry = dropdown_autocomplete.Autocomplete(frame,options=autofill,func="contains",hitlimit=5,state="normal",placeholder_text="",textvariable=entry_tracker)
        filter_entry.activate()
        
        return filter_label,filter_entry


    def plot_selected_items(self,event=None):
        """
        Plot the selected PastPaper objects on a line graph. The x-axis is the completed date, and the y-axis are the percentages of each past paper
        """

        # populate a dictionary with the core data required to plot the selected PastPaper objects
        plot_df_dict = {"Name":[],"Completed Date":[],"Percentage":[],"Grade":[]}
        for selected_item in self.treeview_obj.tv_obj.selection():
            paper_obj = self.treeview_obj.get_data()[selected_item].linked_object
            if paper_obj.get_completed_date_valid() and (paper_obj.get_percentage() != 0 and paper_obj.get_percentage() != -1):
                plot_df_dict["Name"].append(paper_obj.get_name())
                plot_df_dict["Completed Date"].append(paper_obj.get_completed_date_datetime())
                plot_df_dict["Percentage"].append(round(paper_obj.get_percentage()*100))
                plot_df_dict["Grade"].append(paper_obj.get_grade())

        # create a dataframe from the dictionary and sort by completed date
        plot_df = pd.DataFrame(plot_df_dict)
        plot_df['Completed Date'] = pd.to_datetime(plot_df['Completed Date']).dt.date
        plot_df.sort_values(by='Completed Date', inplace=True)
        # plot the dataframe
        fig = px.line(plot_df, x="Completed Date", y="Percentage",hover_name="Name", text="Name", markers=True)
        fig.update_layout(yaxis_range=[0,100])
        fig.update_layout(xaxis=dict(tickformat="%d/%m/%Y"))
        fig.update_traces(textposition="bottom right")
        fig.show()
    
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

    def make_grid_filters(self,size_level):
        rc=0 # row counter
        cc=0 # column counter
        c_mod=2
        r_mod=4
        if size_level <=2:
            r_mod=10000
            self.colconfig(self.filter_inner_frame,0,1,1)
            self.colconfig(self.filter_inner_frame,2,7,0)
        elif size_level <=4:
            r_mod=4
            self.colconfig(self.filter_inner_frame,0,3,1)
            self.colconfig(self.filter_inner_frame,4,7,0)
        else:
            r_mod=2
            self.colconfig(self.filter_inner_frame,0,7,1)
        for item in self.filter_widgets:
            rc,cc=CommonFunctions.grid_apply(item[0],rc=rc,cc=cc,c_mod=c_mod,r_mod=r_mod,sticky="nw",padx=2,pady=2)
            rc,cc=CommonFunctions.grid_apply(item[1],rc=rc,cc=cc,c_mod=c_mod,r_mod=r_mod,sticky="nw",padx=2,pady=2)

    def make_grid_buttons(self,size_level):
        rc=0 # row counter
        cc=0 # column counter
        c_mod=100 # column modulus
        r_mod=1 # row modulus

        # set different modulus for a narrower screen
        if size_level <=2:
            r_mod=100
            c_mod=1

        rc,cc=CommonFunctions.grid_apply(self.plot_button,rc=rc,cc=cc,c_mod=c_mod,r_mod=r_mod,sticky="ew",padx=10,pady=15)
        rc,cc=CommonFunctions.grid_apply(self.delete_button,rc=rc,cc=cc,c_mod=c_mod,r_mod=r_mod,sticky="ew",padx=10,pady=15)


    def make_grid(self,size_level):
        """
        Resize MainPage event (called when the window is resized from the mainline)
        """

        # resize treeview (must happen when size_level <= 2 - see mainline for the meaning of this)
        # apply_width state (values True and False) specify two different states for the treeview (one for wide screen and one for narrow screen).
        # the actions of such width states are defined when instantiating the treeview object
        if size_level <=2:self.treeview_obj.apply_width_state(True)
        else:self.treeview_obj.apply_width_state(False)
        
        self.make_grid_filters(size_level=size_level)
        self.make_grid_buttons(size_level=size_level)

