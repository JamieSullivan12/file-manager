import customtkinter as ctk
import tkinter as tk
import values_and_rules
import re,os
import treeview
from database import PaperObject
import subprocess


class ImportDataPage(ctk.CTkFrame):

    class NewPaperObj(PaperObject):
        def __init__(self,db,mainline_obj):
            super().__init__(db,mainline_obj)

    def findall_regex(self,search_pattern,search_string):
        regex_result = re.findall(search_pattern,search_string,re.IGNORECASE)
        if len(regex_result) > 0: return regex_result[-1]
        else: return None

    def identify_paper_type(self,regex_patterns,search_string):
        document_type = "oa"
        unique_identifier = ""
        if regex_patterns["questionpaper_identifier"].lower() in search_string.lower():
            document_type = "qp"
        if regex_patterns["markscheme_identifier"].lower() in search_string.lower():
            document_type = "ms"
        for identifier in regex_patterns["otherattachments_identifier"]:
            if identifier.lower() in search_string.lower():
                document_type="oa"
                unique_identifier = identifier
        return document_type,unique_identifier

    def reset_imported(self):
        self.browse_button.grid(row=1,column=0,sticky="new")
        self.save_imported_frame.grid_forget()

    def reset_treeview(self):
        self.treeview_obj.grid_forget()
        del self.treeview_obj
        self.setup_treeview_frame()

    def import_command(self):
        subject = str(self.subject_code_entry.get())
        self.browse_button.grid(row=1,column=0,sticky="new")
        self.save_imported_frame.grid_forget()
        
        treeview_data = self.treeview_obj.get_data()
        for data_line in self.treeview_obj.get_data():
            if treeview_data[data_line]["message"][0]=="database_entry":
                treeview_data[data_line]["linked_object"].set_subject(subject)
                self.mainline_obj.db_object.save_row(self.treeview_obj.get_data()[data_line]["linked_object"],copy=True,override_duplicate_warning=True)
                self.mainline_obj.frames["MainPage"].populate_treeview()

        self.reset_treeview()

    def browse_command(self):

        def set_items(value,setter):
            if value != None:
                setter(value)
            else:
                pass
            

        path = tk.filedialog.askdirectory(title="Dialog box")
        regex_patterns = values_and_rules.get_regex_patterns(self.mainline_obj.settings.course_type)


        self.browse_button.grid_forget()
        self.save_imported_frame.grid(row=1,column=0,sticky="new")

        paper_objects_dict = {}

        foldername = os.path.basename(path)
        for root, dirs, files in os.walk(path):
            for filename in files:
                new_paper_obj=self.mainline_obj.db_object.create_new_row()
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

                set_items(year_regex_result,new_paper_obj.set_year)
                set_items(session_regex_result,new_paper_obj.set_session)
                set_items(timezone_regex_result,new_paper_obj.set_timezone)
                set_items(paper_regex_result,new_paper_obj.set_paper)
                set_items(level_regex_result,new_paper_obj.set_level)


                new_paper_obj.generate_name()
                name = new_paper_obj.get_name()

                if name not in paper_objects_dict:
                    paper_objects_dict[name]=new_paper_obj
                else:
                    del new_paper_obj
                    new_paper_obj = paper_objects_dict[name]
                
                
                if documenttype_identifier=="qp":
                    new_paper_obj.set_original_path(search_string)
                elif documenttype_identifier=="ms":
                    new_paper_obj.set_markscheme_path(search_string)
                elif documenttype_identifier=="oa":
                    new_paper_obj.set_otherattachments_path(search_string,unique_identifier=unique_identifier)


        id=0

        treeview_counter = 0
        for new_item_code in paper_objects_dict:
            new_item = paper_objects_dict[new_item_code]
            self.treeview_obj.insert_element(new_item,[],text=new_item_code,iid=new_item_code,message=["database_entry"])
            #new_item.get_year(),new_item.get_session(),new_item.get_timezone(),new_item.get_paper(),new_item.get_level()
            for questionpaper in new_item.get_original():
                id += 1
                self.treeview_obj.insert_element(new_item,[],text=os.path.basename(questionpaper["path"]),childobject=True,childobject_parent_id=new_item_code,childobject_level=1,message=["pdf",questionpaper["path"],"qp"])
            for markscheme in new_item.get_markscheme():
                id += 1
                self.treeview_obj.insert_element(new_item,[],os.path.basename(markscheme["path"]),childobject=True,childobject_parent_id=new_item_code,childobject_level=1,message=["pdf",markscheme["path"],"ms"])
            for otherattachments in new_item.get_otherattachments():
                id += 1
                self.treeview_obj.insert_element(new_item,[],os.path.basename(otherattachments["path"]),childobject=True,childobject_parent_id=new_item_code,childobject_level=1,message=["pdf",otherattachments["path"],"oa"])
            
            
            treeview_counter += 1

    def treeview_remove_child(self,child=None):
        document_type = child["message"][2]
        paper_object = child["linked_object"]
        path = child["message"][1]
        if document_type == "qp":
            paper_object.remove_original_path(path)
        if document_type == "ms":
            paper_object.remove_markscheme_path(path)
        if document_type == "oa":
            paper_object.remove_otherattachments_path(path)
        

    def treeview_add_child(self,child=None,parent=None):
        document_type = child["message"][2]
        path = child["message"][1]
        
        parent_paper_obj = parent["linked_object"]
        if document_type == "qp":
            parent_paper_obj.set_original_path(path)
        if document_type == "ms":
            parent_paper_obj.set_markscheme_path(path)
        if document_type == "oa":
            parent_paper_obj.set_otherattachments_path(path)


    def document_double_clicked_function(self,clicked_item_data):
        if clicked_item_data["message"][0]=="pdf":
            path = clicked_item_data["message"][1]
            if os.path.isfile(path):
                subprocess.Popen([path],shell=True)


    def tree_double_clicked(self,event=None):
        pass

    def populate_treeview(self):
        self.treeview_obj.remove_all()


    def setup_treeview_frame(self):
        self.treeview_obj = treeview.TreeView(self.mainline_obj,self.treeview_bubble_frame,[],row=1,column=0,columnspan=1,double_click_function=self.document_double_clicked_function,height=15,show_tree=True,show_tree_heading="Documents",show_tree_width=0.2,show_editing_buttons=True,child_remove_action=self.treeview_remove_child,child_add_action=self.treeview_add_child)

    def setup_main_bubble_frame(self):
        self.heading_label = ctk.CTkLabel(self.main_bubble_frame,text="Import data from a directory",font=(None,18))
        self.heading_label.grid(row=0,column=0,sticky="nw")

        self.browse_button = ctk.CTkButton(self.main_bubble_frame,text="Browse directory",command=self.browse_command)
        self.browse_button.grid(row=1,column=0,sticky="new")





        self.save_imported_frame = ctk.CTkFrame(self.main_bubble_frame,fg_color="transparent")
        self.subject_code_entry = ctk.CTkEntry(self.save_imported_frame,placeholder_text="Subject")
        self.subject_code_entry.grid(row=0,column=0,sticky="new")
        
        self.save_imported_button = ctk.CTkButton(self.save_imported_frame,text="Import",command=self.import_command)
        self.save_imported_button.grid(row=1,column=0,sticky="new")
        self.reset_imported_button = ctk.CTkButton(self.save_imported_frame,text="Reset",command=self.reset_imported)
        self.reset_imported_button.grid(row=2,column=1,sticky="new")
        self.save_imported_frame.columnconfigure(0,weight=1)
        self.save_imported_frame.columnconfigure(1,weight=1)
        self.save_imported_frame.columnconfigure(2,weight=1)

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