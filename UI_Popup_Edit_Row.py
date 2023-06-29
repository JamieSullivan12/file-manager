from email import message
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import modifiable_label,os
from tkdocviewer import *
import subprocess
import pandas as pd
import values_and_rules
import customtkinter as ctk
import autocomplete_with_dropdown
import custom_errors


class UIPopupEditRow(ctk.CTkFrame):
    
    class PDFPopUp(tk.Toplevel):
        def open_pdf(self,event=None):
            try:
                cwd = os.getcwd()
                subprocess.Popen([os.path.join(cwd,self.path)],shell=True)

            except Exception as e:
                tk.messagebox.showwarning(message=str(e))

        def __init__(self, parent, path):
            super().__init__(parent.mainline_obj.parent)
            self.path=path
            self.geometry("900x900")
            self.title("PDF viewer: " + path)
            

            open_pdf_button = ctk.CTkButton(self,text="Open PDF",command=self.open_pdf)
            open_pdf_button.grid(row=0,column=0)

            # Create a DocViewer widget
            v = DocViewer(self, width=900,height=850)
            v.grid(row=1, column = 0, sticky="nsew")



            cwd = os.getcwd()

            # Display some document
            v.display_file(os.path.join(cwd,path))

    class DocumentsFrame(ctk.CTkFrame):
        class DocumentRowFrame(ctk.CTkFrame):
            def delete_path(self):
                self.document_object.remove_document()
                
                self.document_frame.parent.refresh_document_buttons(type=self.document_frame.type)

            def identifier_change(self):
                self.document_object.set_suffix(self.identifier_input.get())
                self.document_frame.parent.paper_obj.update_database()
                self.document_frame.parent.refresh_document_buttons(type=self.document_frame.type)


            def identifier_input_event(self,event):
                try:self.identifier_save_button.grid_forget()
                except Exception as e:
                    print(e)
                if self.identifier_input.has_changed():
                    self.identifier_save_button.grid(row=self.row,column=3,pady=10,padx=2,sticky="new")

            def make_grid(self,critical):
                try:
                    self.frame_1.grid_forget()
                except Exception as e:
                    pass
                    
                try:
                    self.frame_2.grid_forget()
                except Exception as e:
                    pass

                
                frame2_row=0
                frame2_column=2
                if critical<=2:
                    pady1=(10,2)
                    pady2=(2,10)
                    frame2_row=1
                    frame2_column=1

                    self.columnconfigure(1,weight=1)
                    self.columnconfigure(2,weight=0)

                
                else:
                    pady1=10
                    pady2=10
                    self.columnconfigure(1,weight=1)
                    self.columnconfigure(2,weight=1)


                self.frame_1.grid(row=0,column=1,pady=pady1,padx=(0,4),sticky="new")
                self.frame_2.grid(row=frame2_row,column=frame2_column,pady=pady2,sticky="new",padx=(0,4))
                





            def __init__(self, document_frame, document_object,number):
                super().__init__(document_frame,fg_color="transparent")
                self.document_object=document_object

                self.deleted=False
                self.document_frame=document_frame

                
                button_width = 20



                row=0

                self.frame_1=ctk.CTkFrame(self,fg_color="transparent")
                self.frame_2=ctk.CTkFrame(self,fg_color="transparent")

                self.delete_path_button = ctk.CTkButton(self.frame_2,text="Remove",width=button_width,command=lambda:self.delete_path())
                self.open_button = ctk.CTkButton(self.frame_2,text="Open",width=button_width,command=lambda:self.document_frame.parent.open(self.document_object))
                self.identifier_save_button = ctk.CTkButton(self.frame_2,text="Save",width=button_width,command=self.identifier_change)
                self.frame_1.columnconfigure(0,weight=1)
                self.frame_1.columnconfigure(1,weight=1)


                self.frame_2.columnconfigure(0,weight=1)
                self.frame_2.columnconfigure(1,weight=1)
                self.frame_2.columnconfigure(2,weight=1)
                
                self.number_label = ctk.CTkLabel(self,text=f"{str(number)}.")

                self.label_path = ctk.CTkEntry(self.frame_1)

                self.identifier_default_text = "Path extension"



                self.identifier_input=ctk.CTkEntry(self.frame_1,placeholder_text="File suffix")
                



                self.number_label.grid(row=0,column=0,sticky="nw",pady=(10,0),padx=(2,0))
                self.label_path.grid(row=0,column=1,sticky="new",padx=(0,2),pady=0)
  
                self.delete_path_button.grid(row=0,column=2,sticky="new",padx=(2,0))
                if self.document_object.validitycheck_file_path() == True:
                    self.label_path.insert(0,self.document_object.get_current_file_name())
                    
                    self.identifier_save_button.grid(row=0,column=0,padx=(0,2),sticky="new")

                    self.identifier_input.grid(row=0,column=2,padx=(2,0),sticky="new")
                    if self.document_object.get_suffix()!="":
                        self.identifier_input.insert(0,self.document_object.get_suffix())
                    
                    self.open_button.grid(row=0,column=1,sticky="new",padx=2)

                else:
                    self.number_label.configure(text=f"{str(number)}. Cannot find file")
                    self.label_path.insert(0,self.document_object.get_current_file_path())
                self.label_path.configure(state='readonly')
   
                self.make_grid(critical=self.document_frame.parent.critical)
              
        def add_path(self):
            self.parent.paper_obj.create_insert_new_document(self.type)
            if self.parent.type == "update":
                self.parent.paper_obj.update_database()

            self.parent.refresh_document_buttons(type=self.type)

        def make_grid(self,critical):

            for row in self.document_rows:
                row.make_grid(critical=critical)


        def __init__(self,parent,frame,type,name,document_objects):
            super().__init__(frame,fg_color="transparent")
            self.type=type
            self.name=name
            self.parent = parent

            self.columnconfigure(0,weight=1)

            self.add_button = ctk.CTkButton(self,text=f"Add {name}",command=lambda: self.add_path(),width=50)
            self.add_button.grid(row=0,column=0, sticky="new",pady=(10,0))

            self.document_rows=[]

            for index,document_object_id in enumerate(document_objects):
                document_row = self.DocumentRowFrame(self,document_objects[document_object_id],index+1)
                document_row.grid(row=index+1,column=0,sticky="new")
                self.document_rows.append(document_row)

    def open(self,document_obj, event=None):
        cwd = os.getcwd()
        subprocess.Popen([document_obj.get_current_file_path()],shell=True)

       

    def view(self,path,event=None):

        self.PDFPopUp(self,path)
    
    def refresh_page(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        self.paper_obj.update_object()
        self.setup_page()

    def update_database(self,event=None,refresh_page = True):
        self.paper_obj.update_database()

    def save_database(self,event=None,refresh_page = True):
        self.mainline_obj.db_object.save_row(self.paper_obj)
        if refresh_page:
            self.refresh_page()

        self.mainline_obj.frames["MainPage"].populate_treeview()

    def dropdown_handler(self, combo, label_obj, combo_type, setter, getter):

        if combo.get() == "": setter(False)
        elif combo.get() == "True": setter(True)
        elif combo.get() == "False": setter(False)
        else: setter(False)


        label_obj['text'] = combo_type + ": " + str(getter())



    def completed_date_popup(self, date):
        self.completed_date=date
        #self.select_completed_date_label.configure(text="Completed date: \n" + str(self.paper_obj.get_completed_date()))
        if self.completed_date != None:
            self.completed_date_input.change_contents(values_and_rules.format_date(date))
            self.completed_date_label.configure(text="Completed date (unsaved *)")
        else:
            self.completed_date_label.configure(text="Completed date (unsaved *)")
            self.completed_date_input.clear()

    def update_completed_date(self,refresh_page=True):
        change = tk.messagebox.askyesno(message="Would you like to set the completed date to today?")
        if change:
            self.paper_obj.set_completed_date(pd.to_datetime("today"))
            self.update_database(refresh_page=refresh_page)
            #self.refresh_page()
            self.paper_obj.set_ignore_update(False)
        else:
            self.paper_obj.set_ignore_update(True)
 
    def setup_document_buttons(self,type=""):
        self.directories_frame.columnconfigure(0,weight=1)
        if type == "" or type=="questionpaper":
            self.original_document_row = self.DocumentsFrame(self,self.directories_frame,"questionpaper",self.terminology["Original"],self.paper_obj.get_questionpaper_documents())
            self.original_document_row.grid(row=1,column=0,columnspan=3,padx=self.inner_x_padding,sticky="new")
        if type == "" or type=="markscheme":
            self.markscheme_document_row = self.DocumentsFrame(self,self.directories_frame,"markscheme",self.terminology["Markscheme"],self.paper_obj.get_markscheme_documents())
            self.markscheme_document_row.grid(row=2,column=0,columnspan=3,padx=self.inner_x_padding,sticky="new")
        if type == "" or type=="attachment":
            self.otherattachments_document_row = self.DocumentsFrame(self,self.directories_frame,"attachment","Attachments",self.paper_obj.get_attachment_documents())
            self.otherattachments_document_row.grid(row=3,column=0,columnspan=3,padx=self.inner_x_padding,sticky="new")

        self.open_directory_button = ctk.CTkButton(self.directories_frame,text="Open File Directory",command=self.paper_obj.open_documents_directory,width=24)
        self.open_directory_button.grid(row=4,column=0,sticky="nw",columnspan=3,padx=self.inner_x_padding,pady=(5,self.inner_y_padding))

    
    def refresh_document_buttons(self,type=""):
        if type=="questionpaper" or type=="":
            self.original_document_row.destroy()
        if type=="markscheme" or type=="":
            self.markscheme_document_row.destroy()
        if type=="attachment" or type=="":
            self.otherattachments_document_row.destroy()
        self.setup_document_buttons(type)


    def reset_completed_date(self):
        self.completed_date_popup(None)

    def select_completed_date(self):
        import date_popup
        date_popup.dateselect("Please select a date",self.completed_date_popup)

    def create_gradeboundary_box(self):

        gradeboundaries_inner_frame = ctk.CTkFrame(self.gradeboundaries_frame,fg_color="transparent")
        gradeboundaries_inner_frame.grid(row=1,column=0,padx=self.inner_x_padding,pady=(10,self.inner_y_padding),sticky="new")

        gradeboundaries_inner_frame.columnconfigure(0,weight=1)
        gradeboundaries_inner_frame.columnconfigure(1,weight=1)

        grade_boundaries_list = values_and_rules.get_course_grade_boundaries()[self.paper_obj.get_course_type()]

        self.grade_boundary_entries = []

        row = 0
        for grade_boundary in grade_boundaries_list:
            self.grade_boundary_entries.append(self.create_entry_box(gradeboundaries_inner_frame,title=self.terminology["Grade"]+f" {grade_boundary}",autofill=[],obj_getter=self.paper_obj.get_grade_boundary,obj_setter=self.paper_obj.set_grade_boundary,obj_getter_args=(grade_boundary),obj_setter_args=(grade_boundary)))

            #boundary_input.grid(row=row,column=0,padx=20,pady=5,sticky="new")
            row += 1

        self.grade_boundary_entries.append(self.create_entry_box(gradeboundaries_inner_frame,title="Maximum mark",autofill=[],obj_getter=self.paper_obj.get_gbmax,obj_setter=self.paper_obj.set_gbmax))

        #maxmark_input.grid(row=row,column=0,padx=20,pady=5,sticky="new")


    class InputTracker():
        def __init__(self,controller,obj_getter,obj_setter,obj_getter_args=None,obj_setter_args=None,state="normal",placeholder_text=None):
            self.controller=controller
            self.obj_getter=obj_getter
            self.obj_setter=obj_setter
            self.obj_getter_args=obj_getter_args
            self.obj_setter_args=obj_setter_args
            self.widget_getter=None
            self.widget_setter=None
            self.changed=False
            self.label=None
            self.label_text=None
            self.placeholder_text = placeholder_text or ""
            self.state=state

        def apply_to_setter(self):
            valid = True
            if self.obj_setter!=None:
                if self.obj_setter_args!= None:
                    valid, reason, attribute = self.obj_setter(self.widget_getter(),self.obj_setter_args)
                else:
                    valid, reason, attribute = self.obj_setter(self.widget_getter())
            if valid == False:
                return f"Invalid '{attribute}': {reason}"
            else: return ""
        def refresh(self):
            self.entry.temp_deativate()
            #self.entry.configure(state="normal")
            got = self.get()
            #self.entry.grid_forget()

            #self.entry.delete(0, tk.END) #deletes the current value
            #self.entry.update()
            #self.entry.insert(0, got)
            #if self.state == "readonly":
            #    self.entry.configure(state="readonly")
            self.changed=False
            #self.entry.replace(got)
            self.entry.insert("end","TEST")
            self.set_label()
            
            self.entry.re_activate()


        def entry_event(self,event=None):
            got=self.get()

            if self.widget_getter() == got:
                self.changed=False
            else:
                self.changed=True
            if self.label != None:
                self.set_label()

        def set_label(self):
            if self.changed:
                self.label.configure(text=self.label_text + " *")
            else:
                self.label.configure(text=self.label_text)


        def get(self):
            if self.obj_getter_args!= None:
                got = self.obj_getter(self.obj_getter_args)
            else:
                got = self.obj_getter()
            return got


        def bind_label(self,label,text):
            self.label_text=text
            self.label=label

        def unsaved(self):
            self.entry_event
            return self.changed
            


                      
        def bind_entry(self,entry):
            self.entry=entry

            self.widget_getter=self.entry.get
            
            got=self.get()

            print("ENTRY INSERT")
            if got != "":
                self.entry.insert(0,str(got))
            
            self.entry.bind("<KeyRelease>",self.entry_event)
            self.entry.bind("<Tab>",self.entry_event)
            self.entry.bind("<Return>",self.entry_event)




    def create_entry_box(self,master_frame,title="",autofill=[],obj_getter=None,obj_setter=None,placeholder_text="",state="normal",obj_getter_args=None,obj_setter_args=None):

        label = ctk.CTkLabel(master_frame,text=title, justify="left")

        entry = autocomplete_with_dropdown.Autocomplete(master_frame,options=autofill,func="contains",hitlimit=5,state="normal",placeholder_text=placeholder_text)

        new_input_tracker = self.InputTracker(self,obj_getter,obj_setter,obj_getter_args=obj_getter_args,obj_setter_args=obj_setter_args,state=state,placeholder_text=placeholder_text)
        new_input_tracker.bind_entry(entry)
        new_input_tracker.bind_label(label,text=title)
        entry.activate()

        entry.configure(state=state)

        

        self.input_trackers.append(new_input_tracker)


        return label,entry



    def set_subject_intervention(self,value):

        self.paper_obj.set_subject(value)  
            
    def grid_apply(self,item,rc,cc,c_mod,**kwargs):
        #try:
        #    item.grid_forget()
        #except Exception as e:
        #    pass

        item.grid(row=rc,column=cc,**kwargs)
        cc+=1
        if cc%c_mod==0:
            rc+=1
            cc=0
        return rc,cc

    def make_metadata_grid(self,critical):
        rc=0 # row counter
        cc=0 # column counter
        c_mod=2
        if critical<=2:
            c_mod=1
        rc,cc=self.grid_apply(self.overridename_label,rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
        rc,cc=self.grid_apply(self.overridename_entry,rc=rc,cc=cc,c_mod=c_mod,sticky="new")
        if self.terminology["show_year"]:
            rc,cc=self.grid_apply(self.year_label,rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
            rc,cc=self.grid_apply(self.year_entry,rc=rc,cc=cc,c_mod=c_mod,sticky="new")
        if self.terminology["show_session"]:
            rc,cc=self.grid_apply(self.session_label,rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
            rc,cc=self.grid_apply(self.session_entry,rc=rc,cc=cc,c_mod=c_mod,sticky="new")
        if self.terminology["show_timezone"]:
            rc,cc=self.grid_apply(self.timezone_label,rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
            rc,cc=self.grid_apply(self.timezone_entry,rc=rc,cc=cc,c_mod=c_mod,sticky="new")
        if self.terminology["show_paper"]:
            rc,cc=self.grid_apply(self.paper_label,rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
            rc,cc=self.grid_apply(self.paper_entry,rc=rc,cc=cc,c_mod=c_mod,sticky="new")

        if self.terminology["show_subject"]:
            rc,cc=self.grid_apply(self.subject_label,rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
            rc,cc=self.grid_apply(self.subject_entry,rc=rc,cc=cc,c_mod=c_mod,sticky="new")

        if self.terminology["show_level"]:
            rc,cc=self.grid_apply(self.level_label,rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
            rc,cc=self.grid_apply(self.level_entry,rc=rc,cc=cc,c_mod=c_mod,sticky="new")
        
    def make_gradeboundaries_grid(self,critical):
        rc=0 # row counter
        cc=0 # column counter
        c_mod=2
        if critical <=2:
            c_mod=1
        for item in self.grade_boundary_entries:
            rc,cc=self.grid_apply(item[0],rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
            rc,cc=self.grid_apply(item[1],rc=rc,cc=cc,c_mod=c_mod,sticky="new")

    def make_completed_grid(self,critical):
        rc=0 # row counter
        cc=0 # column counter
        c_mod=2
        date_buttons_col=1
        if critical<=2:
            c_mod=1
            date_buttons_col=0
        
        for item in self.completed_widgets:
            rc,cc=self.grid_apply(item[0],rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
            rc,cc=self.grid_apply(item[1],rc=rc,cc=cc,c_mod=c_mod,sticky="new")

        self.date_buttons_frame.grid(row=rc,column=date_buttons_col,sticky="new",padx=(0,self.inner_x_padding),pady=(2,self.inner_y_padding))


    def make_documentrows_grid(self,critical=False):
        self.original_document_row.make_grid(critical=critical)
        self.markscheme_document_row.make_grid(critical=critical)
        self.otherattachments_document_row.make_grid(critical=critical)


    def make_grid(self,critical):
        self.critical=critical
        
        self.make_metadata_grid(self.critical)
        
        if self.type == "update":
            self.make_gradeboundaries_grid(self.critical)
            self.make_completed_grid(self.critical)
            self.make_documentrows_grid(self.critical)

    def setup_name_label(self):
        self.name_label.configure(state="normal")
        self.name_label.delete(0,tk.END)

        self.name_label.insert(0,self.paper_obj.get_name())
        self.name_label.configure(state="readonly")

    def update_date_entry(self):
        self.completed_date_label.configure(text="Completed date")

        self.completed_date_input.change_contents(self.paper_obj.get_completed_date_pretty())

    def update_grade_and_percentage(self):
        self.percentage_box.change_contents(self.paper_obj.get_percentage_pretty())
        self.grade_box.change_contents(self.paper_obj.get_grade_pretty())


    def setup_page(self):
        self.critical=False
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)

        self.heading_frame = ctk.CTkFrame(self,fg_color=self.mainline_obj.colors.bubble_background)
        self.heading_frame.grid(row=0,column=0,columnspan=1,sticky="nsew",padx=(20,10),pady=(20,10))

        subheading_font = (None,18)
        self.inner_x_padding = 10
        self.inner_y_padding = 20

        self.all_input_fields = []
        
        self.metadata_frame = ctk.CTkFrame(self,fg_color=self.mainline_obj.colors.bubble_background)
        self.metadata_frame.grid(row=0,column=1,columnspan=1,sticky="nsew",padx=(10,20),pady=(20,10))
        self.metadata_frame.columnconfigure(0,weight=1)
        self.metadatasubheading = ctk.CTkLabel(self.metadata_frame,text="Meta data",font=subheading_font)
        self.metadatasubheading.grid(row=0,column=0,padx=self.inner_x_padding,pady=(10,0),sticky="nw")

        self.input_trackers=[]
        
        row = 0
        column = 0
        

        metadata_inner_frame = ctk.CTkFrame(self.metadata_frame,fg_color="transparent")
        metadata_inner_frame.grid(row=1,column=0,padx=self.inner_x_padding,pady=(10,self.inner_y_padding),sticky="new")

        metadata_inner_frame.columnconfigure(0,weight=1)
        metadata_inner_frame.columnconfigure(1,weight=1)

        #override_name_button = CreateInput(metadata_inner_frame,"Override name",getter=self.paper_obj.get_custom_name,setter=self.paper_obj.set_custom_name,override_frame=True,override_frame_row=row,inner_padding=5)
        self.overridename_label,self.overridename_entry=self.create_entry_box(metadata_inner_frame,title="Override name",autofill=[],obj_getter=self.paper_obj.get_custom_name,obj_setter=self.paper_obj.set_custom_name)

        # override_name_button.grid(row=row,column=column,padx=10,pady=5,sticky="new")
        row += 1

        self.year_label,self.year_entry=self.create_entry_box(metadata_inner_frame,title=self.terminology["Year"],autofill=[],obj_getter=self.paper_obj.get_year,obj_setter=self.paper_obj.set_year)
        row += 1

        if self.terminology["show_session"]:

            self.session_label,self.session_entry=self.create_entry_box(metadata_inner_frame,title=self.terminology["Session"],autofill=list(self.terminology["dict_session"].values()),obj_getter=self.paper_obj.get_session,obj_setter=self.paper_obj.set_session)
            row += 1


        if self.terminology["show_timezone"]:

            self.timezone_label,self.timezone_entry=self.create_entry_box(metadata_inner_frame,title=self.terminology["Timezone"],autofill=list(self.terminology["dict_timezone"].values()),obj_getter=self.paper_obj.get_timezone,obj_setter=self.paper_obj.set_timezone)
            row += 1
        
        if self.terminology["show_paper"]:

            self.paper_label,self.paper_entry=self.create_entry_box(metadata_inner_frame,title=self.terminology["Paper"],autofill=list(self.terminology["dict_paper"].values()),obj_getter=self.paper_obj.get_paper,obj_setter=self.paper_obj.set_paper)
            row += 1

        if self.terminology["show_subject"]:

            self.subject_label,self.subject_entry=self.create_entry_box(metadata_inner_frame,title=self.terminology["Subject"],autofill=list(self.mainline_obj.settings.subjects.values()),obj_getter=self.paper_obj.get_subject,obj_setter=self.paper_obj.set_subject)
            row += 1
        
        if self.terminology["show_level"]:
 
            self.level_label,self.level_entry=self.create_entry_box(metadata_inner_frame,title=self.terminology["Level"],autofill=list(self.terminology["dict_level"].values()),obj_getter=self.paper_obj.get_level,obj_setter=self.paper_obj.set_level)

            row += 1




        padx=15
        pady=7

        if self.type != "create":

            self.directories_frame = ctk.CTkFrame(self,fg_color=self.mainline_obj.colors.bubble_background)
            self.directories_frame.grid(row=2,column=0,columnspan=2,sticky="nsew",padx=20,pady=(10,20))
            self.directoriessubheading = ctk.CTkLabel(self.directories_frame,text="Files",font=subheading_font)
            self.directoriessubheading.grid(row=0,column=0,padx=self.inner_x_padding,pady=(10,0),sticky="nw")



            self.completed_frame = ctk.CTkFrame(self,fg_color=self.mainline_obj.colors.bubble_background)
            self.completed_frame.grid(row=1,column=0,columnspan=1,sticky="nsew",padx=(20,10),pady=10)
            self.completedsubheading = ctk.CTkLabel(self.completed_frame,text="Completed data",font=subheading_font)
            self.completedsubheading.grid(row=0,column=0,columnspan=1,padx=self.inner_x_padding,pady=(10,0),sticky="nw")

            
            self.completed_frame.columnconfigure(0,weight=1)


            self.gradeboundaries_frame = ctk.CTkFrame(self,fg_color=self.mainline_obj.colors.bubble_background)
            self.gradeboundaries_frame.grid(row=1,column=1,columnspan=1,sticky="nsew",padx=(10,20),pady=10)
            self.gradeboundariessubheading = ctk.CTkLabel(self.gradeboundaries_frame,text="Grade boundaries data",font=subheading_font)
            self.gradeboundariessubheading.grid(row=0,column=0,padx=self.inner_x_padding,pady=(10,0),sticky="nw")

            self.gradeboundaries_frame.columnconfigure(0,weight=1)

            self.create_gradeboundary_box()

            self.completedinner_frame = ctk.CTkFrame(self.completed_frame,fg_color="transparent")
            self.completedinner_frame.grid(row=1,column=0,columnspan=3,sticky="new",padx=self.inner_x_padding,pady=(10,0))
            self.completedinner_frame.columnconfigure(0,weight=1)
            self.completedinner_frame.columnconfigure(1,weight=1)

            self.completed_widgets=[]

            row=0
            self.completed_widgets.append(self.create_entry_box(self.completedinner_frame,title="Mark",autofill=[],obj_getter=self.paper_obj.get_mark,obj_setter=self.paper_obj.set_mark))
            self.completed_widgets.append(self.create_entry_box(self.completedinner_frame,title="Maximum",autofill=[],obj_getter=self.paper_obj.get_maximum,obj_setter=self.paper_obj.set_maximum))
            #self.create_entry_box(self.completedinner_frame,title="Percentage (calculated)",autofill=[],obj_getter=self.paper_obj.get_percentage_pretty,placeholder_text="Enter mark",state="readonly")
            #self.create_entry_box(self.completedinner_frame,title="Grade (calculated)",autofill=[],obj_getter=self.paper_obj.get_grade_pretty,placeholder_text="Enter mark and grade boundaries",state="readonly")
            import CommonFunctions

            self.percentage_label = ctk.CTkLabel(self.completedinner_frame,text="Percentage (calculated)")
            self.grade_label = ctk.CTkLabel(self.completedinner_frame,text="Grade (calculated)")

            self.percentage_box = CommonFunctions.NewEntry(self.completedinner_frame,placeholder_text="Enter mark")
            self.percentage_box.toggle_readonly_on()
            self.grade_box = CommonFunctions.NewEntry(self.completedinner_frame,placeholder_text="Enter mark and grade boundaries")
            self.grade_box.toggle_readonly_on()


            self.completed_widgets.append((self.percentage_label,self.percentage_box))
            self.completed_widgets.append((self.grade_label,self.grade_box))    

            self.update_grade_and_percentage()


            self.completed_date_label = ctk.CTkLabel(self.completedinner_frame,text="Completed date")

            self.completed_date_input = CommonFunctions.NewEntry(self.completedinner_frame,placeholder_text="Not selected")
            self.completed_date_input.toggle_readonly_on()
            self.completed_widgets.append((self.completed_date_label,self.completed_date_input))

            self.update_date_entry()


            self.date_buttons_frame = ctk.CTkFrame(self.completedinner_frame,fg_color="transparent")
            self.date_buttons_frame.columnconfigure(0,weight=1)
            self.date_buttons_frame.columnconfigure(1,weight=1)




            self.select_completed_date_button = ctk.CTkButton(self.date_buttons_frame,text="Select",command=self.select_completed_date,width=14)
            self.select_completed_date_button.grid(row=0,column=0,sticky="new",padx=(0,2))


            self.reset_completed_date_button = ctk.CTkButton(self.date_buttons_frame,text="Reset",command=self.reset_completed_date,width=14)
            self.reset_completed_date_button.grid(row=0,column=1,sticky="new",padx=(2,0))


            row += 1

            row += 1
            self.document_button_rows = row

            self.setup_document_buttons()



        if self.type == "update":
            self.confirm_button = ctk.CTkButton(self.heading_frame,text="Save",width=15,command=lambda:self.update_or_save())
            self.delete_button = ctk.CTkButton(self.heading_frame,text="Delete",width=15,command=lambda:self.delete_paper_command())
            self.reset_button = ctk.CTkButton(self.heading_frame,text="Reset / Refresh",width=15,command=lambda:self.refresh_page_command())
            self.delete_button.grid(row=4,column=0,padx=15,pady=15,sticky="new")
            self.reset_button.grid(row=3,column=0,padx=15,pady=15,sticky="new")


            header_text="Editing:"
        elif self.type == "create":
            self.confirm_button = ctk.CTkButton(self.heading_frame,text="Create",width=15,command=lambda:self.update_or_save())
            header_text="New document"
        
        self.heading_frame.columnconfigure(0,weight=1)


        self.name_label = ctk.CTkEntry(self.heading_frame,fg_color="transparent",border_width=0,font=(None,14))

        self.name_label.grid(row=1,column=0,sticky="new",padx=9,pady=(0,15))

        self.setup_name_label()
        
        
        header=ctk.CTkLabel(self.heading_frame, text=header_text,font=(None,26))
        header.grid(row=0,column=0,columnspan=1,sticky="nw",padx=15,pady=(15,2))



        self.confirm_button.grid(row=2,column=0,padx=15,pady=15,sticky="new")


    def delete_paper_command(self):
        
        confirm = tk.messagebox.askyesno(title="Delete item",message="Do you with to delete this item. This cannot be undone. Any documents stored in this item will be permenantly deleted")
        if confirm:
            self.mainline_obj.frames["DocumentViewerPage"].closeopentab()
            self.paper_obj.delete_past_paper_obj()
            self.mainline_obj.reset_frame("MainPage")




    def refresh_page_command(self):
        confirm = True
        if self.check_unsaved_changes()==True:
            confirm = tk.messagebox.askyesno(title="Reset tab",message="Tab will be reset to last saved state. All changes since then will be lost. \n\nDo you wish to continue?")

        if confirm:
            self.mainline_obj.frames["DocumentViewerPage"].reset_tab(self.UI_tab_link,self.paper_obj)
            self.mainline_obj.reset_frame("MainPage")


    def update_or_save(self,ignore_automatics=False,refresh_page = True):
        master_err_msg = "Datatype errors found:\n"
        invalid = False
        for input_tracker in self.input_trackers:
            err_msg = input_tracker.apply_to_setter()
            if err_msg != "":
                master_err_msg += " - " + err_msg + "\n"
                invalid = True
        
        if invalid == True:
            raise custom_errors.ExceptionWarning(master_err_msg,"Input errors found")
            
        self.paper_obj.set_completed_date(self.completed_date)
        try:

            if self.type == "update":
                self.update_database(refresh_page=refresh_page)
                self.setup_name_label()
                self.update_grade_and_percentage()
                self.update_date_entry()
                #self.mainline_obj.frames["DocumentViewerPage"].change_tab_name(self.UI_tab_link,self.paper_obj.get_name())

            if self.type == "create":
                self.save_database(refresh_page=refresh_page)

                self.mainline_obj.frames["DocumentViewerPage"].reset_tab(self.UI_tab_link,self.paper_obj)
        
        except custom_errors.ExceptionWarning as e:
            # handled by exception class
            return


        if refresh_page:
            for input_tracker in self.input_trackers:
                input_tracker.refresh()

            self.refresh_document_buttons("questionpaper")
            self.refresh_document_buttons("markscheme")
            self.refresh_document_buttons("attachment")

            self.mainline_obj.reset_frame("MainPage")

    def check_unsaved_changes(self):
        for tracker in self.input_trackers:
            if tracker.unsaved():
                return True
        else:
            return False

    def destroyer(self):
        """ Handle program exit - will close all windows and command lines to prevent the program from remaining open in the background"""
        #root.quit()
        ##root.destroy()
        #sys.exit()
        self.update_or_save(refresh_page=False)
        self.toplevel.destroy()


    def __init__(self, mainline_obj, scrollable_frame, paper_obj=None, type="update",tab_link="",new_document=False):
        super().__init__(scrollable_frame)
        
        if paper_obj == None:
            paper_obj = mainline_obj.db_object.create_new_row()
        self.all_trackers=[]
        self.new_document=new_document
        self.mainline_obj=mainline_obj
        self.paper_obj=paper_obj
        self.type=type
        self.completed_date=None

        self.UI_tab_link = tab_link
        
        # handle program exit protocol
        #root.protocol("WM_DELETE_WINDOW", self.destroyer)
        #toplevel.protocol("WM_DELETE_WINDOW", self.destroyer)

        self.terminology = values_and_rules.get_terminology(self.paper_obj.get_course_type())

        self.setup_page()
        
        scrollable_frame.update()

        self.grid(row=0,column=0,sticky="nsew")
        self.grid(row=0,column=0)

        self.grid_rowconfigure(1,weight=1)
        self.grid_columnconfigure(1,weight=1)

        self.update()
        #toplevel.geometry(f"{self.winfo_width()+25}x{self.winfo_height()-25}+25+25")


