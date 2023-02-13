import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class ReadPastPaperPopUp():

    def add_to_local_storage(self, event=None):

        excludes = self.exclude_code_entry.get().split(",")
        for i, item in enumerate(excludes):
            excludes[i].strip()

        self.subject_code = self.subject_code_entry.get()
        if not os.path.exists("Papers/" + self.subject_code):
            os.makedirs("Papers/" + self.subject_code)

        for item in self.metadata:

            if self.metadata[item]["valid"] == True:
                valid = True
                for exclusion in excludes:
                    if exclusion.lower() in self.metadata[item]["path"].lower():
                        valid = False

                if valid:
                    new_row=self.parent.db_object.create_new_row()
                                        
                    new_row.set_year(self.metadata[item]["year"])
                    new_row.set_session(self.metadata[item]["session"])
                    new_row.set_timezone(self.metadata[item]["timezone"])
                    new_row.set_paper(self.metadata[item]["paper"])
                    new_row.set_subject(self.subject_code)
                    new_row.set_level(self.metadata[item]["level"])
                    
                    exists, new_row = self.parent.db_object.check_row_exists(new_row)
                    #print(exists)
                    if self.metadata[item]["markscheme"] == "MS":
                        new_row.move_file_location("markscheme",self.metadata[item]["path"],copy=True, ignore_duplicate=True)
                    else:
                        new_row.move_file_location("original",self.metadata[item]["path"],copy=True, ignore_duplicate=True)
                    
                    #print("Added",new_row.get_name(),". Exists",str(exists),". Path",self.metadata[item]["path"])
                    if exists:
                        new_row.update_database()
                    else:
                        self.parent.db_object.save_row(new_row)
                    #file_name = f'Original-{self.metadata[item]["session"]}-TZ{self.metadata[item]["timezone"]}-P{self.metadata[item]["paper"]}-{self.subject_code}{self.metadata[item]["level"]}-{self.metadata[item]["markscheme"]}.pdf'
                    #shutil.copyfile(self.metadata[item]["path"],"Papers/" + self.subject_code + "/" + file_name)
        
        self.parent.resetwindows()
        self.top.destroy()
        self.parent.showwindow("MainPage")

    def __init__(self, metadata,parent):
        self.top = tk.Toplevel(parent.parent)
        self.metadata=metadata
        self.parent=parent
        self.top.geometry("1125x650")
        self.top.title("Confirm new files")
        
        header=ttk.Label(self.top, text= "Please review the metadata of the scanned files")
        header.pack(side=tk.TOP)

        entry_label=tk.Label(self.top, text= "Enter the subject code for these files (e.g. MA, PH etc.)")
        entry_label.pack(side=tk.TOP)
        self.subject_code_entry = ttk.Entry(self.top)
        self.subject_code_entry.pack(side=tk.TOP)


        exclude_label=tk.Label(self.top, text= "Exclusions (separated by comma)")
        exclude_label.pack(side=tk.TOP)
        self.exclude_code_entry = ttk.Entry(self.top)
        self.exclude_code_entry.insert(0,"spanish, french, discrete, statistics, sets, calculus")
        self.exclude_code_entry.pack(side=tk.TOP)

        self.continue_button = ttk.Button(self.top,text="Add to local storage",command=self.add_to_local_storage)
        self.continue_button.pack(side=tk.TOP)

        self.treeview = ttk.Treeview(self.top, columns=(1, 2, 3, 4, 5, 6, 7), show='headings', height=25)
        
        self.treeview.heading(1, text='Path')
        self.treeview.heading(2, text='Valid')
        self.treeview.heading(3, text='Session')
        self.treeview.heading(4, text='Timezone')
        self.treeview.heading(5, text='Level')
        self.treeview.heading(6, text='Paper')
        self.treeview.heading(7, text='Markscheme')


        for i,key in enumerate(metadata):
            item = metadata[key]
            self.treeview.insert(parent='', index=i, iid=item["path"], values=(item["path"],item["valid"],item["session"],item["timezone"],item["level"],item["paper"],item["markscheme"]))

        self.treeview.pack(side=tk.TOP)

def assign_metadata(file_name,folder_name, path):
    import re
    session = ""
    year = ""
    valid = True
    metadata = {"path":path,"session":"","timezone":"","level":"","paper":"","markscheme":""}

    try:
        found = re.search('([0-9]{4})',folder_name)
        if found != None:
            year = found.group(1)
        else:
            valid = False
    except AttributeError:
        pass

    if "november" in folder_name.lower():  session = "N"
    elif "may" in folder_name.lower(): session = "M"
    else: valid=False

    metadata["session"]= session
    metadata["year"]=year
    

    try:
        found = re.search('TZ(\d)',file_name)
        if found != None:
            metadata["timezone"] = found.group(1)
        else: metadata["timezone"]="0"
    except AttributeError as e:
        print(e)

    if "markscheme" in file_name.lower():
        metadata["markscheme"]="MS"

    try:
        found = re.search('(paper|Paper)_(\d)',file_name)
        if found != None:
            metadata["paper"] = found.group(2)
        else:
            valid = False
    except AttributeError as e:
        print(e)

    if "HL" in file_name: metadata["level"]="HL"
    elif "SL" in file_name: metadata["level"]="SL"
    elif "HLSL" in file_name or "SLHL" in file_name or "HSL" in file_name or "SHL" in file_name: metadata["level"] = "HLSL"
    else: valid=False

    cancel = False
    excludes = "spanish, french, german, discrete, statistics, sets, calculus".split(", ")
    for exclude in excludes:
        if exclude.lower() in file_name.lower() or exclude.lower() in path.lower() or exclude.lower() in folder_name.lower():
            cancel = True
    
    if not cancel:
        metadata["valid"]=valid

        return metadata
    
    else:
        return False

def read_past_paper_handler(path,parent):
    metadata = {}
    from os.path import join, getsize
    top_level_directory = os.listdir(path)

    for root, dirs, files in os.walk(path):

        for file_name in files:
            metadata_temp = assign_metadata(file_name,root.split("/")[-1], os.path.join(root,file_name))
            if metadata_temp == False:
                pass
            else:
                metadata[os.path.join(root,file_name)]=metadata_temp

    ReadPastPaperPopUp(metadata,parent)

def get_past_papers(parent):
    path = filedialog.askdirectory(title="Dialog box")

    if path:
        read_past_paper_handler(path,parent)
