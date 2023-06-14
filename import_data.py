import customtkinter as ctk
import tkinter as tk
import values_and_rules
import re,os
import treeview
import subprocess
import autocomplete_with_dropdown
import progressbar


class ImportDataPage(ctk.CTkScrollableFrame):


    def findall_regex(self,search_pattern,search_string):
        regex_result = re.findall(search_pattern,search_string,re.IGNORECASE)
        if len(regex_result) > 0: return regex_result[-1]
        else: return None

    def identify_paper_type(self,regex_patterns,search_string):
        document_type="attachment"
        unique_identifier = []
        if regex_patterns["questionpaper_identifier"].lower() in search_string.lower():
            document_type = "questionpaper"

        if regex_patterns["markscheme_identifier"].lower() in search_string.lower():
            document_type = "markscheme"

        for identifier in regex_patterns["attachment_identifier"]:
            if identifier.lower() in search_string.lower():
                document_type="attachment"
                break
        

        if document_type == "questionpaper":
            for suffix in regex_patterns["questionpaper_suffix"]:
                if suffix.lower() in search_string.lower():
                    unique_identifier.append(suffix)

        if document_type == "markscheme":
            for suffix in regex_patterns["markscheme_suffix"]:
                if suffix.lower() in search_string.lower():
                    unique_identifier.append(suffix)

        if document_type == "attachment":
            for suffix in regex_patterns["attachment_suffix"]:
                if suffix.lower() in search_string.lower():
                    unique_identifier.append(suffix)
        return document_type," ".join(unique_identifier)

    def reset_imported(self):
        self.treeview_obj.remove_all()
        self.browse_button.grid(row=1,column=0,sticky="new")
        self.save_imported_frame.grid_forget()

    def reset_treeview(self):
        self.treeview_obj.grid_forget()
        del self.treeview_obj
        self.setup_treeview_frame()

    def import_command(self):
        """
        Insert all selected paper objects into the database
        """
        subject = str(self.subject_code_entry.get())
        self.browse_button.grid(row=1,column=0,sticky="new")
        self.save_imported_frame.grid_forget()
        
        treeview_data = self.treeview_obj.get_data()
        for data_line in self.treeview_obj.get_data():
            if treeview_data[data_line]["childobject"]==False:
                treeview_data[data_line]["linked_object"].set_subject(subject)
                self.mainline_obj.db_object.save_row(treeview_data[data_line]["linked_object"],copy=True)
        self.mainline_obj.frames["MainPage"].populate_treeview()

        self.reset_treeview()

    def make_grid(self,critical):
        pass

    def browse_command(self):

        def set_itemarkscheme(value,setter):
            if value != None:
                setter(value)
            else:
                pass
            

        path = tk.filedialog.askdirectory(title="Dialog box")
        regex_patterns = values_and_rules.get_regex_patterns(self.mainline_obj.settings.course_type)


        self.browse_button.grid_forget()
        self.save_imported_frame.grid(row=1,column=0,sticky="new")

        paper_objects_dict = {}

        total = 0
        for root, dirs, files in os.walk(path):
            total += len(files)

        progressbar_toplevel = progressbar.ProgressBar(self.treeview_obj,total)
        counter=0
        foldername = os.path.basename(path)
        for root, dirs, files in os.walk(path):
            for filename in files:
                progressbar_toplevel.update_progress_bar(counter)
                counter+=1
                search_string =os.path.join(root,filename)
                
                year_regex_result = self.findall_regex(regex_patterns["year_regex"],search_string)

                session_regex_result = self.findall_regex(regex_patterns["session_regex"],search_string)
                
                timezone_regex_result = self.findall_regex(regex_patterns["timezone_regex"],search_string)
                
                paper_regex_result = self.findall_regex(regex_patterns["paper_regex"],search_string)
                
                subject_regex_result = self.findall_regex(regex_patterns["subject_regex"],search_string)
                
                level_regex_result = self.findall_regex(regex_patterns["level_regex"],search_string)

                documenttype_identifier,unique_identifier = self.identify_paper_type(regex_patterns,filename)

                other_regex_result = self.findall_regex(regex_patterns["other_regex"],search_string)
                
                new_paper_obj = self.mainline_obj.db_object.create_new_row()

                set_itemarkscheme(year_regex_result,new_paper_obj.set_year)
                set_itemarkscheme(session_regex_result,new_paper_obj.set_session)
                set_itemarkscheme(timezone_regex_result,new_paper_obj.set_timezone)
                set_itemarkscheme(paper_regex_result,new_paper_obj.set_paper)
                set_itemarkscheme(level_regex_result,new_paper_obj.set_level)


                name=new_paper_obj.generate_name()
                print("GENERATE NAME",name)

                if name not in paper_objects_dict:
                    paper_objects_dict[name]=new_paper_obj
                else:
                    del new_paper_obj
                    new_paper_obj = paper_objects_dict[name]
                
                

                if documenttype_identifier=="questionpaper":
                    #new_paper_obj.set_original_path(search_string)
                    new_paper_obj.create_insert_new_document("questionpaper",override_path=search_string,suffix=unique_identifier,do_not_update_object=True)

                elif documenttype_identifier=="markscheme":
                    #new_paper_obj.set_markscheme_path(search_string)
                    new_paper_obj.create_insert_new_document("markscheme",override_path=search_string,suffix=unique_identifier,do_not_update_object=True)

                elif documenttype_identifier=="attachment":
                    #new_paper_obj.set_otherattachments_path(search_string,unique_identifier=unique_identifier)
                    new_paper_obj.create_insert_new_document("attachment",override_path=search_string,suffix=unique_identifier,do_not_update_object=True)


        id=0

        treeview_counter = 0
        print(paper_objects_dict)
        for new_item_code in paper_objects_dict:
            new_item = paper_objects_dict[new_item_code]
            new_tv_row = self.treeview_obj.insert_element(new_item,[],text=new_item_code,iid=new_item_code,message=["database_entry"])
            #new_item.get_year(),new_item.get_session(),new_item.get_timezone(),new_item.get_paper(),new_item.get_level()
            for questionpaper_id in new_item.get_questionpaper_documents():
                questionpaper_obj=new_item.get_questionpaper_documents()[questionpaper_id]
                id += 1
                self.treeview_obj.insert_element(questionpaper_obj,[],text=os.path.basename(questionpaper_obj.get_current_file_path()),childobject=True,childobject_parent=new_tv_row,childobject_level=1,remove_function=self.treeview_remove_child,add_function=self.treeview_add_child,double_clicked_function=self.document_double_clicked_function)
            for markscheme_id in new_item.get_markscheme_documents():
                markscheme_obj=new_item.get_markscheme_documents()[markscheme_id]
                id += 1
                self.treeview_obj.insert_element(markscheme_obj,[],text=os.path.basename(markscheme_obj.get_current_file_path()),childobject=True,childobject_parent=new_tv_row,childobject_level=1,remove_function=self.treeview_remove_child,add_function=self.treeview_add_child,double_clicked_function=self.document_double_clicked_function)
            for attachment_id in new_item.get_attachment_documents():
                attachment_obj=new_item.get_attachment_documents()[attachment_id]
                id += 1
                self.treeview_obj.insert_element(attachment_obj,[],text=os.path.basename(attachment_obj.get_current_file_path()),childobject=True,childobject_parent=new_tv_row,childobject_level=1,remove_function=self.treeview_remove_child,add_function=self.treeview_add_child,double_clicked_function=self.document_double_clicked_function)
            
            
            treeview_counter += 1
        progressbar_toplevel.destroy()
    def treeview_remove_child(self,child=None):
        child.linked_object.remove_document_from_dict()

    def treeview_add_child(self,treeview_row_obj,child=None,parent=None):
        document_type = child.linked_object.get_file_type()
        path = child.linked_object.get_current_file_path()
        new_child_linked_object=parent.linked_object.create_insert_new_document(document_type,override_path=path,suffix=child["linked_object"].get_suffix(),do_not_update_object=True)
        child.linked_object=new_child_linked_object

    def document_double_clicked_function(self,clicked_item_data):
        path = clicked_item_data["linked_object"].get_current_file_path()
        if os.path.isfile(path):
            subprocess.Popen([path],shell=True)



    def setup_treeview_frame(self):
        self.treeview_obj = treeview.TreeView(self.treeview_bubble_frame,{},height=15,show_tree=True,show_tree_heading="Documents",show_tree_width=0.2,show_editing_buttons=True)
        self.treeview_obj.grid(row=0,column=0,sticky="nsew")
    def setup_main_bubble_frame(self):
        self.heading_label = ctk.CTkLabel(self.main_bubble_frame,text="Import data from a directory",font=(None,18))
        self.heading_label.grid(row=0,column=0,sticky="nw",padx=10,pady=(5,0))

        self.browse_button = ctk.CTkButton(self.main_bubble_frame,text="Browse directory",command=self.browse_command)
        self.browse_button.grid(row=1,column=0,sticky="new",padx=10,pady=10)





        self.save_imported_frame = ctk.CTkFrame(self.main_bubble_frame,fg_color="transparent")

        self.subject_code_entry = autocomplete_with_dropdown.Autocomplete(self.save_imported_frame,options=list(self.mainline_obj.settings.subjects.values()),func="contains",placeholder_text="Subject")

        self.subject_code_entry.grid(row=0,column=0,sticky="new",pady=10,padx=(10,5))
        


        self.save_imported_button = ctk.CTkButton(self.save_imported_frame,text="Import",command=self.import_command)
        self.save_imported_button.grid(row=1,column=0,columnspan=2,sticky="new",padx=(10,10))
        self.reset_imported_button = ctk.CTkButton(self.save_imported_frame,text="Reset",command=self.reset_imported)
        self.reset_imported_button.grid(row=0,column=1,sticky="new",padx=(10,10),pady=10)
        self.save_imported_frame.columnconfigure(0,weight=1)
        self.save_imported_frame.columnconfigure(1,weight=1)

    def __init__(self, mainline_obj, scrollable_frame, grid_preload=  False):
        super().__init__(scrollable_frame)
        self.terminology = values_and_rules.get_terminology(mainline_obj.settings.get_course_type())
        self.mainline_obj=mainline_obj

        self.bubble_padx=20
        self.bubble_pady=10

        self.grid_columnconfigure(0, weight=1)

        self.main_bubble_frame = ctk.CTkFrame(self,corner_radius=15,fg_color=self.mainline_obj.colors.bubble_background)
        self.main_bubble_frame.grid(row=1,column=0,sticky="new",padx=self.bubble_padx,pady=self.bubble_pady)
        self.main_bubble_frame.columnconfigure(0,weight=1)

        self.setup_main_bubble_frame()
        
        self.treeview_bubble_frame = ctk.CTkFrame(self,corner_radius=15,fg_color=self.mainline_obj.colors.bubble_background)
        self.treeview_bubble_frame.grid(row=2,column=0,sticky="new",padx=self.bubble_padx,pady=self.bubble_pady)
        self.treeview_bubble_frame.columnconfigure(0,weight=1)
        self.setup_treeview_frame()