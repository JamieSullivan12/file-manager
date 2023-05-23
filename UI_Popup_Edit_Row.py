from email import message
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import modifiable_label,os
from tkdocviewer import *
import subprocess
import pandas as pd
import scrollable_frame
import values_and_rules
import customtkinter as ctk
import autocomplete_with_dropdown

class CreateInput(ctk.CTkFrame):
    def entry_filter_callback(self, sv, filter_type):
        if not self.setter_param == None: self.setter(self.setter_param,self.entry.get())
        else: self.setter(self.entry.get())
    
    def scrolled_text_filter_callback(self,scrolled_text_widget ,filter_type):
        self.entry.update()
        text = self.entry.get("1.0",tk.END)
        if not self.setter_param == None: self.setter(self.setter_param,text)
        else: self.setter(text)

    def set_label(self):
        if not self.getter_param == None: current_value = self.getter(self.getter_param)
        else: current_value = self.getter()

        self.label["text"]=self.text + ": " + str(current_value)

    def entry_handle_focus_in(self,event):
        if self.user_input == False and self.get_entry_value() == self.text:
            self.entry.delete(0, tk.END)
            self.entry.configure(text_color='black')
            self.user_input = True

    def has_changed(self):
        if self.get_entry_value() == self.current_value:
            return False
        else:
            return True
    def get_tuple(self):
        return self.label,self.entry
    def entry_handle_focus_out(self,event):
        if str(self.entry.get()).strip() == "":
            self.entry.delete(0, tk.END)
            self.entry.configure(text_color='grey')
            self.entry.insert(0, self.text)
            self.user_input = False

    def update_value(self,new_value):
        self.entry.configure(state="normal")
        self.entry.delete(0,tk.END)
        self.entry.insert(tk.END,new_value)
        if self.readonly:
            self.entry.configure(state="readonly")
        self.on_entry()

    def get_entry_value(self):
        if self.scrollable_text==False:
            return self.entry.get()
        else:
            return self.entry.get("1.0",tk.END).strip()
            

    def on_entry(self,event=None):
        if self.bind_on_key_release != None:
            self.bind_on_key_release(event)
        if not self.label_inside:
            if self.get_entry_value() != str(self.current_value):
                self.label.configure(text="* "+self.text)
            else:
                self.label.configure(text=self.text)

    def __init__(self, parent_frame, text, getter, setter,scrollable_text=False,getter_param=None,setter_param=None,label_inside=False,override_frame=False,override_frame_row=0,inner_padding=0,readonly=False,bind_on_key_release=None,entry_fg_color = "white",entry_border_width=1,entry_font=(None,12),readonly_text_color="gray40"):
        super().__init__(parent_frame,fg_color="transparent")        
        self.label_inside=label_inside
        self.readonly=readonly
        self.user_input = False
        self.text=text
        self.getter=getter
        self.setter=setter
        self.setter_param=setter_param
        self.getter_param=getter_param
        self.scrollable_text=scrollable_text
        self.bind_on_key_release=bind_on_key_release
        self.readonly_text_color=readonly_text_color

        if override_frame == True:
            frame = parent_frame
        else:
            frame = self

        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        


        if not self.getter_param == None: self.current_value = self.getter(self.getter_param)
        else: self.current_value = self.getter()


        if scrollable_text:
            self.entry = scrolledtext.ScrolledText(frame, wrap=tk.WORD,width=4,height=4)
            self.entry.bind("<KeyRelease>", lambda e: self.scrolled_text_filter_callback(self.entry,type))
            self.entry.insert(tk.END, self.current_value)
        else:
            # create and place an Entry box into the location where the label was deleted
            self.current_value = str(self.current_value)

            entry_tracker = tk.StringVar()
            entry_tracker.trace("w", lambda name, index, mode, sv=entry_tracker: self.entry_filter_callback(entry_tracker, type))
        
            self.entry = ctk.CTkEntry(frame,textvariable=entry_tracker,fg_color=entry_fg_color,border_width=entry_border_width,font=entry_font)
            self.entry.insert(tk.END, self.current_value)

            #self.set_label()
        # pre-insert the value from the getter function
        
        if not label_inside:

            self.label = ctk.CTkLabel(frame,text=self.text)

            #self.label.grid(row=override_frame_row,column=0,sticky="nw",pady=(inner_padding,0))
            self.entry.grid(row=override_frame_row,column=1,sticky="new",pady=(inner_padding,0))
            self.entry.xview_moveto(1)

        else:
            if self.current_value == "":
                self.entry_handle_focus_out("")
            #self.entry.grid(row=override_frame_row,column=0,sticky="new",pady=(inner_padding,0))
            self.entry.bind("<FocusIn>", self.entry_handle_focus_in)
            self.entry.bind("<FocusOut>", self.entry_handle_focus_out)



        if readonly:
            self.entry.configure(state="readonly",text_color=readonly_text_color)

        self.entry.bind("<KeyRelease>",self.on_entry)


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
                self.document_frame.parent.paper_obj.update_database(pdf_files_only=True)
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
                    self.label_path.insert(0,"Unable to find file in heirarchy")
                self.label_path.configure(state='readonly')
   
                self.make_grid(critical=self.document_frame.parent.critical)
              
        def add_path(self):
            self.parent.paper_obj.browse_file_input(self.type)
            if self.parent.type == "update":
                self.parent.paper_obj.update_database(pdf_files_only=True)

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

    def update_printed(self,refresh_page=True):
        
        change = tk.messagebox.askyesno(message="Would you like to change the Printed field to TRUE?")
        if change:
            self.paper_obj.set_printed(True)
            self.update_database(refresh_page=refresh_page)
            self.paper_obj.set_ignore_update(False)
        else:
            self.paper_obj.set_ignore_update(True)

    def update_completed(self,refresh_page=True):
        
        change = tk.messagebox.askyesno(message="Would you like to change the Completed field to TRUE?")
        if change:
            self.paper_obj.set_completed(True)
            self.update_database(refresh_page=refresh_page)
            #self.refresh_page()
            self.paper_obj.set_ignore_update(False)
        else:
            self.paper_obj.set_ignore_update(True)

   

    def completed_date_popup(self, date):
        self.paper_obj.set_completed_date(pd.Timestamp(date))
        #self.select_completed_date_label.configure(text="Completed date: \n" + str(self.paper_obj.get_completed_date()))
        self.completed_date_input.update_value(self.paper_obj.get_completed_date_pretty())

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
        print("setup",type)
        if type == "" or type=="questionpaper":
            self.original_document_row = self.DocumentsFrame(self,self.directories_frame,"questionpaper",self.terminology["Original"],self.paper_obj.get_questionpaper_documents())
            self.original_document_row.grid(row=1,column=0,columnspan=3,padx=self.inner_x_padding,sticky="new")
        if type == "" or type=="markscheme":
            self.markscheme_document_row = self.DocumentsFrame(self,self.directories_frame,"markscheme",self.terminology["Markscheme"],self.paper_obj.get_markscheme_documents())
            self.markscheme_document_row.grid(row=2,column=0,columnspan=3,padx=self.inner_x_padding,sticky="new")
        if type == "" or type=="attachment":
            self.otherattachments_document_row = self.DocumentsFrame(self,self.directories_frame,"attachment","Attachments",self.paper_obj.get_attachment_documents())
            self.otherattachments_document_row.grid(row=3,column=0,columnspan=3,padx=self.inner_x_padding,sticky="new")

    
    def refresh_document_buttons(self,type=""):
        print("delete")
        if type=="questionpaper" or type=="":
            self.original_document_row.destroy()
        if type=="markscheme" or type=="":
            self.markscheme_document_row.destroy()
        if type=="attachment" or type=="":
            self.otherattachments_document_row.destroy()
        self.setup_document_buttons(type)


    def reset_completed_date(self):
        import numpy as np
        self.completed_date_popup(np.datetime64('NaT'))
        #self.paper_obj.set_completed_date(np.datetime64('NaT'))

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
            entry = CreateInput(gradeboundaries_inner_frame,self.terminology["Grade"]+f" {grade_boundary}",getter=self.paper_obj.get_grade_boundary,setter=self.paper_obj.set_grade_boundary,getter_param=grade_boundary,setter_param=grade_boundary,override_frame=True,override_frame_row=row,inner_padding=5)
            self.grade_boundary_entries.append(entry.get_tuple())
            #boundary_input.grid(row=row,column=0,padx=20,pady=5,sticky="new")
            row += 1
        
        entry = CreateInput(gradeboundaries_inner_frame,"Maximum mark",getter=self.paper_obj.get_gbmax,setter=self.paper_obj.set_gbmax,override_frame=True,override_frame_row=row,inner_padding=5)
        self.grade_boundary_entries.append(entry.get_tuple())
        #maxmark_input.grid(row=row,column=0,padx=20,pady=5,sticky="new")



    def create_entry_box(self,master_frame,row,labelcolumn,labelpadx=(0,0),entrypadx=(0,0),pady=(0,0),title="",autofill=[],getter=None,setter=None):
        
        def entry_insert_event(entry,setter):
            setter(entry.get())


        import label as cl
        label = cl.Label(master_frame,text=title,font=self.mainline_obj.normal_label_font, justify="left")
        #label.grid(row=row,column=labelcolumn,sticky="new",padx=(0,5),pady=(0,5))
        var = tk.StringVar()
        var.set(getter())

        entry = autocomplete_with_dropdown.Autocomplete(master_frame,options=autofill,textvariable=var,func="contains",hitlimit=5)


        #entry.grid(row=row,column=labelcolumn+1,sticky="ne",pady=(0,5))
        
        entry.bind("<KeyRelease>",lambda e:entry_insert_event(entry,setter))
        entry.bind("<Tab>",lambda e:entry_insert_event(entry,setter))
        entry.bind("<Return>",lambda e:entry_insert_event(entry,setter))

        return label,entry



    def set_subject_intervention(self,value):

        self.paper_obj.set_subject(value)  
            
    def grid_apply(self,item,rc,cc,c_mod,**kwargs):
        try:
            item.grid_forget()
        except Exception as e:
            pass

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
        rc,cc=self.grid_apply(self.year_label,rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
        rc,cc=self.grid_apply(self.year_entry,rc=rc,cc=cc,c_mod=c_mod,sticky="new")
        rc,cc=self.grid_apply(self.session_label,rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
        rc,cc=self.grid_apply(self.session_entry,rc=rc,cc=cc,c_mod=c_mod,sticky="new")
        rc,cc=self.grid_apply(self.timezone_label,rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
        rc,cc=self.grid_apply(self.timezone_entry,rc=rc,cc=cc,c_mod=c_mod,sticky="new")
        rc,cc=self.grid_apply(self.paper_label,rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
        rc,cc=self.grid_apply(self.paper_entry,rc=rc,cc=cc,c_mod=c_mod,sticky="new")
        rc,cc=self.grid_apply(self.subject_label,rc=rc,cc=cc,c_mod=c_mod,sticky="nw")
        rc,cc=self.grid_apply(self.subject_entry,rc=rc,cc=cc,c_mod=c_mod,sticky="new")
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


    def setup_page(self):
        self.critical=False
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)

        self.heading_frame = ctk.CTkFrame(self,fg_color=self.mainline_obj.colors.bubble_background)
        self.heading_frame.grid(row=0,column=0,columnspan=1,sticky="nsew",padx=(20,10),pady=(20,10))

        subheading_font = (None,18)
        self.inner_x_padding = 10
        self.inner_y_padding = 20
        

        self.metadata_frame = ctk.CTkFrame(self,fg_color=self.mainline_obj.colors.bubble_background)
        self.metadata_frame.grid(row=0,column=1,columnspan=1,sticky="nsew",padx=(10,20),pady=(20,10))
        self.metadata_frame.columnconfigure(0,weight=1)
        self.metadatasubheading = ctk.CTkLabel(self.metadata_frame,text="Meta data",font=subheading_font)
        self.metadatasubheading.grid(row=0,column=0,padx=self.inner_x_padding,pady=(10,0),sticky="nw")


        
        row = 0
        column = 0
        

        metadata_inner_frame = ctk.CTkFrame(self.metadata_frame,fg_color="transparent")
        metadata_inner_frame.grid(row=1,column=0,padx=self.inner_x_padding,pady=(10,self.inner_y_padding),sticky="new")

        metadata_inner_frame.columnconfigure(0,weight=1)
        metadata_inner_frame.columnconfigure(1,weight=1)

        #override_name_button = CreateInput(metadata_inner_frame,"Override name",getter=self.paper_obj.get_custom_name,setter=self.paper_obj.set_custom_name,override_frame=True,override_frame_row=row,inner_padding=5)
        self.overridename_label,self.overridename_entry=self.create_entry_box(metadata_inner_frame,row=row,labelcolumn=0,labelpadx=(10,5),entrypadx=(5,10),pady=5,title="Override name",autofill=[],getter=self.paper_obj.get_custom_name,setter=self.paper_obj.set_custom_name)

        # override_name_button.grid(row=row,column=column,padx=10,pady=5,sticky="new")
        row += 1

        self.year_label,self.year_entry=self.create_entry_box(metadata_inner_frame,row=row,labelcolumn=0,labelpadx=(10,5),entrypadx=(5,10),pady=5,title=self.terminology["Year"],autofill=[],getter=self.paper_obj.get_year,setter=self.paper_obj.set_year)
        row += 1

        if self.terminology["show_session"]:

            self.session_label,self.session_entry=self.create_entry_box(metadata_inner_frame,row=row,labelcolumn=0,labelpadx=(10,5),entrypadx=(5,10),pady=5,title=self.terminology["Session"],autofill=list(self.terminology["dict_session"].values()),getter=self.paper_obj.get_session,setter=self.paper_obj.set_session)

            row += 1


        if self.terminology["show_timezone"]:

            self.timezone_label,self.timezone_entry=self.create_entry_box(metadata_inner_frame,row=row,labelcolumn=0,labelpadx=(10,5),entrypadx=(5,10),pady=5,title=self.terminology["Timezone"],autofill=list(self.terminology["dict_timezone"].values()),getter=self.paper_obj.get_timezone,setter=self.paper_obj.set_timezone)

            row += 1
        
        if self.terminology["show_paper"]:

            self.paper_label,self.paper_entry=self.create_entry_box(metadata_inner_frame,row=row,labelcolumn=0,labelpadx=(10,5),entrypadx=(5,10),pady=5,title=self.terminology["Paper"],autofill=list(self.terminology["dict_paper"].values()),getter=self.paper_obj.get_paper,setter=self.paper_obj.set_paper)

            row += 1

        if self.terminology["show_subject"]:

            self.subject_label,self.subject_entry=self.create_entry_box(metadata_inner_frame,row=row,labelcolumn=0,labelpadx=(10,5),entrypadx=(5,10),pady=5,title=self.terminology["Subject"],autofill=list(self.mainline_obj.settings.subjects.values()),getter=self.paper_obj.get_subject,setter=self.set_subject_intervention)
            
            row += 1
        
        if self.terminology["show_level"]:
 
            self.level_label,self.level_entry=self.create_entry_box(metadata_inner_frame,row=row,labelcolumn=0,labelpadx=(10,5),entrypadx=(5,10),pady=5,title=self.terminology["Level"],autofill=list(self.terminology["dict_level"].values()),getter=self.paper_obj.get_level,setter=self.paper_obj.set_level)

            row += 1


        row +=1 



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

            #self.confirm_frame = ctk.CTkFrame(self,fg_color=self.mainline_obj.colors.bubble_background)
            #self.confirm_frame.grid(row=3,column=1,columnspan=1,sticky="nsew",padx=15,pady=15)

            


            self.create_gradeboundary_box()
            


            self.completedinner_frame = ctk.CTkFrame(self.completed_frame,fg_color="transparent")
            self.completedinner_frame.grid(row=1,column=0,columnspan=3,sticky="new",padx=self.inner_x_padding,pady=(10,0))
            self.completedinner_frame.columnconfigure(0,weight=1)
            self.completedinner_frame.columnconfigure(1,weight=1)

            self.completed_widgets=[]

            row=0
            mark_button = CreateInput(self.completedinner_frame,"Mark",getter=self.paper_obj.get_mark,setter=self.paper_obj.set_mark,override_frame=True,override_frame_row=row,inner_padding=5)
            self.completed_widgets.append(mark_button.get_tuple())
            row += 1

            maximum_button = CreateInput(self.completedinner_frame,"Maximum",getter=self.paper_obj.get_maximum,setter=self.paper_obj.set_maximum,override_frame=True,override_frame_row=row,inner_padding=5)
            self.completed_widgets.append(maximum_button.get_tuple())
            row += 1

            
            percentage_button = CreateInput(self.completedinner_frame,"Percentage (calculated)",getter=self.paper_obj.get_percentage_pretty,setter=self.paper_obj.pass_setter,readonly=True,override_frame=True,override_frame_row=row,inner_padding=5)
            self.completed_widgets.append(percentage_button.get_tuple())
            row += 1
            grade_button = CreateInput(self.completedinner_frame,"Grade (calculated)",getter=self.paper_obj.get_grade_pretty,setter=self.paper_obj.pass_setter,readonly=True,override_frame=True,override_frame_row=row,inner_padding=5)
            self.completed_widgets.append(grade_button.get_tuple())
            
            row += 1

            self.completed_date_input = CreateInput(self.completedinner_frame,"Completed date",getter=self.paper_obj.get_completed_date_pretty,setter=self.paper_obj.pass_setter,readonly=True,override_frame=True,override_frame_row=row,inner_padding=5)
            self.completed_widgets.append(self.completed_date_input.get_tuple())
            row += 1


            self.date_buttons_frame = ctk.CTkFrame(self.completedinner_frame,fg_color="transparent")
            self.date_buttons_frame.columnconfigure(0,weight=1)
            self.date_buttons_frame.columnconfigure(1,weight=1)




            self.select_completed_date_button = ctk.CTkButton(self.date_buttons_frame,text="Select",command=self.select_completed_date,width=14)
            self.select_completed_date_button.grid(row=0,column=0,sticky="new",padx=(0,2))


            self.reset_completed_date_button = ctk.CTkButton(self.date_buttons_frame,text="Reset",command=self.reset_completed_date,width=14)
            self.reset_completed_date_button.grid(row=0,column=1,sticky="new",padx=(2,0))


            row += 1
            self.open_directory_button = ctk.CTkButton(self.directories_frame,text="Open File Directory",command=self.paper_obj.open_file_directory,width=24)
            self.open_directory_button.grid(row=row,column=column,sticky="nw",padx=20,pady=pady)

            row += 1
            self.document_button_rows = row

            self.setup_document_buttons()



        if self.type == "update":
            self.confirm_button = ctk.CTkButton(self.heading_frame,text="Save",width=15,command=lambda:self.update_or_save())
            self.delete_button = ctk.CTkButton(self.heading_frame,text="Delete",width=15,command=lambda:self.delete_paper_command())
            self.reset_button = ctk.CTkButton(self.heading_frame,text="Reset",width=15,command=lambda:self.refresh_page_command())
            self.delete_button.grid(row=4,column=0,padx=15,pady=15,sticky="new")
            self.reset_button.grid(row=3,column=0,padx=15,pady=15,sticky="new")


            header_text="Editing:"
        elif self.type == "create":
            self.confirm_button = ctk.CTkButton(self.heading_frame,text="Create",width=15,command=lambda:self.update_or_save())
            header_text="New document"
        
        self.heading_frame.columnconfigure(0,weight=1)

        name_label = ctk.CTkEntry(self.heading_frame,fg_color="transparent",border_width=0,font=(None,14))
        name_label.insert(0,self.paper_obj.get_name())
        name_label.configure(state="readonly")
        name_label.grid(row=1,column=0,sticky="new",padx=9,pady=(0,15))

        #name_entry = CreateInput(self.heading_frame,"",self.paper_obj.get_name,self.paper_obj.pass_setter,label_inside=True,readonly=True,entry_fg_color="transparent",entry_border_width=0,entry_font=(None,24),readonly_text_color="gray10")
        #name_entry.grid(row=1,column=0,sticky="new",padx=9,pady=(2,15))
        header=ctk.CTkLabel(self.heading_frame, text=header_text,font=(None,26))
        header.grid(row=0,column=0,columnspan=1,sticky="nw",padx=15,pady=(15,2))


        self.confirm_button.grid(row=2,column=0,padx=15,pady=15,sticky="new")


    def delete_paper_command(self):
        
        confirm = tk.messagebox.askyesno(title="Delete item",message="Do you with to delete this item. This cannot be undone. Any documents stored in this item will be permenantly deleted")
        if confirm:
            self.mainline_obj.frames["DocumentViewerPage"].closeopentab()
            self.paper_obj.delete_item()
            self.mainline_obj.resetmainpage()




    def refresh_page_command(self):
        confirm = tk.messagebox.askyesno(title="Reset tab",message="Resetting this tab will not save any changes you made. Do you wish to continue?")
        if confirm:
            self.mainline_obj.frames["DocumentViewerPage"].reset_tab(self.UI_tab_link,self.paper_obj)
            self.mainline_obj.resetmainpage()


    def update_or_save(self,ignore_automatics=False,refresh_page = True):
        if self.type == "update":
            self.update_database(refresh_page=refresh_page)
        if self.type == "create":
            self.save_database(refresh_page=refresh_page)
            self.type = "update"
            ignore_automatics=True

        if ignore_automatics == False:
            ignore = self.paper_obj.get_ignore_update()

            if not ignore and ((self.paper_obj.get_percentage() != "" and float(self.paper_obj.get_percentage()) != 0) or type(self.paper_obj.get_completed_date()) == pd._libs.tslibs.timestamps.Timestamp)  and self.paper_obj.get_printed() == False:
                self.update_printed(refresh_page=False)
            
            if not ignore and (self.paper_obj.get_percentage() != "" and float(self.paper_obj.get_percentage()) != 0) and self.paper_obj.get_completed() == False:
                self.update_completed(refresh_page=False)
            if not ignore and self.paper_obj.get_completed() == True and type(self.paper_obj.get_completed_date()) != pd._libs.tslibs.timestamps.Timestamp:
                self.update_completed_date(refresh_page=False)
        
        if refresh_page:
            self.mainline_obj.frames["DocumentViewerPage"].reset_tab(self.UI_tab_link,self.paper_obj)
            self.mainline_obj.resetmainpage()


    def destroyer(self):
        """ Handle program exit - will close all windows and command lines to prevent the program from remaining open in the background"""
        #root.quit()
        ##root.destroy()
        #sys.exit()
        self.update_or_save(refresh_page=False)
        self.toplevel.destroy()


    def __init__(self, mainline_obj, scrollable_frame, grid_preload=  False, paper_obj=None, type="update",tab_link="",new_document=False):
        super().__init__(scrollable_frame)
        
        if paper_obj == None:
            paper_obj = mainline_obj.db_object.create_new_row()

        self.new_document=new_document
        self.mainline_obj=mainline_obj
        self.paper_obj=paper_obj
        self.type=type

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


