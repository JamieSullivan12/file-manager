import tkinter as tk
from tkinter import ttk,filedialog,messagebox
import sys,time, os
import shutil
from turtle import width
from tkdocviewer import *
import subprocess

class GUI(ttk.Frame):


    class Paper():
        def __init__(self,data,path,tv,collection,filter_refresh=None):
            self.data = data
            self.path = path
            self.file_name = self.data
            self.data = self.data.replace(".pdf","") # remove file extensions
            self.collection = collection
            self.filter_refresh=filter_refresh
            self.tv=tv
            self.bak_data = {}

        def getvalue(self,key):
            if key in self.dict_data:
                return self.dict_data[key]
            else: 
                return "error"
        
        def setvalue(self,key,new_value):
            if key in self.dict_data:
                self.dict_data[key]=new_value
            else: pass

        def add_to_collection(self):
            for key in self.dict_data:
                if key in self.collection:
                    if self.dict_data[key] not in self.collection[key]:
                        self.collection[key].append(self.dict_data[key])
                else:
                    self.collection[key] = []
                    self.collection[key].append(self.dict_data[key])
            self.filter_refresh()           
        
        def deconstruct_data(self, order_list, placeholder_mapping):
            self.order_list=order_list
            self.placeholder_mapping=placeholder_mapping
            """Will deconstruct self.data into its constituent parts, using a given order"""
            # PLC is a placeholder
            self.dict_data = {"PLC":"","original":self.file_name}

            # testing validity of original file name
            number_of_components = len(self.data.split("-"))
            if number_of_components == len(order_list):
                for i,component in enumerate(self.data.split("-")):
                    self.dict_data[order_list[i]]=component
            else:
                for component in order_list:
                    self.dict_data[component]=""
                            

            self.construct_file_name()

        def construct_file_name(self):
            self.file_name_list = []
            file_name = ""
            for element in self.order_list:
                if "PLC" in element:
                    self.file_name_list.append(self.placeholder_mapping[element])
                else:
                    self.file_name_list.append(self.dict_data[element])
            file_name = "-".join(self.file_name_list) + ".pdf"

            return file_name

        def print_file(self):

            os.startfile(os.path.join(self.path,self.file_name), "print")

        def open_file(self):
            subprocess.Popen([self.path + "\\" + self.file_name],shell=True)

        def add_treeview(self,index):
            self.construct_file_name()
            self.tv.insert(parent='', index=index, iid=self.dict_data["original"], values=(self.dict_data["original"],self.dict_data["session"],self.dict_data["timezone"],self.dict_data["paper"],self.dict_data["subject"]))
            self.bak_data = dict(self.dict_data)

        def rename_file(self):
            new_file_name = self.construct_file_name()
            try:

                os.rename(self.get_full_path(), self.path + "\\" + new_file_name)
                
                self.file_name = new_file_name
                self.dict_data["original"]=self.file_name
                success = True
                self.bak_data = dict(self.dict_data)
            except FileExistsError as e:
                tk.messagebox.showerror(message="File already exists\n\n" + str(e))

                self.dict_data = dict(self.bak_data)
                success = False
            


            return success
        def get_full_path(self):
            return self.path + "\\" + self.file_name

        def add_to_local_path(self,old_path,new_path):

            new_file_name = self.construct_file_name()
            
            override = True
            if os.path.exists(new_path + "\\" + new_file_name):
                override = tk.messagebox.askyesno(message="The file '" + new_path + "\\" + new_file_name + "' already exists.\n\nWould you like to override?")

            if override == True:
                shutil.copyfile(self.get_full_path(), new_path + "\\" + new_file_name)
                self.bak_data = dict(self.dict_data)

            else: 
                self.dict_data = dict(self.bak_data)


            self.path=new_path
            self.file_name=new_file_name
            self.dict_data["original"]=self.file_name



    def filter_treeview(self):
        self.tv.delete(*self.tv.get_children())
        self.tv_counter=0
        for item in self.data:
            add = True
            for filter in self.filters:
                if filter in self.data[item].dict_data:
                    if self.filters[filter].lower() not in self.data[item].dict_data[filter].lower() and not self.filters[filter]=="":
                        add = False
            if add:
                self.data[item].add_treeview(self.tv_counter)
                self.tv_counter=self.tv_counter+1


    def dropdown_handler(self, combo, type, event=None):
        self.filters[type]=combo.get()
        self.filter_treeview()


    def entry_filter_callback(self, sv, filter_type):
        self.filters[filter_type]=sv.get() 
        self.filter_treeview()

        


    class AddPaperPopUp():
        
        class ModifiableButton():
        
            def bindframe(self,frame,sequence,func):
                frame.bind(sequence, func)
                for child in frame.winfo_children():
                    child.bind(sequence, func)


            def textchangerequest(self,frame,label, getter, setter, value="", prefix="", suffix=""):
                """
                Generalised code for a text field which can be edited (through a double click)
                - frame: the frame in which this event is occuring
                - label: the text (Label) field which needs to be made mofifiable
                - getter: a function which will return the current value for that field
                - setter: a function which will take (and apply) whatever the user has entered within the Entry box
                - prefix (OPTIONAL): when the user has finished entering the new value, it will be placed back into a text box - with a prefix if selected
                - suffix (OPTIONAL): when the user has finished entering the new value, it will be placed back into a text box - with a suffix if selected 
                """

                def cancel(label, entry, row, column, padx, pady, sticky):
                    """
                    Will destroy the entry box, and replace the label widget onto the screen (as it was initially)
                    NOTE: this is called either when the user presses <Escape> or after the user presses <Enter> and the changes have been saved
                    """
                    entry.destroy()
                    label.grid(row=row,column=column,sticky=sticky,padx=padx,pady=pady)
                            
                def apply(label, entry, row, column, padx, pady, sticky, prefix, suffix):
                    """
                    Will look at the Entry box for any changes, and write them to a desired lcoation (the setter method)
                    """
                    try:
                        setter(value,entry.get())
                    except Exception as e:
                        messagebox.showerror(message="Unknown error occured:\n\n" + str(e))
                        cancel(label, entry, row, column, padx, pady, sticky)
                        return
                    
                    # insert the newly entered value into the label widget which was grid forgot from the screen
                    label["text"] = f"{prefix}{entry.get()}{suffix}"
                    cancel(label, entry, row, column, padx, pady, sticky)
                    

                    # note: this is not generalised code
                    self.parent.file_name_label["text"]=self.parent.new_paper_obj.construct_file_name()

                # remember details of the current textbox (which will need to be removed for the Entry box)
                row    = label.grid_info()['row']
                column = label.grid_info()['column']
                padx = label.grid_info()['padx']
                pady = label.grid_info()['pady']
                sticky= label.grid_info()['sticky']
                # delete the label
                label.grid_forget()

                # create and place an Entry box into the location where the label was deleted
                current_value = getter(value)
                entry = ttk.Entry(frame)
                entry.grid(row=row,column=column,sticky=sticky,padx=padx,pady=pady)
                # pre-insert the value from the getter function
                entry.insert(tk.END, current_value)

                # bind return (save changes) and escape (cancel changes) keys
                entry.bind("<Return>",lambda e:apply(label, entry, row, column, padx, pady, sticky,prefix,suffix))
                entry.bind("<Escape>",lambda e:cancel(label, entry, row, column, padx, pady, sticky))


            def __init__(self, parent, row, column, top, paper_obj, item, padx=0, pady=0):
                self.parent=parent
                self.modifiable_button = tk.Label(top,text=item.title() + ": " + paper_obj.getvalue(item), width = 20  )
                self.modifiable_button.grid(row=row+2,column=0,sticky="nw",padx=padx,pady=pady)
                self.bindframe(self.modifiable_button,"<Double-Button-1>",lambda e:self.textchangerequest(top,self.modifiable_button,paper_obj.getvalue, paper_obj.setvalue, value=item, prefix= item.title() + ": "))

        
        def complete(self,e=None):
            self.new_paper_obj.add_to_collection()

            if self.existing_paper_obj != None:
                current_file_name = self.new_paper_obj.getvalue("original")
                
                success = self.new_paper_obj.rename_file()
                if success:
                    del self.parent.data[current_file_name]
                    self.parent.data[self.new_paper_obj.getvalue("original")] = self.new_paper_obj

            else:
                self.new_path = self.selected_directory["path"]

                self.new_paper_obj.add_to_local_path(self.current_path,self.new_path)


            self.parent.data[self.new_paper_obj.getvalue("original")] = self.new_paper_obj
            self.parent.filter_treeview()
            self.parent.tv_counter += 1
            self.top.destroy()


        def __init__(self,parent,current_path=None,selected_directory=None,file_name=None, existing_paper_obj = None):
            self.top = tk.Toplevel(parent.parent)
            self.parent=parent
            self.current_path=current_path
            self.selected_directory=selected_directory
            self.top.geometry("1125x650")
            self.top.title("Confirmation")

            self.existing_paper_obj=existing_paper_obj
            if existing_paper_obj != None:
                self.new_paper_obj=existing_paper_obj
                path = self.new_paper_obj.get_full_path()

            else:
                self.new_paper_obj = parent.Paper(file_name,self.current_path,parent.tv,parent.data_collection,filter_refresh=parent.filter_refresh)
                self.new_paper_obj.deconstruct_data(self.selected_directory["convention_array"],self.selected_directory["placeholder"])

            header=tk.Label(self.top, text= "You have selected: ")
            self.file_name_label=tk.Label(self.top, text= self.new_paper_obj.construct_file_name())

            header.grid(row=0,column=0, columnspan=2, sticky="nw", padx=20,pady=(20,0))
            self.file_name_label.grid(row=0,column=0, columnspan=2, sticky="nw", padx=20,pady=(5,20))


            # grid settings for left column
            padx = (20,0)
            pady = 15

            i = 2
            for item in self.new_paper_obj.dict_data:
                if item != "PLC" and item != "original":
                    self.ModifiableButton(self,i, 0, self.top, self.new_paper_obj, item, padx=padx, pady=pady)
                i = i + 1

            self.complete_button = ttk.Button(self.top,text="Finish",command=self.complete)
            self.complete_button.grid(row = i + 2,column=0, sticky="nw",padx=padx,pady=pady)
            
            self.open_file_button = ttk.Button(self.top, text="Open PDF",command=lambda: self.new_paper_obj.open_file())
            self.open_file_button.grid(row=i+3,column=0,sticky="nw",padx=padx,pady=pady)


            self.print_button = ttk.Button(self.top, text="Print",command=self.new_paper_obj.print_file)
            self.print_button.grid(row=i+4,column=0,sticky="nw",padx=padx,pady=pady)



            # Create a DocViewer widget
            v = DocViewer(self.top, width=700,height=400)
            v.grid(row=2, column = 1, rowspan=i+3, sticky="nsew")

            # Display some document
            v.display_file(self.new_paper_obj.get_full_path())

    class GetFileTypePopUp():
        
        def continue_cmd(self):
            self.top.destroy()
            self.parent.AddPaperPopUp(self.parent,selected_directory=self.selected_directory,current_path=self.current_path,file_name=self.file_name)
            

        def select_dropdown(self,event=None):
            self.dropdown_confirmation["text"]=f"{self.directory_select.get()}\n{self.directories[self.directory_select.get()]['path']}\n{self.directories[self.directory_select.get()]['convention']}\n{self.directories[self.directory_select.get()]['path']}"
            
            self.selected_directory = self.directories[self.directory_select.get()]

            self.continue_button.pack(side=tk.TOP)


        def __init__(self,parent,directories,current_path,file_name):
            self.top = tk.Toplevel(parent.parent)
            self.parent=parent
            self.current_path=current_path
            self.file_name=file_name
            self.directories=directories
            self.top.geometry("1125x650")
            self.top.title("Select Destination Directory")
            
            header=tk.Label(self.top, text= "Please select a destination directory for:\n" + self.file_name)
            header.pack(side=tk.TOP)

            self.dropdown_confirmation=tk.Label(self.top, text="Nothing selected")
            self.dropdown_confirmation.pack(side=tk.TOP)

            self.continue_button = ttk.Button(self.top,text="Continue",command=self.continue_cmd)


            directory_arr = self.directories.keys()
            # give selection for the output directory
            self.directory_select = ttk.Combobox(self.top, values=list(directory_arr),state="readonly")
            self.directory_select.pack(side=tk.TOP)
            self.directory_select.bind("<<ComboboxSelected>>", self.select_dropdown)



    def add_paper(self,event=None):
        path = tk.filedialog.askopenfilename(initialdir = "Downloads",
                                        title = "Select a File")
                                        #filetypes = ("Text files",
                                                    #"*.pdf")
        
        current_path = "/".join(path.split("/")[:-1])
        file_name = path.split("/")[-1]

        if path:
            self.GetFileTypePopUp(self,self.directories,current_path,file_name)



    def filter_refresh(self):
        try:
            for combobox in self.comboboxes:
                for item in self.data_collection:
                    if item == combobox:
                        for specific_filter in self.data_collection[item]:
                            if specific_filter not in self.comboboxes[combobox]["values"]:
                                self.comboboxes[combobox]["values"] =  (*self.comboboxes[combobox]['values'], specific_filter)
        except Exception as e:
            print(e)

    def treeview_edit(self,event):        
        # retrieving the path from the heirarchy row
        path = self.tv.identify('item',event.x,event.y)
        
        paper_obj = self.data[path]

        self.AddPaperPopUp(self,existing_paper_obj=paper_obj)


    def manage_config(self):
        import json
        import configparser
        self.error = ''
        self.config = configparser.ConfigParser()
        self.config.optionxform = lambda option: option

        try:
            self.config.read('config.ini')
        except configparser.ParsingError as e:
            MsgBox = messagebox.showerror(title='Config Error', message='It is likely that your configuration file has been corrupted. The config file will be reset, however a backup of the current one will be created (config.ini.bak).\n\n Please contact admin in order to enter all correct elements. \n\nError Msg: ' + str(e))
            os.rename('config.ini', 'config.ini.bak')
            self.config.read('config.ini')
        

        self.directories = {}

        for heading in self.config.sections():
            if "directory" in heading:
                name = self.config[heading]["name"]
                code = self.config[heading]["code"]
                path = self.config[heading]["path"]
                convention = self.config[heading]["convention"]
                convention_array = convention.split("-")
                placeholder_string = self.config[heading]["placeholder"]
                placehodelder = json.loads(placeholder_string)
                self.directories[name]={"name":name,"code":code,"path":path,"convention":convention,"convention_array":convention_array, "placeholder":placehodelder}

        with open('config.ini','w') as configFile:
            self.config.write(configFile)


    
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
                        file_name = f'Original-{self.metadata[item]["session"]}-TZ{self.metadata[item]["timezone"]}-P{self.metadata[item]["paper"]}-{self.subject_code}{self.metadata[item]["level"]}-{self.metadata[item]["markscheme"]}.pdf'
                        shutil.copyfile(self.metadata[item]["path"],"Papers/" + self.subject_code + "/" + file_name)


        def __init__(self,parent, metadata):
            self.top = tk.Toplevel(parent.parent)
            self.parent=parent
            self.metadata=metadata
            self.top.geometry("1125x650")
            self.top.title("Confirm new files")
            
            header=tk.Label(self.top, text= "Please review the metadata of the scanned files")
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

    def assign_metadata(self,file_name,folder_name, path):
        import re
        session = ""
        year = ""
        valid = True
        metadata = {"path":path,"session":"","timezone":"","level":"","paper":"","markscheme":""}

        try:
            found = re.search('([0-9]{4})',folder_name)
            if found != None:
                year = found.group(1)[-2:]
            else:
                valid = False
        except AttributeError:
            pass

        if "november" in folder_name.lower():  session = "N"
        elif "may" in folder_name.lower(): session = "M"
        else: valid=False

        metadata["session"]= year + session
        
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
        excludes = "spanish, french, discrete, statistics, sets, calculus".split(", ")
        for exclude in excludes:
            print("Exclude",exclude,file_name.lower(), exclude.lower() in file_name.lower())
            if exclude.lower() in file_name.lower() or exclude.lower() in path.lower() or exclude.lower() in folder_name.lower():
                cancel = True
                print("EXCLUDE",path,file_name)
        
        if not cancel:
            metadata["valid"]=valid

            return metadata
        
        else:
            return False

    def read_past_paper_handler(self,path):
        metadata = {}
        from os.path import join, getsize
        self.top_level_directory = os.listdir(path)

        for root, dirs, files in os.walk(path):

            for file_name in files:
                print(file_name)
                metadata_temp = self.assign_metadata(file_name,root.split("/")[-1], os.path.join(root,file_name))
                if metadata_temp == False:
                    pass
                else:
                    metadata[os.path.join(root,file_name)]=metadata_temp

        self.ReadPastPaperPopUp(self,metadata)

    def get_past_papers(self):
        path = filedialog.askdirectory(title="Dialog box")
    
        if path:
            self.read_past_paper_handler(path)

    

    def __init__(self,parent,root):
        self.parent = parent
        self.root=root


        self.manage_config()


        self.tv = ttk.Treeview(self.parent, columns=(1, 2, 3, 4, 5), show='headings', height=25)

        self.tv.heading(1, text='Name')
        self.tv.heading(2, text='Session')
        self.tv.heading(3, text='Timezone')
        self.tv.heading(4, text='Paper')
        self.tv.heading(5, text='Subject')

        self.data_collection = {"session":[],"paper":[],"timezone":[],"subject":[]}
        self.data = {}
        self.tv_counter = 0

        for directory in self.directories:
            if os.path.exists(self.directories[directory]["path"]):
                dir_metadata = self.directories[directory]

                self.dir_arr = os.listdir(dir_metadata["path"])

                for i,item in enumerate(self.dir_arr):
                    new_paper_obj = self.Paper(item,dir_metadata["path"],self.tv,self.data_collection,filter_refresh=self.filter_refresh)
                    new_paper_obj.deconstruct_data(dir_metadata["convention_array"],dir_metadata["placeholder"])
                    new_paper_obj.add_treeview(self.tv_counter)
                    new_paper_obj.add_to_collection()

                    self.data[new_paper_obj.getvalue("original")] = new_paper_obj
                    self.tv_counter=self.tv_counter+1
            else:
                print("path does not exist:",directory)
        # when a row on the treeview is double clicked, treeview_edit will be run (
        # opening the selected file will be prompted - see function description for more info)
        self.tv.bind("<Double-1>", self.treeview_edit)

        self.filters={}

        self.comboboxes = {}

        i = 0



        self.session_label = ttk.Label(self.parent,text="Session Filter")
        self.session_label.grid(row=i,column=0,sticky="nw")

        self.session_filter = ttk.Combobox(self.parent, values=self.data_collection["session"] + [""],state="readonly")
        self.session_filter.grid(row=i,column=1,sticky="nw")
        self.session_filter.bind("<<ComboboxSelected>>", lambda e: self.dropdown_handler(self.session_filter, "session"))

        sv3 = tk.StringVar()
        sv3.trace("w", lambda name, index, mode, sv=sv3: self.entry_filter_callback(sv, "session"))
        self.session_entry = ttk.Entry(self.parent, textvariable=sv3)
        self.session_entry.grid(row=i,column=2,sticky="nw")

        self.comboboxes["session"]=self.session_filter


        i += 1

        self.subject_label = ttk.Label(self.parent,text="Subject Filter")
        self.subject_label.grid(row=i,column=0,sticky="nw")

        self.subject_filter = ttk.Combobox(self.parent, values=self.data_collection["subject"] + [""],state="readonly")
        self.subject_filter.grid(row=i,column=1,sticky="nw")
        self.subject_filter.bind("<<ComboboxSelected>>", lambda e: self.dropdown_handler(self.subject_filter, "subject"))

        sv1 = tk.StringVar()
        sv1.trace("w", lambda name, index, mode, sv=sv1: self.entry_filter_callback(sv, "subject"))
        self.subject_entry = ttk.Entry(self.parent, textvariable=sv1)
        self.subject_entry.grid(row=i,column=2,sticky="nw")

        self.comboboxes["subject"]=self.subject_filter

        i += 1

        self.timezone_label = ttk.Label(self.parent,text="Timezone Filter")
        self.timezone_label.grid(row=i,column=0,sticky="nw")

        self.timezone_filter = ttk.Combobox(self.parent, values=self.data_collection["timezone"] + [""],state="readonly")
        self.timezone_filter.grid(row=i,column=1,sticky="nw")
        self.timezone_filter.bind("<<ComboboxSelected>>", lambda e: self.dropdown_handler(self.timezone_filter, "timezone"))
        self.comboboxes["timezone"]=self.timezone_filter

        sv2 = tk.StringVar()
        sv2.trace("w", lambda name, index, mode, sv=sv2: self.entry_filter_callback(sv, "timezone"))
        self.timezone_entry = ttk.Entry(self.parent, textvariable=sv2)
        self.timezone_entry.grid(row=i,column=2,sticky="nw")

        i += 1


        self.paper_label = ttk.Label(self.parent,text="Paper Filter")
        self.paper_label.grid(row=i,column=0,sticky="nw")

        self.paper_filter = ttk.Combobox(self.parent,values=self.data_collection["paper"] + [""],state="readonly")
        self.paper_filter.grid(row=i,column=1,sticky="nw")
        self.paper_filter.bind("<<ComboboxSelected>>", lambda e: self.dropdown_handler(self.paper_filter, "paper"))

        sv4 = tk.StringVar()
        sv4.trace("w", lambda name, index, mode, sv=sv4: self.entry_filter_callback(sv, "paper"))
        self.paper_entry = ttk.Entry(self.parent, textvariable=sv4)
        self.paper_entry.grid(row=i,column=2,sticky="nw")


        self.comboboxes["paper"]=self.paper_filter

        i += 1

        self.add_paper_button = ttk.Button(self.parent,text="Add Paper",command=self.add_paper)
        self.add_paper_button.grid(row=i,column=0,columnspan=3,sticky="nw")



        

        i += 1


        # Adding a vertical scrollbar to Treeview widget
        treeScroll = ttk.Scrollbar(self.parent)
        treeScroll.configure(command=self.tv.yview)
        self.tv.configure(yscrollcommand=treeScroll.set)
        treeScroll.grid(row=i,column=3,sticky="ns")

        # Adding a vertical scrollbar to Treeview widget
        treexScroll = ttk.Scrollbar(self.parent, orient=tk.HORIZONTAL)
        treexScroll.configure(command=self.tv.xview)
        self.tv.configure(xscrollcommand=treexScroll.set)
        treexScroll.grid(row=i+1,column=0,columnspan=3,sticky="ew")

        self.tv.grid(row=i,column=0,columnspan=3,sticky="nw")

        i += 2

        self.get_past_papers_button = ttk.Button(self.parent,text="Add Past Papers",command=self.get_past_papers)
        self.get_past_papers_button.grid(row=i,column=0,columnspan=2,sticky="nw")


def destroyer():
    """ Handle program exit - will close all windows and command lines to prevent the program from remaining open in the background"""
    root.quit()
    root.destroy()
    sys.exit()

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    parent = tk.Toplevel(master=root)

    parent.title("Past Paper Manager")

    parent.minsize(150,150)
    parent.geometry("1200x800")

    gui = GUI(parent,root)

    # handle program exit protocol
    root.protocol("WM_DELETE_WINDOW", destroyer)
    parent.protocol("WM_DELETE_WINDOW", destroyer)

    parent.mainloop()