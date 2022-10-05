# library imports
import json
import shutil
import pandas as pd
import tkinter as tk
import numpy as np
from tkinter import ttk, filedialog, messagebox
import sys, os, scrollable_frame, UI_MainPage

class database():
    class PaperObject():
        def __init__(self, db, mainline_obj):
            self.db=db
            self.mainline_obj = mainline_obj
            self.db_index=None
            self.db_row=None
            self.db_row_injected=False

            self.__percentage=0

            self.__normal_format = True
            self.__custom_name = ""
            self.__year = ""
            self.__session = ""
            self.__timezone = ""
            self.__paper = ""
            self.__subject = ""
            self.__level = ""
            self.__questions = ""
            self.__original = []
            self.__markscheme = []
            self.__scanned = []

            self.__printed = False
            self.__completed_date = np.datetime64('NaT')
            self.__completed = False
            self.__partial = False
            self.__mark = 0.00
            self.__maximum = 0.00
            self.__notes = ""

            self.__original_valid=False
            self.__markscheme_valid=False
            self.__scanned_valid=False
            
            
            self.__name = ""

        #def update_original():

        def is_float(self,element) -> bool:
            try:
                float(element)
                return True
            except ValueError:
                return False

        def delete_item(self):
            print("INDEX",self.db_index)
            print(self.db_index,self.__name,self.db.at[self.db_index,"Session"],self.db.at[self.db_index,"Year"],self.db.at[self.db_index,"Timezone"],self.db.at[self.db_index,"Paper"],self.db.at[self.db_index,"Subject"],self.db.at[self.db_index,"Level"])
            self.db.drop(self.db_index,inplace=True)
            self.db.to_csv('database.csv',index=False)

        def set_db_index(self,new_index):
            self.db_index = new_index

        def reformat_integers(self):
            if self.is_float(self.__year): self.__year = str(int(self.__year))
            else: 
                self.__year = ""
                #print("replace year")
            
            if self.is_float(self.__timezone): self.__timezone = str(int(self.__timezone))
            else: 
                self.__timezone = ""
                #print("replace timezone")


            if self.is_float(self.__paper): 
                #print("Changing paper",self.__paper,str(int(self.__paper)))
                self.__paper = str(int(self.__paper))
            else: 
                self.__paper = ""
                #print("replace paper")

            if self.is_float(self.__mark): self.__mark = float(self.__mark)
            else: 
                self.__mark = ""
                #print("replace mark")

            if self.is_float(self.__maximum): self.__maximum = float(self.__maximum)
            else: 
                self.__maximum = ""
                #print("replace percentage")


        def assign_db_data(self,db_row, db_index):
            self.db_index = db_index
            self.db_row = db_row
            self.db_row_injected=True
            # reading in all rows from the database
            #print(self.db_row["Year"])
            self.__normal_format = self.db_row["NormalFormat"]
            self.__custom_name = self.db_row["CustomName"]
            

            
            self.__session = self.db_row["Session"]
            
            self.__year = self.db_row["Year"]
            self.__timezone = self.db_row["Timezone"]
            self.__paper = self.db_row["Paper"]


            
            self.__subject = self.db_row["Subject"]
            self.__level = self.db_row["Level"]
            self.__questions = self.db_row["Questions"]
            self.__original = json.loads(str(self.db_row["Original"]))
            self.__markscheme = json.loads(str(self.db_row["Markscheme"]))
            self.__scanned = json.loads(str(self.db_row["Scanned"]))


            self.reformat_integers()


            self.__printed = self.db_row["Printed"]
            self.__completed_date = self.db_row["CompletedDate"]
            self.__completed = self.db_row["Completed"]
            self.__partial = self.db_row["Partial"]
            self.__mark = self.db_row["Mark"]
            self.__maximum = self.db_row["Maximum"]
            self.__notes = self.db_row["Notes"]

            self.update_database(clean_dir=False)


        def create_file_name(self, type, unique_identifier = ""):
            if type == "original": prefix = "original"
            if type == "markscheme": prefix = "markscheme"
            if type == "scanned": prefix = "scanned"



            new_file_name = prefix+"-"+self.__name
            if unique_identifier != "":
                new_file_name = new_file_name + "-" + unique_identifier
            new_file_name += ".pdf"
            return new_file_name


        def update_object(self):
            """
            FUNCTION: complete a range of checks and tests on the data fields within this object, including the following:
            - set the field name
            - check path validity of all three paths
            - check the mark and maximum fields, and calculate a percentage score
            """

            self.reformat_integers()
            
            if self.__custom_name != "":
                self.__normal_format = False
            else:
                self.__normal_format = True
            

            # check mark and maximum validity, calculate decimal / percentage score
            self.__mark_exists, self.__percentage, self.__mark, self.__maximum = self.check_valid_mark_and_maximum()

            

            # custom fields which are specific to the database
            self.__name = self.create_name()
            #print("name1",self.__name)
            # check the given path fields (for the original past paper document, markscheme document and scanned PDF document)
            for index,path_dictionary in enumerate(self.__original):
                path_dictionary["valid"], path_dictionary["path"] = self.check_path_exists(path_dictionary["path"])
                
                
                if os.path.join(self.create_path_for_files(),self.create_file_name("original",path_dictionary["identifier"])) != path_dictionary["path"]:
                    if self.is_valid_pdf(path_dictionary["path"]):
                        self.move_file_location("original",os.path.join(os.getcwd(),path_dictionary["path"]),custom_identifier=path_dictionary["identifier"],set_function_index=index)
            
            # check the given path fields (for the markscheme past paper document, markscheme document and scanned PDF document)
            for index,path_dictionary in enumerate(self.__markscheme):
                path_dictionary["valid"], path_dictionary["path"] = self.check_path_exists(path_dictionary["path"])
                
                
                if os.path.join(self.create_path_for_files(),self.create_file_name("markscheme",path_dictionary["identifier"])) != path_dictionary["path"]:
                    if self.is_valid_pdf(path_dictionary["path"]):
                        self.move_file_location("markscheme",os.path.join(os.getcwd(),path_dictionary["path"]),custom_identifier=path_dictionary["identifier"],set_function_index=index)
            
            # check the given path fields (for the scanned past paper document, markscheme document and scanned PDF document)
            for index,path_dictionary in enumerate(self.__scanned):
                path_dictionary["valid"], path_dictionary["path"] = self.check_path_exists(path_dictionary["path"])
                
                
                if os.path.join(self.create_path_for_files(),self.create_file_name("scanned",path_dictionary["identifier"])) != path_dictionary["path"]:
                    if self.is_valid_pdf(path_dictionary["path"]):
                        self.move_file_location("scanned",os.path.join(os.getcwd(),path_dictionary["path"]),custom_identifier=path_dictionary["identifier"],set_function_index=index)


            

            #self.__markscheme_valid, self.__markscheme = self.check_path_exists(self.__markscheme)
            #self.__scanned_valid, self.__scanned = self.check_path_exists(self.__scanned)



        def is_valid_pdf(self,path):
            #print("Valid check",os.path.join(os.getcwd(),path))
            if os.path.exists(os.path.join(os.getcwd(),path)) and str(path)[-4:] == ".pdf": 
                return True
            else: return False

        def pretty_level(self):
            if self.__level == "SL": return "Standard Level"
            if self.__level == "HL": return "Higher Level"
            else: return self.__level

        def create_path_for_files(self):

            path = "Papers"

            if self.pretty_subject() != "": path += "/" + self.pretty_subject()
            if self.pretty_level() != "": path += "/" + self.pretty_level()
            if self.pretty_year() != "": path += "/" + self.pretty_year()
            if self.pretty_session() != "": path += "/" + self.pretty_session()
            if self.pretty_timezone() != "": path += "/" + self.pretty_timezone()


            return path

        def update_database(self, pdf_files_only = False,clean_dir = True):
            """
            FUNCTION: sync the internal object elements from this class with those of the original Pandas database
            WARNING: ALL ELEMENTS WITHIN THIS OBJECT MUST BE A VALID DATATYPE FOR THE PANDAS DATAFRAME. Use the self.update_object() method before calling this one
            """
            self.update_object()    
            if self.db_row_injected == False:
                none_array = []
                
                
                for i in list(range(len(self.db.columns))):
                    none_array.append(None)

                self.db.loc[self.db.shape[0]] = none_array
                self.db_row_injected=True
                
            if pdf_files_only == False:

                self.db.at[self.db_index, "NormalFormat"] = self.__normal_format
                self.db.at[self.db_index, "CustomName"] = self.__custom_name
                self.db.at[self.db_index, "Year"] = str(self.__year)
                self.db.at[self.db_index, "Session"] = self.__session
                self.db.at[self.db_index, "Timezone"] = str(self.__timezone)
                self.db.at[self.db_index, "Paper"] = self.__paper
                self.db.at[self.db_index, "Subject"] = self.__subject
                self.db.at[self.db_index, "Level"] = self.__level
                self.db.at[self.db_index, "Questions"] = self.__questions
                self.db.at[self.db_index, "Printed"] = self.__printed
                self.db.at[self.db_index, "CompletedDate"] = self.__completed_date
                self.db.at[self.db_index, "Completed"] = self.__completed
                self.db.at[self.db_index, "Partial"] = self.__partial
                self.db.at[self.db_index, "Mark"] = self.__mark
                self.db.at[self.db_index, "Maximum"] = self.__maximum
                self.db.at[self.db_index, "Notes"] = self.__notes
            
            self.db.at[self.db_index, "Original"] = json.dumps(self.__original)
            self.db.at[self.db_index, "Markscheme"] = json.dumps(self.__markscheme)
            self.db.at[self.db_index, "Scanned"] = json.dumps(self.__scanned)
            self.db.to_csv('database.csv',index=False)

            if clean_dir:
                self.mainline_obj.clean_dir()



        def pretty_year(self):
            if len(str(self.__year)) == 2: return "20" + str(self.__year)
            else: return str(self.__year)

        def pretty_session(self):
            if self.__session == "M":return "May"
            elif self.__session == "N":return "November"
            elif self.__session == "TRL":return "Trial"
            else: return self.__session
        
        def pretty_timezone(self):
            if self.__timezone == "": 
                #print("ENMPTY")
                return ""
            else:
                return "TZ" + str(self.__timezone)
        
        def pretty_subject(self):
            if self.__subject == "MA": return "Mathematics"
            elif self.__subject == "PH": return "Physics"
            elif self.__subject == "BM": return "Business Management"
            elif self.__subject == "CS": return "Computer Science"
            elif self.__subject == "EN": return "English"
            else: return self.__subject

        def move_file_location(self, type, override_path = None, set_function_index=-1, custom_identifier="",copy=False,ignore_duplicate=False):
            """
            Move a PDF file to a new location
            IN:
            - type (str): original, markscheme or scanned
            - OPTIONAL override_path: the path of the current location of the PDF file needing to be moved
            - OPTIONAL set_function_index (default -1): the index of the directory being modified in the original/markscheme/scanned dictionaries
            - OPTIONAL custom_identifier (str): adds an identifier to the directory being added
            - OPTIONAL copy (default False): sets the copy/replace setting
            - OPTIONAL ignore_duplicate (default False): will override duplicates if set to True
            """
            # get the current working directory
            current_working_directory = os.getcwd()
            #print("INDEX",set_function_index)
            #print("CUSTOM1",custom_identifier)
            # generating the new paths for the selected item
            # TODO make MAC compatible
            
            if type == "original":
                #relative_folder_path = self.create_path_for_files()
                #current_path = os.path.join(current_file_path,self.__original)
                set_function = self.set_original_path
                set_function_identifier = self.set_original_identifier
                #unique_identifier = self.get_original_identifier(set_function_index)
            elif type == "markscheme":
                #relative_folder_path = self.create_path_for_files()
                #current_path = os.path.join(current_file_path,self.__markscheme)
                set_function = self.set_markscheme_path
                set_function_identifier = self.set_markscheme_identifier
                #unique_identifier = self.get_markscheme_identifier(set_function_index)

            elif type == "scanned":
                #relative_folder_path = self.create_path_for_files()
                #current_path = os.path.join(current_file_path,self.__scanned)
                set_function = self.set_scanned_path
                set_function_identifier = self.set_scanned_identifier
                #unique_identifier = self.get_scanned_identifier(set_function_index)
            
            relative_folder_path = self.create_path_for_files()
            if override_path != None:
                current_path = override_path

            new_path = os.path.join(current_working_directory,relative_folder_path)
            
            # make the target directory if it does not yet exist
            if not os.path.exists(new_path):
                os.makedirs(new_path)

            # check if the target file already exists
            override = True


            new_file_name = self.create_file_name(type,custom_identifier)


            if os.path.exists(os.path.join(new_path,new_file_name)) and not ignore_duplicate:
                override = tk.messagebox.askyesno(message=f"The file {new_file_name} already exists in {new_path}")

            if override == True:
                if copy == True:
                    shutil.copy(current_path, os.path.join(new_path,new_file_name))
                else:
                    shutil.move(current_path, os.path.join(new_path,new_file_name))
                new_index = set_function(os.path.join(relative_folder_path,new_file_name), index = set_function_index)
                set_function_identifier(custom_identifier,new_index)
    



        def delete_path(self,type,index,ignore_removed_pdf=False):
            
            return_msg = ""
            if type == "original":
                return_msg = self.delete_original(index,ignore_removed_pdf=ignore_removed_pdf)
            if type == "markscheme":
                return_msg = self.delete_markscheme(index,ignore_removed_pdf=ignore_removed_pdf)
            if type == "scanned":
                return_msg = self.delete_scanned(index,ignore_removed_pdf=ignore_removed_pdf)
            return return_msg



        def browse_file_input(self, type,custom_identifier="",set_function_index=-1,completefunction=None):
            """
            Will prompt user for input on either the original, markscheme or original files
            IN:
            - type (str): indicate for which field this function is being used (either 'original', 'markscheme' or 'scanned')
            - set_function_index (int): the index of the path being changed in the original/markscheme/scanned dictionaries
            - OPTIONAL completefunction (default None): a function which is run once the change has been made
            """

            # TODO restrict to only PDF files
            path = tk.filedialog.askopenfilename(initialdir = "Downloads",title = f"Select the {type.title()} file")

            self.update_object()


            #print("CuSTOME",custom_identifier)

            self.move_file_location(type,override_path=path,set_function_index=set_function_index,custom_identifier=custom_identifier, copy=True)

            if completefunction != None:
                completefunction()
            
            #self.mainline_obj.resetwindows("MainPage")

        def set_normal_format(self, normal_format):
            self.__normal_format=normal_format
        def set_custom_name(self, custom_name):
            self.__custom_name=custom_name
        def set_year(self, year):
            self.__year=str(year)
        def set_session(self, session):
            self.__session=session
        def set_timezone(self, timezone):
            self.__timezone=str(timezone)
        def set_paper(self, paper):
            self.__paper=str(paper)
        def set_subject(self, subject):
            self.__subject=subject
        def set_level(self, level):
            self.__level=level
        def set_questions(self, questions):
            self.__questions=questions
        
        def remove_file(self,path):
            try:
                os.remove(path)
                return True
            except Exception as e:
                return e



        def delete_original(self,index,ignore_removed_pdf=False):
            return_msg = self.remove_file(self.__original[index]["path"])
            if return_msg == True or ignore_removed_pdf==True: return self.__original.pop(index)
            else: return str(return_msg)


        def delete_markscheme(self,index,ignore_removed_pdf=False):
            return_msg = self.remove_file(self.__markscheme[index]["path"])
            if return_msg == True or ignore_removed_pdf==True: return self.__markscheme.pop(index)
            else: return str(return_msg)


        def delete_scanned(self,index,ignore_removed_pdf=False):
            return_msg = self.remove_file(self.__scanned[index]["path"])
            if return_msg == True or ignore_removed_pdf==True: return self.__scanned.pop(index)
            else: return str(return_msg)



        def set_original(self,original,index = -1):
            self.__original[index]["path"]=original
            print("depracated")

        def set_original_path(self, original, index = -1):
            if index == -1: 
                
                self.__original.append({"path":original,"valid":True,"identifier":""})
                return_index = len(self.__original)-1
            else:
                self.__original[index]["path"]=original
                return_index = index
            return return_index

        def set_original_valid(self,original,index):

            self.__original[index]["valid"]=original

        def set_original_identifier(self,original,index):

            self.__original[index]["identifier"]=original


        def set_markscheme_path(self, markscheme, index = -1):
            if index == -1: 
                self.__markscheme.append({"path":markscheme,"valid":True,"identifier":""})
                return_index = len(self.__markscheme)-1
            else:
                self.__markscheme[index]["path"]=markscheme
                return_index = index
            return return_index



        def set_markscheme_valid(self,markscheme,index):

            self.__markscheme[index]["valid"]=markscheme

        def set_markscheme_identifier(self,markscheme,index):
            #print(index)
            #print(self.__markscheme)
            self.__markscheme[index]["identifier"]=markscheme

        def set_scanned_path(self, scanned, index = -1):
            if index == -1: 
                self.__scanned.append({"path":scanned,"valid":True,"identifier":""})
                return_index = len(self.__scanned)-1
            else:
                self.__scanned[index]["path"]=scanned
                return_index = index
            return return_index

        def set_scanned_valid(self,scanned,index):

            self.__scanned[index]["valid"]=scanned

        def set_scanned_identifier(self,scanned,index):

            self.__scanned[index]["identifier"]=scanned

        def set_markscheme(self, markscheme, index = -1):
            if index == -1: 
                self.__markscheme.append(markscheme)
            else:
                self.__markscheme[index]=markscheme

        def set_scanned(self, scanned, index = -1):
            if index == -1: 
                self.__scanned.append(scanned)
            else:
                self.__scanned[index]=scanned

        def set_printed(self, printed):
            self.__printed=printed
        def set_completed_date(self, completed_date):
            self.__completed_date=completed_date
        def set_completed(self, completed):
            self.__completed=completed
        def set_partial(self, partial):
            self.__partial=partial
        def set_mark(self, mark):
            if mark == "": self.__mark = 0.00
            else: self.__mark=float(mark)
        def set_maximum(self, maximum):
            if maximum == "": self.__maximum = 0.00
            else: self.__maximum=float(maximum)
        def set_notes(self, notes):
            self.__notes=notes
        def set_name(self, name):
            self.__name=name

        def open_file_directory(self):
            cwd = os.getcwd()
            path = self.create_path_for_files()
            if os.path.exists(os.path.join(cwd,path)):
                os.startfile(os.path.join(cwd,path))
            else:
                tk.messagebox.showerror(message=f"Unable to open {str(os.path.join(cwd,path))}. It could be that the path does not exist, or that you do not have the permissions to access it.")

        # getters and setters
        def get_normal_format(self):
            return self.__normal_format
        def get_custom_name(self):
            return self.__custom_name
        def get_year(self):
            return self.__year
        def get_session(self):
            return self.__session
        def get_timezone(self):
            return self.__timezone
        def get_paper(self):
            return self.__paper
        def get_subject(self):
            return self.__subject
        def get_level(self):
            return self.__level
        def get_questions(self):
            return self.__questions
        def get_original(self):
            return self.__original
        
        def get_original_identifier(self, index):

            if len(self.__original) == 0: return ""
            return self.__original[index]["identifier"]
        def get_original_path(self, index):

            if len(self.__original) == 0: return ""
            return self.__original[index]["path"]
        def get_original_valid(self, index):
            if len(self.__original) == 0: return ""
            return self.__original[index]["valid"]

        
        def get_markscheme_identifier(self, index):
            #print("EDITING INDEX")
            #print(self.__markscheme)
            #print(index)
            #print(self.__markscheme[index]["identifier"])
            if len(self.__markscheme) == 0: return ""
            return self.__markscheme[index]["identifier"]
        def get_markscheme_path(self, index):
            if len(self.__markscheme) == 0: return ""
            return self.__markscheme[index]["path"]
        def get_markscheme_valid(self, index):
            if len(self.__markscheme) == 0: return ""
            return self.__markscheme[index]["valid"]

        
        def get_scanned_identifier(self, index):
            if len(self.__scanned) == 0: return ""
            return self.__scanned[index]["identifier"]
        def get_scanned_path(self, index):
            if len(self.__scanned) == 0: return ""
            return self.__scanned[index]["path"]
        def get_scanned_valid(self, index):
            if len(self.__scanned) == 0: return ""
            return self.__scanned[index]["valid"]
        
        def get_markscheme(self, index = -1):
            return self.__markscheme
        def get_scanned(self, index = -1):
            return self.__scanned
        def get_printed(self):
            return self.__printed
        def get_completed_date(self):
            return self.__completed_date
        def get_completed(self):
            return self.__completed
        def get_partial(self):
            return self.__partial
        def get_mark(self):
            return self.__mark
        def get_maximum(self):
            return self.__maximum
        def get_notes(self):
            return self.__notes
        def get_name(self):
            return self.__name
        def get_percentage(self):
            return self.__percentage


        def check_valid_mark_and_maximum(self):
            """
            FUNCTION: check the validity of the mark and maximum, and then calculate a percentage score based on this response
            IN: none
            OUT:
            - mark_exists (bool): indicate whether mark and maximum are valid
            - percentage (float): decimal number to indicate the percentage score (0.00 if mark or maximum invalid)
            - mark (float): number indicating the mark for the paper (0.00 if invalid)
            - maximum (float): number indicating the maximum mark for the paper (0.00 if invalid)
            - 
            """
            mark_exists = True
            percentage = 0.00
            mark = 0.00
            maximum = 0.00

            # check type of mark and maximum
            if self.__mark != '' and self.__mark >= 0 and (isinstance(self.__mark, int) or isinstance(self.__mark, float)):
                mark = float(self.__mark)
            else: 
                mark_exists = False
            
            # note: maximum  MUST be greater than 0 for the percentage division
            if self.__maximum != '' and self.__maximum > 0 and (isinstance(self.__maximum, int) or isinstance(self.__maximum, float)):
                maximum = float(self.__maximum)
            else: 
                mark_exists = False

            # create a decimal percentage score based on mark and maximum
            if mark_exists == True:
                percentage = round(self.__mark / self.__maximum, 3 )
            
            return mark_exists, percentage, mark, maximum

        def check_path_exists(self,path):
            """
            Check whether a given path exists
            IN:
            - path (str): the path of the document being checked
            OUT:
            - valid (bool): indicating whether the given path is valid
            - path (str): the updated path (will be set to an empty string if invalid)
            """

            current_file_path = os.getcwd()

            valid = True
            if path == "":
                valid = False
            
            # TODO check to ensure the file is a PDF
            elif not os.path.exists(os.path.join(current_file_path,path)):
                valid = False
            
            return valid, path

        def create_name(self):
            """
            Creates a name for the object based on the data read from the dataframe. This name will either:
            - follow the conventional naming format for past papers
            - take on the custom name provided by the data if the data row does not adhere to the past paper formatting
            """
            
            
            name = ""
            if self.__normal_format == True:
                name_array = []

                if str(self.__session) != "": name_array.append(str(self.__session))
                if str(self.__year) != "": name_array.append(str(self.pretty_year()))
                if str(self.__timezone) != "": name_array.append("TZ" + str(self.__timezone))
                if str(self.__paper) != "": name_array.append("P" + str(self.__paper))
                if str(self.__subject) != "": name_array.append(str(self.__subject))
                if str(self.__level) != "": name_array.append(str(self.__level))


                #name_array = [str(self.__session), str(self.__year), "TZ"+str(self.__timezone), "P"+str(self.__paper), self.__subject, self.__level]
                if self.__questions != "": name_array.append(self.__questions)
                name = "-".join(str(i) for i in name_array)
            elif self.__normal_format == False:
                name = self.__custom_name

            #print("name",name)

            return name


    def __init__(self, db_path,mainline_obj):
        """
        Manage the database of past papers

        IN:
        - path: the path of the database
        """

        self.mainline_obj=mainline_obj
        self.db = pd.read_csv(db_path)
        
        #print(self.db)
        self.db.dropna(subset = ["NormalFormat"], inplace=True)
        #print(self.db)
        self.db.astype({'NormalFormat': 'bool','Printed': 'bool','Completed': 'bool','Partial': 'bool'}).dtypes
        #print(self.db)
        self.db = self.db.replace(np.nan, '')
        self.db["CompletedDate"] = pd.to_datetime(self.db['CompletedDate'], dayfirst=True, errors='coerce')

        self.paper_objects = []
        self.db_index = 0
        for self.db_index, row in self.db.iterrows():
            self.paper_objects.append(self.PaperObject(self.db, self.mainline_obj))
            self.paper_objects[-1].assign_db_data(row,self.db_index)

    def create_new_row(self):
        """
        Will create a new database element, however will NOT save it to the pandas dataframe or an array. This new object must be passed into the save_row() function to do so.
        """
        new_row_object = self.PaperObject(self.db, self.mainline_obj)
        return new_row_object

    def check_row_exists(self,row_obj):
        """
        Will check if a given row object already exists within the database, if it does, it will return that which already exists
        IN:
        - row_obj: the item being checked
        OUT:
        - exists (bool): True if it does already exist, False if it does not
        - row_obj_new: if the boolean above is true, the existing row_obj will be returned, and vice versa
        """
        #print (self.paper_objects)
        for row in self.paper_objects:
            row_obj.update_object()
            row.update_object()
            if row.get_name() == row_obj.get_name():
                return True, row
            else:
                pass
        return False, row_obj

       


    def save_row(self, row):
        self.db_index += 1
        row.set_db_index(self.db_index)
        self.paper_objects.append(row)
        row.update_database()


