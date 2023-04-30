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


class UIPopupEditRow(ttk.Frame):
    
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
            

            open_pdf_button = ttk.Button(self,text="Open PDF",command=self.open_pdf)
            open_pdf_button.grid(row=0,column=0)

            # Create a DocViewer widget
            v = DocViewer(self, width=900,height=850)
            v.grid(row=1, column = 0, sticky="nsew")



            cwd = os.getcwd()

            # Display some document
            v.display_file(os.path.join(cwd,path))

    class DocumentButton(ttk.Frame):
        class Row(ttk.Frame):

            def get_unique_identifier(self):
                return self.identifier_getter(index = self.index)

            def change_identifier(self,value,event=None):
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
                    self.document_button.parent.update_or_save(ignore_automatics=True)


            def __init__(self, document_button, path_dictionary, index, identifier_getter, path_setter, identifier_setter, row):
                super().__init__(document_button)
                self.index=index
                self.deleted=False
                self.identifier_setter=identifier_setter
                self.path_setter=path_setter
                self.identifier_getter=identifier_getter
                self.document_button=document_button
                #self.paper_obj = document_button.parent.paper_obj
                self.path_dictionary = path_dictionary
                self.change_path_button = ttk.Button(document_button,text="Change Path",command=lambda:document_button.parent.paper_obj.browse_file_input(document_button.type,set_function_index=self.index,completefunction=self.document_button.parent.parent.populate_treeview()))
                self.change_path_button.grid(row=row,column=2,sticky="nw",padx=10,pady=10)

                self.delete_path_button = ttk.Button(document_button,text="Delete Path",command=lambda:self.delete_path())
                self.delete_path_button.grid(row=row,column=5,sticky="nw",padx=5,pady=10)

                self.view_button = ttk.Button(document_button,text="View",command=lambda:self.document_button.parent.view(self.path_dictionary["path"],""))
                self.view_button.grid(row=row,column=6,sticky="nw",padx=5,pady=10)
                self.open_button = ttk.Button(document_button,text="Open",command=lambda:self.document_button.parent.open(self.path_dictionary["path"]))
                self.open_button.grid(row=row,column=7,sticky="nw",padx=5,pady=10)


                self.label_path = ttk.Label(document_button,text=path_dictionary["path"] + "\t(Valid " + str(path_dictionary["valid"]) + ")")
                self.label_path.grid(row=row,column=0,sticky="nw",columnspan=2,padx=(20,0),pady=10)

                document_button.parent.CreateInput(document_button,"Unique extension",row=row,column=3,getter=self.get_unique_identifier,setter=self.change_identifier,padx=5,pady=10)

        def add_path(self):
            self.parent.paper_obj.browse_file_input(self.type,custom_identifier=self.identifier_entry.get())
            if self.parent.type == "update":
                self.parent.paper_obj.update_database(pdf_files_only=True)
            #self.parent.refresh_document_buttons()
            self.parent.update_or_save(ignore_automatics=True)



        def __init__(self,parent,type,top_level_getter, identifier_getter, path_setter, identifier_setter):
            super().__init__(parent.frame)
            self.type=type
            self.parent = parent
            self.path_setter=path_setter

            self.add_button = ttk.Button(self,text=f"Add {type}",command=lambda: self.add_path(),width=24)
            self.add_button.grid(row=0,column=0, sticky="nw",padx=20,pady=(10,0))

            self.identifier_entry = ttk.Entry(self,width=30)
            self.identifier_entry.grid(row=0,column=1,sticky="nw",padx=0,pady=(10,0))

            
            self.file_paths = top_level_getter()
            for index,path_dictionary in enumerate(self.file_paths):
                row = self.Row(self,path_dictionary,index,identifier_getter, path_setter, identifier_setter,index+1)
                #row.grid(row=index+1,column=1,columnspan=3)


    def open(self,path, event=None):
        cwd = os.getcwd()
        subprocess.Popen([os.path.join(cwd,path)],shell=True)

       

    def view(self,path,event=None):

        self.PDFPopUp(self,path)
    
    def refresh_page(self):
        for widgets in self.frame.winfo_children():
            widgets.destroy()
        self.paper_obj.update_object()
        self.setup_page()

    def update_database(self,event=None,refresh_page = True):
        self.paper_obj.update_database()
        if refresh_page:
            self.refresh_page()
        #self.mainline_obj.resetwindows("MainPage")
        self.parent.populate_treeview()

    def save_database(self,event=None,refresh_page = True):
        self.mainline_obj.db_object.save_row(self.paper_obj)
        if refresh_page:
            self.refresh_page()
        #self.mainline_obj.resetwindows("MainPage")
        self.parent.populate_treeview()


    class CreateInput():
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

        def __init__(self, frame, text, row, column, getter, setter, padx=0, pady=0,sticky="nw",scrollable_text=False,getter_param=None,setter_param=None):
                
            self.frame=frame
            self.text=text
            self.row=row
            self.column=column
            self.padx=padx
            self.pady=pady
            self.getter=getter
            self.setter=setter
            self.setter_param=setter_param
            self.getter_param=getter_param
            

            


            if not self.getter_param == None: current_value = self.getter(self.getter_param)
            else: current_value = self.getter()

            if scrollable_text:
                self.label = tk.Label(frame,text=self.text + ": ")
                self.label.grid(row=self.row,column=self.column,sticky=sticky,padx=padx,pady=pady)
                
                self.entry = scrolledtext.ScrolledText(frame, wrap=tk.WORD,
                                        width=40, height=3)
                self.entry.bind("<KeyRelease>", lambda e: self.scrolled_text_filter_callback(self.entry,type))
                self.entry.grid(row=row,column=column+1,sticky=sticky,padx=padx,pady=pady)
                self.entry.insert(tk.END, current_value)
            else:
                # create and place an Entry box into the location where the label was deleted
                current_value = str(current_value)
                
                self.label = tk.Label(frame,text=self.text + ": " + str(current_value))
                self.label.grid(row=self.row,column=self.column,sticky=sticky,padx=padx,pady=pady)
                
                entry_tracker = tk.StringVar()
                entry_tracker.trace("w", lambda name, index, mode, sv=entry_tracker: self.entry_filter_callback(entry_tracker, type))
            
                self.entry = ttk.Entry(frame,textvariable=entry_tracker)
                self.entry.grid(row=row,column=column+1,sticky=sticky,padx=padx,pady=pady) 
                self.entry.insert(tk.END, current_value)
                
                self.set_label()
            # pre-insert the value from the getter function
            

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
        row = self.document_button_rows


        self.original_document_row = self.DocumentButton(self,self.terminology["Original"],self.paper_obj.get_original,self.paper_obj.get_original_identifier,self.paper_obj.set_original_path,self.paper_obj.set_original_identifier)
        self.original_document_row.grid(row=row,column=0,columnspan=3,sticky="nw")

        row += 1
        self.markscheme_document_row = self.DocumentButton(self,self.terminology["Markscheme"],self.paper_obj.get_markscheme,self.paper_obj.get_markscheme_identifier,self.paper_obj.set_markscheme_path,self.paper_obj.set_markscheme_identifier)
        self.markscheme_document_row.grid(row=row,column=0,columnspan=3,sticky="nw")

        row += 1
        self.otherattachments_document_row = self.DocumentButton(self,"Other Attachments",self.paper_obj.get_otherattachments,self.paper_obj.get_otherattachments_identifier,self.paper_obj.set_otherattachments_path,self.paper_obj.set_otherattachments_identifier)
        self.otherattachments_document_row.grid(row=row,column=0,columnspan=3,sticky="nw")

        row += 1
        return row
    
    def refresh_document_buttons(self):
        self.original_document_row.destroy()
        self.markscheme_document_row.destroy()
        self.otherattachments_document_row.destroy()
        self.setup_document_buttons()


    def reset_completed_date(self):
        import numpy as np
        self.paper_obj.set_completed_date(np.datetime64('NaT'))

    def select_completed_date(self):
        import date_popup
        date_popup.dateselect("Please select a date",self.completed_date_popup)

    def create_gradeboundary_box(self):
        self.gradeboundary_frame = ttk.Frame(self.frame)

        

        grade_boundaries_list = values_and_rules.get_course_grade_boundaries()[self.paper_obj.get_course_type()]

        row = 0
        for grade_boundary in grade_boundaries_list:
            self.CreateInput(self.gradeboundary_frame,self.terminology["Grade"]+f" {grade_boundary}",row=row,column=0,getter=self.paper_obj.get_grade_boundary,setter=self.paper_obj.set_grade_boundary,padx=20,pady=5,sticky="nw",getter_param=grade_boundary,setter_param=grade_boundary)
            row += 1
        
        self.CreateInput(self.gradeboundary_frame,"Maximum mark",row=row,column=0,getter=self.paper_obj.get_gbmax,setter=self.paper_obj.set_gbmax,padx=20,pady=5,sticky="nw")

        self.gradeboundary_frame.grid(row=1,column=2,rowspan=20,sticky="nw")




    def setup_page(self):

        header=tk.Label(self.frame, text= "Edit: " + self.paper_obj.get_name())
        header.grid(row=0,column=0,columnspan=2,sticky="nw",padx=20,pady=15)

        self.create_gradeboundary_box()
        
        
        row = 1
        column = 0
        
        self.CreateInput(self.frame,"Override name",row=row,column=column,getter=self.paper_obj.get_custom_name,setter=self.paper_obj.set_custom_name,padx=20,pady=5,sticky="nw")
        row += 1
        
        self.CreateInput(self.frame,"Year",row=row,column=column,getter=self.paper_obj.get_year,setter=self.paper_obj.set_year,padx=20,pady=5,sticky="nw")
        row += 1

        if self.terminology["show_session"]:
            self.CreateInput(self.frame,self.terminology["Session"],row=row,column=column,getter=self.paper_obj.get_session,setter=self.paper_obj.set_session,padx=20,pady=5,sticky="nw")
            row += 1
        
        if self.terminology["show_timezone"]:
            self.CreateInput(self.frame,self.terminology["Timezone"],row=row,column=column,getter=self.paper_obj.get_timezone,setter=self.paper_obj.set_timezone,padx=20,pady=5,sticky="nw")
            row += 1
        
        if self.terminology["show_paper"]:
            self.CreateInput(self.frame,self.terminology["Paper"],row=row,column=column,getter=self.paper_obj.get_paper,setter=self.paper_obj.set_paper,padx=20,pady=5,sticky="nw")
            row += 1

        if self.terminology["show_subject"]:
            self.CreateInput(self.frame,self.terminology["Subject"],row=row,column=column,getter=self.paper_obj.get_subject,setter=self.paper_obj.set_subject,padx=20,pady=5,sticky="nw")
            row += 1
        
        if self.terminology["show_level"]:
            self.CreateInput(self.frame,self.terminology["Level"],row=row,column=column,getter=self.paper_obj.get_level,setter=self.paper_obj.set_level,padx=20,pady=5,sticky="nw")
            row += 1

        self.CreateInput(self.frame,"Notes",row=row,column=column,getter=self.paper_obj.get_notes,setter=self.paper_obj.set_notes,padx=20,pady=5,sticky="nw",scrollable_text = True)
        row +=1 

        """
        row += 1
        printed_label=tk.Label(self.frame, text= "Printed: " + str(self.paper_obj.get_printed()))
        printed_label.grid(row=row,column=0,columnspan=2,sticky="nw",padx=20,pady=5)

        printed_combo = ttk.Combobox(self.frame, values=["","True","False"],state="readonly")
        printed_combo.grid(row=row,column=column+1,sticky="nw",pady=5,padx=20)
        printed_combo.set(str(self.paper_obj.get_printed()))
        printed_combo.bind("<<ComboboxSelected>>", lambda e: self.dropdown_handler(printed_combo, printed_label, "Printed", self.paper_obj.set_printed,self.paper_obj.get_printed))

        row += 1
        completed_label=tk.Label(self.frame, text= "Completed: " + str(self.paper_obj.get_completed()))
        completed_label.grid(row=row,column=0,columnspan=2,sticky="nw",padx=20,pady=5)

        completed_combo = ttk.Combobox(self.frame, values=["","True","False"],state="readonly")
        completed_combo.grid(row=row,column=column+1,sticky="nw",pady=5,padx=20)
        completed_combo.set(str(self.paper_obj.get_completed()))

        completed_combo.bind("<<ComboboxSelected>>", lambda e: self.dropdown_handler(completed_combo, completed_label,"Completed", self.paper_obj.set_completed,self.paper_obj.get_completed))

        row += 1
        partial_label=tk.Label(self.frame, text= "Partial: " + str(self.paper_obj.get_partial()))
        partial_label.grid(row=row,column=0,columnspan=2,sticky="nw",padx=20,pady=5)

        partial_combo = ttk.Combobox(self.frame, values=["","True","False"],state="readonly")
        partial_combo.grid(row=row,column=column+1,sticky="nw",pady=5,padx=20)
        partial_combo.set(str(self.paper_obj.get_partial()))

        partial_combo.bind("<<ComboboxSelected>>", lambda e: self.dropdown_handler(partial_combo, partial_label,"Partial", self.paper_obj.set_partial,self.paper_obj.get_partial))        
        


        row += 1

        """

        self.CreateInput(self.frame,"Mark: ",row=row,column=column,getter=self.paper_obj.get_mark,setter=self.paper_obj.set_mark,padx=20,pady=5,sticky="nw")
        
        row += 1

        self.CreateInput(self.frame,"Maximum: ",row=row,column=column,getter=self.paper_obj.get_maximum,setter=self.paper_obj.set_maximum,padx=20,pady=5,sticky="nw")
        row += 1

        self.percentage_label_text = str(round(float(self.paper_obj.get_percentage()) * 100,1))
        grade = self.paper_obj.get_grade()
        if grade == -1:
            grade = "None"
        else:
            grade = str(grade)
        self.percentage_label = ttk.Label(self.frame, text ="Percentage mark: " + self.percentage_label_text + "%\t---\tGrade: " + grade)
        self.percentage_label.grid(row=row,column=column,sticky="nw",padx=20,pady=(5,15),columnspan=2)

        row += 1


        
        self.open_directory_button = ttk.Button(self.frame,text="Open File Directory",command=self.paper_obj.open_file_directory,width=24)
        self.open_directory_button.grid(row=row,column=column,sticky="nw",padx=20,pady=5)

        row += 1
        self.document_button_rows = row

        row = self.setup_document_buttons()


        row += 1

        self.completed_date = str(self.paper_obj.get_completed_date())
        self.select_completed_date_label = ttk.Label(self.frame, text ="Completed date: " + self.completed_date)
        self.select_completed_date_label.grid(row=row,column=column+1,sticky="nw",pady=5)

        self.select_completed_date_button = ttk.Button(self.frame,text="Select Completed Date",command=self.select_completed_date,width=24)
        self.select_completed_date_button.grid(row=row,column=column,sticky="nw",padx=20,pady=5)
        
        self.reset_completed_date_button = ttk.Button(self.frame,text="Reset Completed Date",command=self.reset_completed_date,width=24)
        self.reset_completed_date_button.grid(row=row,column=column+2,sticky="nw",padx=20,pady=5)

        row += 3

        if self.type == "update":
            self.confirm_button = ttk.Button(self.frame,text="Confirm",width=30,command=lambda:self.update_or_save())
        elif self.type == "create":
            self.confirm_button = ttk.Button(self.frame,text="Create",width=30,command=lambda:self.update_or_save())
            
        

        self.confirm_button.grid(row=row,column=column,padx=20,pady=15,ipady=30)

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
                self.update_printed(refresh_page=refresh_page)
            
            if not ignore and (self.paper_obj.get_percentage() != "" and float(self.paper_obj.get_percentage()) != 0) and self.paper_obj.get_completed() == False:
                self.update_completed(refresh_page=refresh_page)
            if not ignore and self.paper_obj.get_completed() == True and type(self.paper_obj.get_completed_date()) != pd._libs.tslibs.timestamps.Timestamp:
                self.update_completed_date(refresh_page=refresh_page)
        
        if refresh_page:
            self.refresh_page()



    def destroyer(self):
        """ Handle program exit - will close all windows and command lines to prevent the program from remaining open in the background"""
        #root.quit()
        ##root.destroy()
        #sys.exit()
        self.update_or_save(refresh_page=False)
        self.toplevel.destroy()


    def __init__(self,toplevel,parent, scrollable_frame, mainline_obj, paper_obj, type="update"):
        super().__init__(scrollable_frame)
        
        self.toplevel = toplevel

        self.parent=parent
        self.mainline_obj=mainline_obj
        self.paper_obj=paper_obj
        self.type=type
        
        # handle program exit protocol
        #root.protocol("WM_DELETE_WINDOW", self.destroyer)
        toplevel.protocol("WM_DELETE_WINDOW", self.destroyer)

        self.terminology = values_and_rules.get_terminology(self.paper_obj.get_course_type())


        self.frame = ttk.Frame(self)
        
        self.setup_page()
        
        scrollable_frame.update()

        self.frame.grid(row=0,column=0,sticky="nsew")
        self.grid(row=0,column=0)

        self.frame.grid_rowconfigure(1,weight=1)
        self.frame.grid_columnconfigure(1,weight=1)

        self.frame.update()
        toplevel.geometry(f"{self.frame.winfo_width()+25}x{self.frame.winfo_height()-25}+25+25")


