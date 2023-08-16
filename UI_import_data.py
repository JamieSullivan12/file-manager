import customtkinter as ctk
import tkinter as tk
import re,os
import treeview
import dropdown_autocomplete
import progressbar


class ImportDataPage(ctk.CTkScrollableFrame):


    def findall_regex(self, search_pattern, filepath, filename, location_rule="anywhere", custom_key={}):
        """
        Find all occurrences of a regular expression pattern in a file path or filename.

        Args:
            search_pattern (str): Regular expression pattern to search for.
            filepath (str): File path to search in.
            filename (str): File name to search in.
            location_rule (str): Location rule for searching ("filename", "filepath", "both", "anywhere").
            custom_key (dict): Custom key-value mapping for search results. The key is the search result, and the value is the custom key to be returned instead of the search result.

        Returns:
            list: List of search results based on the location rule and custom key.
        """

        found_filename=False
        found_filepath=False
        regex_result_filename=[]
        regex_result_path=[]

        # Use regex to find a search pattern in the filename and/or filepath (depending on location_rule)
        if location_rule == "filename" or location_rule == "anywhere" or location_rule == "both":
            found_filename=True
            regex_result_filename = re.findall(search_pattern,filename,re.IGNORECASE)
        if location_rule == "filepath" or location_rule == "anywhere" or location_rule == "both":
            found_filepath=True
            regex_result_path = re.findall(search_pattern,filepath,re.IGNORECASE)
        
        # Satisfy th restriction set by location_rule:
        # - If location_rule is "filename" or "filepath", return the search result from the corresponding location.
        # - If location_rule is "both", the regex pattern must be found in both locations.
        # - If location_rule is "anywhere", the regex pattern may be found in either one or the other (or both) locations.
        if location_rule == "both" and (not found_filename or not found_filepath):
            regex_result = []
        elif location_rule == "both" or location_rule == "anywhere":
            regex_result = regex_result_filename + regex_result_path
        elif location_rule == "filename":
            regex_result = regex_result_filename
        elif location_rule == "filepath":
            regex_result = regex_result_path
        else:
            regex_result = regex_result_filename + regex_result_path
        
        # Overwrite the search result with a custom key if it exists
        custom_key_casefold={}
        for key in custom_key:
            custom_key_casefold[key.casefold()]=custom_key[key]

        # Return the search result
        if len(regex_result) > 0: 
            if custom_key != {} and regex_result[-1].casefold() in custom_key_casefold:
                regex_result = custom_key_casefold[regex_result[-1].casefold()]
            else:
                regex_result=regex_result[-1]
            return regex_result
        else: return None

    def identify_paper_type(self, search_string):
        """
        Identify the type of paper document based on search string.

        Args:
            search_string (str): Search string to identify document type.

        Returns:
            tuple: Document type and unique identifier.
        """

        # Default document is attachment if not identified as question paper or mark scheme.
        document_type="attachment"
        document_suffix = []

        # If no identifiers are specified, assume document is question paper.
        if len(self.course_values.identifiers_questionpaper)==0:document_type="questionpaper"
        # If no identifiers are specified, assume document is mark scheme.
        if len(self.course_values.identifiers_markscheme)==0:document_type="markscheme"
        # If no identifiers are specified, assume document is attachment.
        if len(self.course_values.identifiers_attachment)==0:document_type="attachment"


        # Iterate through all the identifiers and check if they are in the search string.
        for identifier in self.course_values.identifiers_questionpaper:
            if identifier.casefold() in search_string.casefold():
                document_type = "questionpaper"
                break

        # Iterate through all the identifiers and check if they are in the search string.
        for identifier in self.course_values.identifiers_markscheme:
            if identifier.casefold() in search_string.casefold():
                document_type = "markscheme"
                break

        # Iterate through all the identifiers and check if they are in the search string.
        for identifier in self.course_values.identifiers_attachment:
            if identifier.casefold() in search_string.casefold() and not identifier.casefold() == "":
                document_type="attachment"
                break
        
        # Find all suffixes relevant to the determined document type.
        # A suffix are appendices to the document name (such as a specified language etc. which are useful for ident
        # ifying the document if there are more than one).
        if document_type == "questionpaper":
            for suffix in self.course_values.suffix_questionpaper:
                if suffix.casefold() in search_string.casefold():
                    document_suffix.append(suffix)
        if document_type == "markscheme":
            for suffix in self.course_values.suffix_markscheme:
                if suffix.casefold() in search_string.casefold():
                    document_suffix.append(suffix)
        if document_type == "attachment":
            for suffix in self.course_values.suffix_attachment:
                if suffix.casefold() in search_string.casefold():
                    document_suffix.append(suffix)

        return document_type," ".join(document_suffix)

    def reset_imported(self):
        """
        Reset the imported data and UI elements.
        """
        self.treeview_obj.remove_all()
        self.browse_button.grid(row=1,column=0,sticky="new")
        self.save_imported_frame.grid_forget()

    def reset_treeview(self):
        """
        Reset the treeview UI element.
        """
        self.treeview_obj.grid_forget()
        del self.treeview_obj
        self.setup_treeview_frame()

    def import_command(self):
        """
        Import selected paper objects into the database.
        """
        subject = str(self.subject_code_entry.get())

        # Setup progress bar
        progressbar_import = progressbar.CustomProgressBar(self.save_imported_frame,text="Importing...",total_number=len(self.treeview_obj.get_data()))
        progressbar_import.grid(row=2,column=0,columnspan=2,sticky="new",padx=15,pady=15)
        self.save_imported_frame.update()

        if self.treeview_obj.get_data() > 600:
            if tk.messagebox.askyesno("Warning","You are about to import a large number of documents. This may take a long time. Are you sure you want to continue?"):
                pass

                # Iterate through all the data in the treeview
                counter = 0
                treeview_data = self.treeview_obj.get_data()
                for data_line in self.treeview_obj.get_data():
                    counter += 1
                    progressbar_import.update_progress_bar(counter)
                    # If the row is level 0 (i.e. a paper object) then import it into the database
                    # Note all documents attached to the paper object will be treeview level 1, so they will be imported automatically
                    # as they are attached to the paper object
                    if treeview_data[data_line].level==0:
                        treeview_data[data_line].linked_object.set_subject(subject)
                        self.mainline_obj.db_object.add_past_paper(treeview_data[data_line].linked_object)
                        treeview_data[data_line].linked_object.update_to_database(copy_documents=True)
                        
                self.mainline_obj.frames["MainPage"].populate_treeview()

                # Reset the treeview and show the browse button
                self.browse_button.grid(row=1,column=0,sticky="new")
                self.save_imported_frame.grid_forget()
                progressbar_import.destroy()
                self.reset_treeview()
            else:
                return
            
    def make_grid(self,critical):
        pass

    def set_itemarkscheme(self, value, setter):
        """
        Set the value using a setter function if the value is not None.

        Args:
            value: Value to set.
            setter: Setter function to call.
        """
        if value is not None:
            setter(value)

    def cancel(self):
        self.cancel_browse=True
        self.reset_imported()

    def browse_command(self):
        """
        Browse and process files from a selected directory.
        """
        self.cancel_browse=False
        # Ask the user to select a directory
        path = tk.filedialog.askdirectory(title="Dialog box")

        # Hide the browse button and show the import frame
        self.browse_button.grid_forget()
        self.save_imported_frame.grid(row=1, column=0, sticky="new")

        # Create and configure the subject code entry widget
        self.subject_code_entry = dropdown_autocomplete.Autocomplete(
            self.save_imported_frame, options=list(self.mainline_obj.settings.subjects.values()),
            func="contains", placeholder_text="Subject"
        )
        self.subject_code_entry.grid(row=0, column=0, sticky="new", pady=10, padx=(10, 5))
        self.subject_code_entry.activate()

        self.cancel_button=ctk.CTkButton(self.save_imported_frame,text="Cancel",command=self.cancel)
        self.cancel_button.grid(row=0,column=1,sticky="new",pady=10,padx=(5,10))

        # Initialize variables for processing files
        paper_objects_dict = {}
        total = 0

        # Count the total number of files in the selected directory
        for root, dirs, files in os.walk(path):
            total += len(files)

        # Prevent program crash due to too large import
        if total > 600:
            tk.messagebox.showerror("Error", f"Too many files to import ({total}, maximum 500). Please select a smaller directory.")
            self.reset_imported()
            return

        # Create and display a progress bar
        progressbar_toplevel = progressbar.CustomProgressBar(
            self.save_imported_frame, text=f"Importing... (1/{total})", total_number=total
        )
        progressbar_toplevel.grid(row=2, column=0, columnspan=2, padx=15, pady=15, sticky="nw")

        # Initialize counters
        counter = 0

        # Iterate through files in the selected directory
        for root, dirs, files in os.walk(path):
            for filename in files:
                if self.cancel_browse:
                    return
                # Update progress bar
                progressbar_toplevel.update_progress_bar(counter)
                progressbar_toplevel.update_label(f"Importing... ({counter + 1}/{total})")
                counter += 1

                # Create the full search string for the file
                search_string = os.path.join(root, filename)

                # Apply regular expressions to extract information from the filename
                year_regex_result = self.findall_regex(
                    self.course_values.regex_year, filepath=root, filename=filename,
                    location_rule=self.course_values.find_year
                )
                session_regex_result = self.findall_regex(
                    self.course_values.regex_session, filepath=root, filename=filename,
                    location_rule=self.course_values.find_session, custom_key=self.course_values.key_session
                )
                timezone_regex_result = self.findall_regex(
                    self.course_values.regex_timezone, filepath=root, filename=filename,
                    location_rule=self.course_values.find_timezone, custom_key=self.course_values.key_timezone
                )
                paper_regex_result = self.findall_regex(
                    self.course_values.regex_paper, filepath=root, filename=filename,
                    location_rule=self.course_values.find_paper, custom_key=self.course_values.key_paper
                )
                level_regex_result = self.findall_regex(
                    self.course_values.regex_level, filepath=root, filename=filename,
                    location_rule=self.course_values.find_level, custom_key=self.course_values.key_level
                )

                # Identify the document type and unique identifier
                documenttype_identifier, document_suffix = self.identify_paper_type(filename)

                # Apply regular expression to extract additional information
                other_regex_result = self.findall_regex(
                    self.course_values.regex_other, filepath=root, filename=filename,
                    location_rule="anywhere"
                )

                # Create a new PastPaper object
                new_paper_obj = self.mainline_obj.db_object.create_new_row(temporary=True)

                # Set attributes using the extracted information
                self.set_itemarkscheme(year_regex_result, new_paper_obj.set_year)
                self.set_itemarkscheme(session_regex_result, new_paper_obj.set_session)
                self.set_itemarkscheme(timezone_regex_result, new_paper_obj.set_timezone)
                self.set_itemarkscheme(paper_regex_result, new_paper_obj.set_paper)
                self.set_itemarkscheme(level_regex_result, new_paper_obj.set_level)

                # Update the object's values
                new_paper_obj.update_values()
                name = new_paper_obj.generate_name()

                # Handle duplicate paper names
                if name not in paper_objects_dict:
                    paper_objects_dict[name] = new_paper_obj
                else:
                    del new_paper_obj
                    new_paper_obj = paper_objects_dict[name]

                # Create and insert new documents into the object based on the document type
                if documenttype_identifier == "questionpaper":
                    new_paper_obj.create_insert_new_document(
                        "questionpaper", override_path=search_string, suffix=document_suffix
                    )
                elif documenttype_identifier == "markscheme":
                    new_paper_obj.create_insert_new_document(
                        "markscheme", override_path=search_string, suffix=document_suffix
                    )
                elif documenttype_identifier == "attachment":
                    new_paper_obj.create_insert_new_document(
                        "attachment", override_path=search_string, suffix=document_suffix
                    )

        id = 0
        treeview_counter = 0
        for new_item_code in paper_objects_dict:
            new_item = paper_objects_dict[new_item_code]
            new_tv_row = self.treeview_obj.insert_element(
                new_item, [], text=new_item_code, iid=new_item_code, message=["database_entry"]
            )
            for questionpaper_id in new_item.get_questionpaper_documents():
                questionpaper_obj=new_item.get_questionpaper_documents()[questionpaper_id]
                id += 1
                self.treeview_obj.insert_element(questionpaper_obj,[],text=questionpaper_obj.get_filename(),childobject=True,childobject_parent=new_tv_row,childobject_level=1,remove_function=self.treeview_remove_child,add_function=self.treeview_add_child,double_clicked_function=self.document_double_clicked_function)
            for markscheme_id in new_item.get_markscheme_documents():
                markscheme_obj=new_item.get_markscheme_documents()[markscheme_id]
                id += 1
                self.treeview_obj.insert_element(markscheme_obj,[],text=markscheme_obj.get_filename(),childobject=True,childobject_parent=new_tv_row,childobject_level=1,remove_function=self.treeview_remove_child,add_function=self.treeview_add_child,double_clicked_function=self.document_double_clicked_function)
            for attachment_id in new_item.get_attachment_documents():
                attachment_obj=new_item.get_attachment_documents()[attachment_id]
                id += 1
                self.treeview_obj.insert_element(attachment_obj,[],text=attachment_obj.get_filename(),childobject=True,childobject_parent=new_tv_row,childobject_level=1,remove_function=self.treeview_remove_child,add_function=self.treeview_add_child,double_clicked_function=self.document_double_clicked_function)
        
            treeview_counter += 1

        # Clean up progress bar
        print("DESTROY")
        progressbar_toplevel.destroy()

    def treeview_remove_child(self, child=None):
        """
        Remove a child document from the treeview and primary storage.

        Args:
            child: Child item to remove.
        """
        child.linked_object.remove_document(keep_file=True)

    def treeview_add_child(self, child=None, parent=None):
        """
        Add a child document to the treeview and primary storage.

        Args:
            child: Child item to add.
            parent: Parent item to associate with.
        """
        document_type = child.linked_object.get_document_type()
        filepath = child.linked_object.get_full_filepath()
        new_child_linked_object = parent.linked_object.create_insert_new_document(document_type, override_path=filepath, suffix="")
        child.linked_object = new_child_linked_object

    def document_double_clicked_function(self, clicked_item_data):
        """
        Function to handle double-clicking a document item in the treeview.

        Args:
            clicked_item_data: Data of the clicked item.
        """
        clicked_object = clicked_item_data.linked_object
        try:
            clicked_object.open_document()
        except Exception as e:
            pass


    def setup_treeview_frame(self):
        """
        Set up the treeview UI element.
        """
        self.treeview_obj = treeview.TreeView(
            self.treeview_bubble_frame, {}, height=15, show_tree=True, show_tree_heading="Documents",
            show_tree_width=0.2, show_editing_buttons=True, double_click_function=self.document_double_clicked_function
        )
        self.treeview_obj.grid(row=0, column=0, sticky="nsew")
    
    def setup_main_bubble_frame(self):
        """
        Set up the main bubble frame UI element.
        """

        self.heading_label = ctk.CTkLabel(self.main_bubble_frame,text="Import data from a directory",font=(None,18))
        self.heading_label.grid(row=0,column=0,sticky="nw",padx=10,pady=(5,0))

        self.browse_button = ctk.CTkButton(self.main_bubble_frame,text="Browse directory",command=self.browse_command)
        self.browse_button.grid(row=1,column=0,sticky="new",padx=10,pady=10)

        self.save_imported_frame = ctk.CTkFrame(self.main_bubble_frame,fg_color="transparent")
        self.save_imported_button = ctk.CTkButton(self.save_imported_frame,text="Import",command=self.import_command)
        self.save_imported_button.grid(row=1,column=0,columnspan=2,sticky="new",padx=(10,10),pady=(0,15))
        self.reset_imported_button = ctk.CTkButton(self.save_imported_frame,text="Reset",command=self.reset_imported)
        self.reset_imported_button.grid(row=0,column=1,sticky="new",padx=(10,10),pady=10)
        
        self.save_imported_frame.columnconfigure(0,weight=1)
        self.save_imported_frame.columnconfigure(1,weight=1)

    def __init__(self, mainline_obj, scrollable_frame, grid_preload=False):
        super().__init__(scrollable_frame)

        # Reference to the mainline_obj to access shared data and methods
        self.course_values = mainline_obj.get_course_values()
        self.mainline_obj = mainline_obj

        self.bubble_padx = 20
        self.bubble_pady = 10
        self.grid_columnconfigure(0, weight=1)

        self.main_bubble_frame = ctk.CTkFrame(
            self, corner_radius=15, fg_color=self.mainline_obj.colors.bubble_background
        )
        self.main_bubble_frame.grid(
            row=1, column=0, sticky="new", padx=self.bubble_padx, pady=self.bubble_pady
        )
        self.main_bubble_frame.columnconfigure(0, weight=1)

        self.setup_main_bubble_frame()

        self.treeview_bubble_frame = ctk.CTkFrame(
            self, corner_radius=15, fg_color=self.mainline_obj.colors.bubble_background
        )
        self.treeview_bubble_frame.grid(
            row=2, column=0, sticky="new", padx=self.bubble_padx, pady=self.bubble_pady
        )
        self.treeview_bubble_frame.columnconfigure(0, weight=1)
        self.setup_treeview_frame()