class GUI(ttk.Frame):
    def clean_dir(self):
        # remove all empty directories

        root = os.path.join(os.getcwd(),"Papers")

        walk = list(os.walk(root))
        for path, _, _ in walk[::-1]:
            if len(os.listdir(path)) == 0:
                os.rmdir(path)
                #os.remove(path)
    def setupmenubar(self):
        """ Configure the navigation bar (menubar) """
        
        # initialise menu bar object
        self.menubar = tk.Menu(self.parent)

        # create the "Settings" menu
        self.options_menu = tk.Menu(self.menubar, tearoff=False)
        self.options_menu.add_command(label="Placeholder", command=None)
        self.menubar.add_cascade(label="Settings", menu=self.options_menu)

        # create the "Navigate" menu
        self.navigate_menu = tk.Menu(self.menubar, tearoff=False)
        self.navigate_menu.add_command(label="Placeholder", command=None)
        self.menubar.add_cascade(label="Navigate", menu=self.navigate_menu)

        # place menu bar onto the toplevel_frame widget
        self.parent.config(menu=self.menubar)


    def resetwindows(self, showwindow=""):
        """
        Reset the entire application - all windows will be removed, and then re-generated
        """
        # remove all windows
        for frame in self.frames:
            self.frames[frame].grid_forget()
        # regenerate all windows
        self.setupwindows()

        if showwindow != "":
            self.showwindow(showwindow)


    def setupwindows(self):
        '''
        Initialise all GUI classes
        '''
        # when other GUI pages are initialised, they may begin trying to change the active page (using showwindow() method). this is prevented using the ignore_setup flag.
        self.ignore_setup=True 
        
        # store all GUI pages in a dictionary.
        self.frames={}

        # loop through all imported GUI objects (from other files)
        pages = [UI_MainPage.MainPage]
        for page in pages:
            # if page already has been initalised, remove it
            if page.__name__ in self.frames:
                self.frames[page.__name__].grid_forget()
            # strore the name of the class (will be used as a key in the self.frames dict)
            page_name = page.__name__

            # initalise the GUI object. self is passed as the mainline_obj class. It allows all other GUI objects to access attributes and methods from this mainline class.
            frame = page(self, self.scrollable_frame)

            # for easy access, add the newly created object to a dictionary
            self.frames[page_name] = frame

            self.current_frame_object = frame
           
        self.ignore_setup=False

    def showwindow(self, frame_name):
        '''
        Show a requested GUI class to the user. frame_name is the name of that GUI class which needs to be shown
        '''
        # see setupwindows() method for description of self.ignore_setup
        if not self.ignore_setup:
            # remove current frame from the display
            self.current_frame_object.grid_forget()
            
            # place the requested frame on the display
            self.current_frame_object = self.frames[frame_name]
            self.current_frame_object.grid(row=0,column=0)

            # update ALL widget elements
            self.scrollable_frame.update()


    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.db_object = database("database.csv",self)

        self.clean_dir()

        ########### INITIALISING GUI ############
        # using developer-made generalised code to define a new frame with scrollbars
        self.scrollable_frame = scrollable_frame.ScrollableFrame(self.parent)

        self.setupmenubar()
        self.setupwindows()

        self.showwindow("MainPage")

        #self.pack()


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
    parent.grid_rowconfigure(0,weight=1)
    parent.grid_columnconfigure(0,weight=1)
    gui = GUI(parent)

    # handle program exit protocol
    root.protocol("WM_DELETE_WINDOW", destroyer)
    parent.protocol("WM_DELETE_WINDOW", destroyer)

    parent.mainloop()