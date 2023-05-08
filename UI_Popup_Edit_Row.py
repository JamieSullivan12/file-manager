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
            self.entry = scrolledtext.ScrolledText(frame, wrap=tk.WORD,width=8,height=4)
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

            self.label.grid(row=override_frame_row,column=0,sticky="nw",pady=(inner_padding,0))
            self.entry.grid(row=override_frame_row,column=1,sticky="new",pady=(inner_padding,0))
            self.entry.xview_moveto(1)

        else:
            if self.current_value == "":
                self.entry_handle_focus_out("")
            self.entry.grid(row=override_frame_row,column=0,sticky="new",pady=(inner_padding,0))
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

    class DocumentButton(ctk.CTkFrame):
        class Row(ctk.CTkFrame):

            def get_unique_identifier(self):
                return self.identifier_getter(index = self.index)

            def change_identifier(self,value,event=None):
                if value != self.identifier_default_text:
                    self.identifier_setter(value,self.index)

            def change_path(self,value,event=None):
                self.path_setter(value,self.index)

            def delete_path(self):
                continue_delete = tk.messagebox.askyesno(message="Are you sure you would like to delete this path?")
                if continue_delete:
                    self.deleted = True
                    #print(self.path_dictionary["valid"],type(self.path_dictionary["valid"]))
                    if self.path_dictionary["valid"] == False:
                        return_msg = self.document_button.parent.paper_obj.delete_path(self.document_button.type,self.index, ignore_removed_pdf = True)
                    else:
                        return_msg = self.document_button.parent.paper_obj.delete_path(self.document_button.type,self.index)
                    if isinstance(return_msg, dict):
                        tk.messagebox.showinfo(message=f"Successfully deleted {return_msg['path']}")
                        if self.document_button.parent.type == "update":
                            self.document_button.parent.paper_obj.update_database(pdf_files_only=True)
                        #self.document_button.parent.refresh_document_buttons()
                    else:
                        tk.messagebox.showerror(message=f"An unknown error occured\n\n{str(return_msg)}")
                        if self.document_button.parent.type == "update":
                            self.document_button.parent.paper_obj.update_database(pdf_files_only=True)
                        #self.document_button.parent.refresh_document_buttons()
                    #self.document_button.parent.update_or_save(ignore_automatics=True)
                    self.document_button.parent.refresh_document_buttons()

            def identifier_change(self):
                self.document_button.parent.paper_obj.update_database(pdf_files_only=True)
                self.document_button.parent.refresh_document_buttons()


            def identifier_input_event(self,event):
                try:self.identifier_save_button.grid_forget()
                except Exception as e:
                    print(e)
                if self.identifier_input.has_changed():
                    self.identifier_save_button.grid(row=self.row,column=3,pady=10,padx=2,sticky="new")


            def __init__(self, document_button, path_dictionary, index, identifier_getter, path_setter, identifier_setter, row):
                super().__init__(document_button,fg_color="transparent")
                self.index=index
                self.deleted=False
                self.identifier_setter=identifier_setter
                self.path_setter=path_setter
                self.identifier_getter=identifier_getter
                self.document_button=document_button
                self.row=row

                self.columnconfigure(0,weight=1)
                self.columnconfigure(1,weight=10)
                self.columnconfigure(2,weight=2)
                self.columnconfigure(3,weight=2)
                self.columnconfigure(4,weight=2)
                self.columnconfigure(5,weight=2)

                button_width = 20
                self.path_dictionary = path_dictionary
                #self.change_path_button = ctk.CTkButton(self,text="Save",width=button_width,command=lambda:document_button.parent.paper_obj.browse_file_input(document_button.type,set_function_index=self.index,completefunction=self.document_button.parent.mainline_obj.frames["MainPage"].populate_treeview()))
                #self.change_path_button.grid(row=row,column=3,sticky="new",padx=2,pady=10)

                self.delete_path_button = ctk.CTkButton(self,text="Remove",width=button_width,command=lambda:self.delete_path())
                self.delete_path_button.grid(row=row,column=4,sticky="new",padx=2,pady=10)

                #self.view_button = ctk.CTkButton(self,text="View",command=lambda:self.document_button.parent.view(self.path_dictionary["path"],""))
                #self.view_button.grid(row=row,column=3,sticky="nw",padx=5,pady=10)
                self.open_button = ctk.CTkButton(self,text="Open PDF",width=button_width,command=lambda:self.document_button.parent.open(self.path_dictionary["path"]))
                self.open_button.grid(row=row,column=5,sticky="new",padx=2,pady=10)


                #self.label_path = ctk.CTkLabel(self,text=path_dictionary["path"] + "\t(Valid " + str(path_dictionary["valid"]) + ")")

                self.number_label = ctk.CTkLabel(self,text=f"{index+1}.")
                self.number_label.grid(row=row,column=0,sticky="nw",pady=10)

                self.label_path = ctk.CTkEntry(self)
                self.label_path.insert(0,path_dictionary["path"])
                self.label_path.configure(state='readonly')
                self.label_path.grid(row=row,column=1,sticky="new",padx=(10,2),pady=10)
                

                self.identifier_default_text = "Path extension"

                self.identifier_input = CreateInput(self,self.identifier_default_text,getter=self.get_unique_identifier,setter=self.change_identifier,label_inside=True,bind_on_key_release=self.identifier_input_event)
                self.identifier_input.grid(row=row,column=2,padx=2,pady=10,sticky="new")
                self.identifier_save_button = ctk.CTkButton(self,text="Save",width=button_width,command=self.identifier_change)

        def add_path(self):
            self.parent.paper_obj.browse_file_input(self.type,custom_identifier="")
            if self.parent.type == "update":
                self.parent.paper_obj.update_database(pdf_files_only=True)
            #self.parent.refresh_document_buttons()
            #self.parent.update_or_save(ignore_automatics=True)
            self.parent.refresh_document_buttons()



        def __init__(self,parent,frame,type,name,top_level_getter, identifier_getter, path_setter, identifier_setter):
            super().__init__(frame,fg_color="transparent")
            self.type=type
            self.name=name
            self.parent = parent
            self.path_setter=path_setter

            self.columnconfigure(0,weight=1)

            self.add_button = ctk.CTkButton(self,text=f"Add {name}",command=lambda: self.add_path(),width=50)
            self.add_button.grid(row=0,column=0, sticky="new",pady=(10,0))

            #self.identifier_entry = ctk.CTkEntry(self,width=30)
            #self.identifier_entry.grid(row=0,column=1,sticky="nw",padx=0,pady=(10,0))

            
            self.file_paths = top_level_getter()
            for index,path_dictionary in enumerate(self.file_paths):
                row = self.Row(self,path_dictionary,index,identifier_getter, path_setter, identifier_setter,index+1)
                row.grid(row=index+1,column=0,sticky="new")


    def open(self,path, event=None):
        cwd = os.getcwd()
        subprocess.Popen([os.path.join(cwd,path)],shell=True)

       

    def view(self,path,event=None):

        self.PDFPopUp(self,path)
    
    def refresh_page(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        self.paper_obj.update_object()
        self.setup_page()

    def update_database(self,event=None,refresh_page = True):
        self.paper_obj.update_database()
        #if refresh_page:
        #    self.refresh_page()
        #self.mainline_obj.resetwindows("MainPage")
        #self.parent.populate_treeview()

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
            #self.refresh_page()
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
        #print(date, type(date))
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
 
    def setup_document_buttons(self):
        row = 1

        self.directories_frame.columnconfigure(0,weight=1)
        self.original_document_row = self.DocumentButton(self,self.directories_frame,"original",self.terminology["Original"],self.paper_obj.get_original,self.paper_obj.get_original_identifier,self.paper_obj.set_original_path,self.paper_obj.set_original_identifier)
        self.original_document_row.grid(row=row,column=0,columnspan=3,padx=self.inner_x_padding,sticky="new")

        row += 1
        self.markscheme_document_row = self.DocumentButton(self,self.directories_frame,"markscheme",self.terminology["Markscheme"],self.paper_obj.get_markscheme,self.paper_obj.get_markscheme_identifier,self.paper_obj.set_markscheme_path,self.paper_obj.set_markscheme_identifier)
        self.markscheme_document_row.grid(row=row,column=0,columnspan=3,padx=self.inner_x_padding,sticky="new")

        row += 1
        self.otherattachments_document_row = self.DocumentButton(self,self.directories_frame,"otherattachments","Other Attachments",self.paper_obj.get_otherattachments,self.paper_obj.get_otherattachments_identifier,self.paper_obj.set_otherattachments_path,self.paper_obj.set_otherattachments_identifier)
        self.otherattachments_document_row.grid(row=row,column=0,columnspan=3,padx=self.inner_x_padding,sticky="new")

        row += 1
        return row
    
    def refresh_document_buttons(self):
        self.original_document_row.destroy()
        self.markscheme_document_row.destroy()
        self.otherattachments_document_row.destroy()
        self.setup_document_buttons()


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

        row = 0
        for grade_boundary in grade_boundaries_list:
            boundary_input = CreateInput(gradeboundaries_inner_frame,self.terminology["Grade"]+f" {grade_boundary}",getter=self.paper_obj.get_grade_boundary,setter=self.paper_obj.set_grade_boundary,getter_param=grade_boundary,setter_param=grade_boundary,override_frame=True,override_frame_row=row,inner_padding=5)
            #boundary_input.grid(row=row,column=0,padx=20,pady=5,sticky="new")
            row += 1
        
        maxmark_input = CreateInput(gradeboundaries_inner_frame,"Maximum mark",getter=self.paper_obj.get_gbmax,setter=self.paper_obj.set_gbmax,override_frame=True,override_frame_row=row,inner_padding=5)
        #maxmark_input.grid(row=row,column=0,padx=20,pady=5,sticky="new")





    def setup_page(self):

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
        
        
        row = 0
        column = 0
        

        metadata_inner_frame = ctk.CTkFrame(self.metadata_frame,fg_color="transparent")
        metadata_inner_frame.grid(row=1,column=0,padx=self.inner_x_padding,pady=(10,self.inner_y_padding),sticky="new")

        metadata_inner_frame.columnconfigure(0,weight=1)
        metadata_inner_frame.columnconfigure(1,weight=1)

        override_name_button = CreateInput(metadata_inner_frame,"Override name",getter=self.paper_obj.get_custom_name,setter=self.paper_obj.set_custom_name,override_frame=True,override_frame_row=row,inner_padding=5)
        # override_name_button.grid(row=row,column=column,padx=10,pady=5,sticky="new")
        row += 1
        
        year_button = CreateInput(metadata_inner_frame,"Year",getter=self.paper_obj.get_year,setter=self.paper_obj.set_year,override_frame=True,override_frame_row=row,inner_padding=5)
        # year_button.grid(row=row,column=column,padx=10,pady=5,sticky="new")
        row += 1

        if self.terminology["show_session"]:
            session_button = CreateInput(metadata_inner_frame,self.terminology["Session"],getter=self.paper_obj.get_session,setter=self.paper_obj.set_session,override_frame=True,override_frame_row=row,inner_padding=5)
            # session_button.grid(row=row,column=column,padx=10,pady=5,sticky="new")
            row += 1
        
        if self.terminology["show_timezone"]:
            timezone_button = CreateInput(metadata_inner_frame,self.terminology["Timezone"],getter=self.paper_obj.get_timezone,setter=self.paper_obj.set_timezone,override_frame=True,override_frame_row=row,inner_padding=5)
            # timezone_button.grid(row=row,column=column,padx=10,pady=5,sticky="new")
            row += 1
        
        if self.terminology["show_paper"]:
            paper_button = CreateInput(metadata_inner_frame,self.terminology["Paper"],getter=self.paper_obj.get_paper,setter=self.paper_obj.set_paper,override_frame=True,override_frame_row=row,inner_padding=5)
            # paper_button.grid(row=row,column=column,padx=10,pady=5,sticky="new")
            row += 1

        if self.terminology["show_subject"]:
            subject_button = CreateInput(metadata_inner_frame,self.terminology["Subject"],getter=self.paper_obj.get_subject,setter=self.paper_obj.set_subject,override_frame=True,override_frame_row=row,inner_padding=5)
            # subject_button.grid(row=row,column=column,padx=10,pady=5,sticky="new")
            row += 1
        
        if self.terminology["show_level"]:
            level_button = CreateInput(metadata_inner_frame,self.terminology["Level"],getter=self.paper_obj.get_level,setter=self.paper_obj.set_level,override_frame=True,override_frame_row=row,inner_padding=5)
            # level_button.grid(row=row,column=column,padx=10,pady=5,sticky="new")
            row += 1

        notes_button = CreateInput(metadata_inner_frame,"Notes",getter=self.paper_obj.get_notes,setter=self.paper_obj.set_notes,override_frame=True,override_frame_row=row,inner_padding=5,scrollable_text = True)
        # notes_button.grid(row=row,column=column,padx=10,pady=5,sticky="new")
        row +=1 

        """
        row += 1
        printed_label=ctk.CTkLabel(self, text= "Printed: " + str(self.paper_obj.get_printed()))
        printed_label.grid(row=row,column=0,columnspan=2,sticky="nw",padx=20,pady=5)

        printed_combo = ttk.Combobox(self, values=["","True","False"],state="readonly")
        printed_combo.grid(row=row,column=column+1,sticky="nw",pady=5,padx=20)
        printed_combo.set(str(self.paper_obj.get_printed()))
        printed_combo.bind("<<ComboboxSelected>>", lambda e: self.dropdown_handler(printed_combo, printed_label, "Printed", self.paper_obj.set_printed,self.paper_obj.get_printed))

        row += 1
        completed_label=ctk.CTkLabel(self, text= "Completed: " + str(self.paper_obj.get_completed()))
        completed_label.grid(row=row,column=0,columnspan=2,sticky="nw",padx=20,pady=5)

        completed_combo = ttk.Combobox(self, values=["","True","False"],state="readonly")
        completed_combo.grid(row=row,column=column+1,sticky="nw",pady=5,padx=20)
        completed_combo.set(str(self.paper_obj.get_completed()))

        completed_combo.bind("<<ComboboxSelected>>", lambda e: self.dropdown_handler(completed_combo, completed_label,"Completed", self.paper_obj.set_completed,self.paper_obj.get_completed))

        row += 1
        partial_label=ctk.CTkLabel(self, text= "Partial: " + str(self.paper_obj.get_partial()))
        partial_label.grid(row=row,column=0,columnspan=2,sticky="nw",padx=20,pady=5)

        partial_combo = ttk.Combobox(self, values=["","True","False"],state="readonly")
        partial_combo.grid(row=row,column=column+1,sticky="nw",pady=5,padx=20)
        partial_combo.set(str(self.paper_obj.get_partial()))

        partial_combo.bind("<<ComboboxSelected>>", lambda e: self.dropdown_handler(partial_combo, partial_label,"Partial", self.paper_obj.set_partial,self.paper_obj.get_partial))        
        


        row += 1

        """

        padx=15
        pady=7


        self.completedinner_frame = ctk.CTkFrame(self.completed_frame,fg_color="transparent")
        self.completedinner_frame.grid(row=1,column=0,columnspan=3,sticky="new",padx=self.inner_x_padding,pady=(10,0))
        self.completedinner_frame.columnconfigure(0,weight=1)
        self.completedinner_frame.columnconfigure(1,weight=1)

        row=0
        mark_button = CreateInput(self.completedinner_frame,"Mark",getter=self.paper_obj.get_mark,setter=self.paper_obj.set_mark,override_frame=True,override_frame_row=row,inner_padding=5)
        #mark_button.grid(row=row,column=0,columnspan=2,padx=padx,pady=pady,sticky="new")
        row += 1

        maximum_button = CreateInput(self.completedinner_frame,"Maximum",getter=self.paper_obj.get_maximum,setter=self.paper_obj.set_maximum,override_frame=True,override_frame_row=row,inner_padding=5)
        #maximum_button.grid(row=row,column=0,columnspan=2,padx=padx,pady=pady,sticky="new")
        row += 1

        #self.percentage_label_text = str(round(float(self.paper_obj.get_percentage()) * 100,1))
        #grade = self.paper_obj.get_grade()
        #if grade == -1:
        #    grade = "None"
        #else:
        #    grade = str(grade)
        #self.percentage_label = ctk.CTkLabel(self.completed_frame, text ="Percentage mark" + self.percentage_label_text + "%\t---\tGrade: " + grade)
        #self.percentage_label.grid(row=row,column=0,sticky="nw",padx=padx,pady=pady,columnspan=2)
        
        
        percentage_button = CreateInput(self.completedinner_frame,"Percentage (calculated)",getter=self.paper_obj.get_percentage_pretty,setter=self.paper_obj.pass_setter,readonly=True,override_frame=True,override_frame_row=row,inner_padding=5)
        row += 1
        grade_button = CreateInput(self.completedinner_frame,"Grade (calculated)",getter=self.paper_obj.get_grade_pretty,setter=self.paper_obj.pass_setter,readonly=True,override_frame=True,override_frame_row=row,inner_padding=5)

        
        row += 1

        self.completed_date_input = CreateInput(self.completedinner_frame,"Completed date",getter=self.paper_obj.get_completed_date_pretty,setter=self.paper_obj.pass_setter,readonly=True,override_frame=True,override_frame_row=row,inner_padding=5)

        row += 1
        #self.completed_date = str(self.paper_obj.get_completed_date())
        #self.select_completed_date_label = ctk.CTkLabel(self.completed_frame, text ="Completed date: \n" + self.completed_date)
        #self.select_completed_date_label.grid(row=row,column=0,sticky="nw",padx=padx,pady=pady)

        self.date_buttons_frame = ctk.CTkFrame(self.completedinner_frame,fg_color="transparent")
        self.date_buttons_frame.grid(row=row,column=1,sticky="new",padx=(0,self.inner_x_padding),pady=(2,self.inner_y_padding))
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

        row = self.setup_document_buttons()



        if self.type == "update":
            self.confirm_button = ctk.CTkButton(self.heading_frame,text="Save all changes",width=30,command=lambda:self.update_or_save())
            header_text="Editing:"
        elif self.type == "create":
            self.confirm_button = ctk.CTkButton(self.heading_frame,text="Save all",width=30,command=lambda:self.update_or_save())
            header_text="Create new document"
        
        self.heading_frame.columnconfigure(0,weight=1)
        name_entry = CreateInput(self.heading_frame,"",self.paper_obj.get_name,self.paper_obj.pass_setter,label_inside=True,readonly=True,entry_fg_color="transparent",entry_border_width=0,entry_font=(None,24),readonly_text_color="gray10")
        name_entry.grid(row=1,column=0,sticky="new",padx=9,pady=(2,15))
        header=ctk.CTkLabel(self.heading_frame, text=header_text,font=(None,26))
        header.grid(row=0,column=0,columnspan=1,sticky="nw",padx=15,pady=(15,2))


        self.confirm_button.grid(row=2,column=0,padx=15,pady=15,sticky="new")

    #def update_documents(self):
    #    self.setup_document_buttons()

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


    def __init__(self, mainline_obj, scrollable_frame, grid_preload=  False, paper_obj=None, type="update",tab_link=""):
        super().__init__(scrollable_frame)
        
        if paper_obj == None:
            paper_obj = mainline_obj.db_object.create_new_row()


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


