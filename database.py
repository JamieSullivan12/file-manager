import datetime
import json
import shutil
import pandas as pd
import tkinter as tk
import numpy as np
import sys, os
import random
import values_and_rules
import customtkinter as ctk
import uuid
import custom_errors






class PaperObject():

    class DocumentData():
        
        def __init__(self,master_dict,paper_obj):
            self.__id=str(uuid.uuid4())
            self.paper_obj=paper_obj
            self.master_dict=master_dict
            self.__prefix=""
            self.__directory_path=""
            self.__file_name=""
            self.__original_file_name=""
            
            # the file extension infers the file type
            self.__file_extension=""
            self.__file_type=""
            # placed at the end of the file_name (used in case of duplicate file names in a single directory)
            self.__suffix=""
            self.__numberid=0
        
        def __del__(self):
            """
            Delete object instance
            """
            pass

        def remove_document_from_dict(self):
            
            del self.master_dict[self.get_id()]


        def remove_document(self):
            try:
                os.remove(self.get_current_file_path())
            except Exception as e:
                print(e)
            self.remove_document_from_dict()
            self.paper_obj.update_object()
            self.paper_obj.update_database()
            self.__del__()

        def generate_new_file_name(self,override_new_file_name=None,extension=False):
            
            if override_new_file_name != None:
                new_file_name=override_new_file_name
            else:

                new_file_name=self.__file_name

            extension_str=""
            if extension==True:
                extension_str=f".{self.__file_extension}"
            self.file_name_list=[]
            if self.__prefix !="":self.file_name_list.append(self.__prefix)
            if new_file_name !="":self.file_name_list.append(new_file_name)
            if self.__suffix !="":self.file_name_list.append(self.__suffix)
            if self.get_numberid() !="" and self.get_numberid()!=0:self.file_name_list.append(f"({self.get_numberid()})")
            
            name = "-".join(self.file_name_list) + extension_str
            return name
        def generate_new_file_path(self,override_new_directory_path=None,override_new_file_name=None):
            """
            Return a string with the full path (including directory,filename,suffix and file extension)
            """
            if override_new_directory_path != None:
                new_directory_path=override_new_directory_path
            else: new_directory_path=self.__directory_path


            return os.path.join(new_directory_path,f"{self.generate_new_file_name(override_new_file_name=override_new_file_name)}.{self.__file_extension}")

        def get_current_file_name(self):
            return self.__original_file_name

        def get_current_file_path(self):
            return os.path.join(self.__directory_path,f"{self.get_original_file_name()}.{self.__file_extension}")

        def get_id(self):
            return self.__id
        def get_directory_path(self):
            return self.__directory_path
        
        def get_file_type(self):
            """
            questionpaper, markscheme or attachment
            """
            return self.__file_type
        def get_original_file_name(self):
            return self.__original_file_name
        def get_file_extension(self):
            return self.__file_extension
        def get_suffix(self):
            return self.__suffix
        def get_prefix(self):
            return self.__prefix
        def get_numberid(self):
            return self.__numberid
        def get_file_name(self):
            return self.__file_name
        def increment_numberid(self):
            self.__numberid+=1
        def reset_numberid(self):
            self.__numberid=0

        def validitycheck_directory_path(self):
            if os.path.exists(self.get_directory_path()):
                return True
            else:
                return False
        def validitycheck_file_path(self):
            if os.path.exists(self.get_current_file_path()):
                return True
            else:
                return False
        
        def set_file_type(self,value):
            self.__file_type=value
        def set_original_file_name(self,value):
            self.__original_file_name=value
        def set_prefix(self,value):
            self.__prefix=value
        def set_file_name(self,value):
            self.__file_name=value
        def set_file_extension(self,value):
            # remove the dot from the file extension
            self.__file_extension=value.replace(".","")

        def set_original_directory_path(self,new_directory_path):
            self.__directory_path=new_directory_path

        def file_path_already_exists(self,new_file_path):

            new_file_path = os.path.join(new_file_path, self.generate_new_file_name(extension=True))
            #if os.path.exists(new_file_path): 
            #    print(new_file_path,"ALREADY EXISTS")
            #    return True
            for document in self.master_dict:
                if self.master_dict[document].get_current_file_path() == new_file_path and self.master_dict[document].get_id()!=self.get_id():
                    return True
            return False

        def set_directory_path(self,new_directory_path,new_file_name,copy=False):
            self.set_file_name(new_file_name)
            # ensure the destination directory exists
            if not os.path.exists(new_directory_path):
                os.makedirs(new_directory_path)

            self.reset_numberid()
            # ensure the file being moved with not override an existing file with the same name in the destination directory
            while self.file_path_already_exists(new_directory_path) == True:
                self.increment_numberid()
        
            new_file_path=self.generate_new_file_path(override_new_directory_path=new_directory_path)
            if new_file_path != self.get_current_file_path():
                if copy == True:
                    shutil.copy(self.get_current_file_path(),new_file_path)
                else:
                    shutil.move(self.get_current_file_path(),new_file_path)

            self.__directory_path=new_directory_path
            self.set_original_file_name(self.generate_new_file_name())


        def set_suffix(self,value):
            self.__suffix=value
        def set_prefix(self,value):
            self.__prefix=value
        def set_numberid(self,value):
            self.__numberid=int(value)

        def deserialise(self,dict):
            """
            Decode a dictionary with serialised data, thus populating the object. Dictionary key:value pairs must include:
            - "id": -> str
            - "directory_path":path wherein the file sits (eg users/name/downloads/...) -> str
            - "file_name":name of file without extension (eg .pdf) or suffix (see below) -> str
            - "file_type":file extension (eg .pdf) -> str
            - "suffix":string placed at the end of the file name -> str
            """
            
            self.__id=dict["id"]
            self.set_original_directory_path(dict["directory_path"])
            self.set_file_name(dict["file_name"])
            self.set_original_file_name(dict["original_file_name"])
            self.set_file_type(dict["file_type"])
            self.set_file_extension(dict["file_extension"])
            self.set_suffix(dict["suffix"])
            self.set_numberid(dict["numberid"])
        
        def serialise(self):
            """
            Return a serialised version of the object (in dictionary form). This may be run through the deserialise() method to load data back into the object
            """

            serialised_dict = {
                "id":self.get_id(),
                "directory_path":self.get_directory_path(),
                "file_name":self.get_file_name(),
                "original_file_name":self.get_original_file_name(),
                "file_type":self.get_file_type(),
                "file_extension":self.get_file_extension(),
                "suffix":self.get_suffix(),
                "numberid":self.get_numberid()
            }

            return serialised_dict

        def different_file_path(self,new_file_path,new_file_name):
            """
            Check if the path of the current document differs from a given file path.
            True: different
            False: no difference
            """
            if self.generate_new_file_path(override_new_directory_path=new_file_path,override_new_file_name=new_file_name)!=self.get_current_file_path():
                return True
            else:
                return False

    def __init__(self, db_obj, db, mainline):
        self.db_obj=db_obj
        self.db=db
        self.mainline = mainline
        
      
        self.__db_id = str(uuid.uuid4())

        
        self.db_row=None
        self.db_row_injected=False
        self.__ignore_update = False
        self.__normal_format = True

        self.__course_type=self.mainline.settings.get_course_type()


        self.__custom_name = ""
        
        self.__year = "" # IB AL

        self.__session = "" # IB AL

        self.__timezone = "" # IB AL
        
        self.__paper = "" # IB AL

        self.__subject = "" # IB AL
        
        self.__level = "" # IB

        # TODO: REMOVE
        self.__questions = ""

        self.__original = []

        self.__markscheme = []

        self.__otherattachments = []



        self.__questionpaper_documents = {}
        self.__markscheme_documents = {}
        self.__attachment_documents = {}

        self.__printed = False

        self.__completed_date = np.datetime64('NaT')

        self.__completed_date_datetime = None

        self.__completed = False

        self.__partial = False

        self.__mark = 0.00

        self.__maximum = 0.00

        self.__percentage=-1

        self.__notes = ""

        self.terminology=values_and_rules.get_terminology(self.__course_type)
        self.regex_requirements = values_and_rules.get_regex_patterns(self.__course_type)
        # define a dictionary with key: grade boundary codes, value: grade boundary value            
        self.__grade_boundaries = {}
        self.__grade_boundaries_percentages = {}

        for grade_boundary in values_and_rules.get_course_grade_boundaries()[self.__course_type]:
            self.__grade_boundaries[grade_boundary]=0
            self.__grade_boundaries_percentages[grade_boundary]=0

        self.__gbmax = 0
        self.__grade = -1


        self.__name = ""

    def set_grade(self):
        pass
        


    def get_grade(self):
        return self.__grade

    def is_float(self,element) -> bool:
        try:
            float(element)
            return True
        except ValueError:
            return False

    def delete_item(self):
        """
        Delete a document object from the paper object
        """


        for questionpaper in list(self.__questionpaper_documents.keys()):
            self.__questionpaper_documents[questionpaper].remove_document()
        for markscheme in list(self.__markscheme_documents.keys()):
            self.__markscheme_documents[markscheme].remove_document()
        for attachment in list(self.__attachment_documents.keys()):
            self.__attachment_documents[attachment].remove_document()
        self.db.drop(self.__db_id,inplace=True)
        self.db.to_csv('database.csv',index=False)
        del self.mainline.db_object.paper_objects[self.__db_id]
        

        self.mainline.clean_dir()

    def set_id(self,db_id):
        self.__db_id = db_id

    def reformat_integers(self):
        if self.is_float(self.__year): self.__year = str(int(self.__year))
        else: 
            self.__year = ""
        
        if self.is_float(self.__timezone): self.__timezone = str(int(self.__timezone))
        else: 
            self.__timezone = ""

        if self.is_float(self.__paper): 
            self.__paper = str(int(self.__paper))
        else: 
            self.__paper = ""

        if self.is_float(self.__mark): self.__mark = float(self.__mark)
        else: 
            self.__mark = ""

        if self.is_float(self.__maximum): self.__maximum = float(self.__maximum)
        else: 
            self.__maximum = ""

    def serialise_object_dict(self,dict):
        """
        Convert a dictionary where the value in key:value is an object to a serialised form.
        Required: each object must have a method .serialise() which returns a serialised datastructure (e.g. list,dict etc.)  
        """
        serialised_dict={}
        for key in dict:
            serialised_value = dict[key].serialise()
            serialised_dict[key]=serialised_value
        return serialised_dict

    def deserialise_object_dict(self,dict,object_instantiator,class_args):
        """
        Create new instances of an object based on a serialised dictionary where:
        - key is the unique ID of each object
        - value is the serialised dictionary that can be passed into a .deserialise(dict) function in the newly created object
        """
        deserialised_dict={}
        for key in dict:
            new_object = object_instantiator(deserialised_dict,class_args)
            new_object.deserialise(dict[key])
            deserialised_dict[key]=new_object
        return deserialised_dict


    def reset_to_db_default(self):
        try:
            row = self.db.loc[self.__db_id]
        except KeyError as e:
            raise custom_errors.ExceptionWarning(message="The metadata entered already exists in the database. \n\nThe object was not created",title="Duplicate warning")
        self.assign_db_data(row,self.__db_id)

    def assign_db_data(self,db_row, db_id):
        self.__db_id = db_id
        
        self.db_row = db_row
        self.db_row_injected=True

        # reading in all rows from the database


        self.__normal_format = self.db_row["NormalFormat"]
        self.__custom_name = self.db_row["CustomName"]            
        self.__course_type = self.db_row["CourseType"]
        self.__session = self.db_row["Session"]
        self.__year = self.db_row["Year"]
        self.__timezone = self.db_row["Timezone"]
        self.__paper = self.db_row["Paper"]

        self.__ignore_update = self.db_row["IgnoreUpdate"]
        
        self.__subject = self.db_row["Subject"]
        self.__level = self.db_row["Level"]
        self.__questions = self.db_row["Questions"]
        

        questionpaper_documents = json.loads(str(self.db_row["QuestionPaperDocuments"]))
        markscheme_documents = json.loads(str(self.db_row["MarkschemeDocuments"]))
        attachment_documents = json.loads(str(self.db_row["AttachmentDocuments"]))

        self.__questionpaper_documents=self.deserialise_object_dict(questionpaper_documents,self.DocumentData,self)
        self.__markscheme_documents=self.deserialise_object_dict(markscheme_documents,self.DocumentData,self)
        self.__attachment_documents=self.deserialise_object_dict(attachment_documents,self.DocumentData,self)

        grade_boundaries=json.loads(str(self.db_row["GradeBoundaries"]) or "{}")
        if grade_boundaries != {}:
            self.__grade_boundaries = grade_boundaries

        self.reformat_integers()


        self.__printed = self.db_row["Printed"]
        
        self.__completed_date = self.db_row["CompletedDate"]
        
        self.__completed = self.db_row["Completed"]
        self.__partial = self.db_row["Partial"]
        self.__mark = self.db_row["Mark"]
        self.__maximum = self.db_row["Maximum"]
        self.__notes = self.db_row["Notes"]


        self.__gbmax=self.db_row["GBMAX"]
        
        self.update_database(clean_dir=False)


    def create_file_name(self, type, unique_identifier = ""):
        if type == "questionpaper": prefix = "questionpaper"
        if type == "markscheme": prefix = "markscheme"
        if type == "attachment": prefix = "attachment"



        new_file_name = prefix+"-"+self.__name
        if unique_identifier != "":
            new_file_name = new_file_name + "-" + unique_identifier
        return new_file_name

    def get_ignore_update(self):
        return self.__ignore_update
    def set_ignore_update(self,ignore_update):
        self.__ignore_update = ignore_update



    def set_grade_boundary(self,grade_boundary_value,grade_boundary_code):
        """
        IN:
        - the grade boundary (code) being modified
        - the value to be inserted into that grade boundary
        OUT:
        - void
        """

        self.__grade_boundaries[grade_boundary_code]=grade_boundary_value

    def get_grade_boundary(self,grade_boundary_code):
        print("get",self.__grade_boundaries[grade_boundary_code],grade_boundary_code)
        return self.__grade_boundaries[grade_boundary_code]

    def get_grade_boudary_percentage(self,grade_boundary_code):
        return self.__grade_boundaries_percentages[grade_boundary_code]




    def set_gbmax(self,gbmax):
        self.__gbmax=gbmax
    def get_gbmax(self):
        return self.__gbmax


    def is_valid_gbmax(self):
        if self.is_float(self.__gbmax):
            if float(self.__gbmax) > 0:
                return True
        return False

    def is_valid_grade_boundaries(self):
        """
        Check if the dictionary of grade boundaries is valid AND calculate percentages. Rules:
        - all GB values must be float
        - all GB values must be 0 or greater
        """

        for grade_boundary in self.__grade_boundaries:
            value = self.__grade_boundaries[grade_boundary]
            if self.is_float(value):
                if float(value) >= 0 and self.is_valid_gbmax():
                    self.__grade_boundaries_percentages[grade_boundary]=float(value)/float(self.__gbmax)

        self.generate_grade()

    def generate_name(self):
        self.__name = self.create_name()


    def check_paper_exists(self):
        return self.db_obj.check_row_exists(self)

    def update_object(self,copy=False,override_duplicate_warning=False,new_obj=False):
        """
        FUNCTION: complete a range of checks and tests on the data fields within this object, including the following:
        - set the field name
        - check path validity of all three paths
        - check the mark and maximum fields, and calculate a percentage score
        """
        

        self.attributes_dict = {"Year":str(self.__year),"Session":str(self.__session),"Timezone":str(self.__timezone),"Paper":str(self.__paper),"Subject":str(self.__subject),"Level":str(self.__level),"Mark":str(self.__mark),"Maximum":str(self.__maximum),"Notes":self.__notes}
        
        if not self.check_minimum_requirements():
            if not new_obj:
                self.reset_to_db_default()

            required = []
            for x in self.regex_requirements["minimum_requirements"]:
                required.append(self.terminology[x])
            required = "\n".join(required)
            raise custom_errors.ExceptionWarning(message=f"The data entered in insufficient to constitute a paper entry. \n\nMinimum required fields:\n{required}.\n\nChanges were not saved.",title="Insufficient data")



        if pd.isnull(self.__completed_date):self.__completed_date_datetime=None
        elif type(self.__completed_date)==datetime.date: __completed_date_datetime=self.__completed_date
        else:self.__completed_date_datetime=self.__completed_date.to_pydatetime()

        self.reformat_integers()
        
        if self.__custom_name != "":
            self.__normal_format = False
        else:
            self.__normal_format = True
        

        # check mark and maximum validity, calculate decimal / percentage score
        self.__mark_exists, self.__percentage, self.__mark, self.__maximum = self.check_valid_mark_and_maximum()

        self.is_valid_grade_boundaries()


        if not self.mainline.settings.subject_name_exists(self.get_subject()):
            self.mainline.settings.add_subject(self.get_subject())

        # create a base file name specific to the attributes of this object
        self.__name = self.create_name()

        
        if self.check_paper_exists():
            if not new_obj:
                self.reset_to_db_default()
            raise custom_errors.ExceptionWarning(message=f"22A paper already exists with the same metadata. \n\nChanges were not saved.",title="Duplicate warning")

        
        def update_document_objects(document_object,valid_directory_path):            
            if document_object.different_file_path(valid_directory_path,self.__name):
                self.move_file_location(document_object,valid_directory_path,copy=copy)

        valid_directory_path=self.create_directory_path()
        for document_id in self.__questionpaper_documents:
            update_document_objects(self.__questionpaper_documents[document_id],valid_directory_path)
        for document_id in self.__markscheme_documents:
            update_document_objects(self.__markscheme_documents[document_id],valid_directory_path)
        for document_id in self.__attachment_documents:
            update_document_objects(self.__attachment_documents[document_id],valid_directory_path)
       


    def is_valid_pdf(self,path):
        if os.path.exists(os.path.join(os.getcwd(),path)) and str(path)[-4:] == ".pdf": 
            return True
        else: return False

    def pretty_level(self):
        if self.__level == "SL": return "Standard Level"
        if self.__level == "HL": return "Higher Level"
        else: return self.__level

    def create_directory_path(self):

        path = "Papers"
        print(self.__course_type)
        path += "/" + values_and_rules.get_course_types()[self.__course_type]
        if self.pretty_subject() != "": path += "/" + self.pretty_subject()
        if self.pretty_level() != "": path += "/" + self.pretty_level()
        if self.pretty_year() != "": path += "/" + self.pretty_year()
        if self.pretty_session() != "": path += "/" + self.pretty_session()
        if self.pretty_timezone() != "": path += "/" + self.pretty_timezone()



        return os.path.join(os.getcwd(),path)


    def check_minimum_requirements(self):

        for req in self.regex_requirements["minimum_requirements"]:
            if self.attributes_dict[req].strip()=="":
                return False
        return True

    def update_database(self, pdf_files_only = False,clean_dir = True,copy=False,override_duplicate_warning=False,new_obj=False):
        """
        FUNCTION: sync the internal object elements from this class with those of the original Pandas database
        WARNING: ALL ELEMENTS WITHIN THIS OBJECT MUST BE A VALID DATATYPE FOR THE PANDAS DATAFRAME. Use the self.update_object() method before calling this one
        """
        self.update_object(copy=copy,override_duplicate_warning=override_duplicate_warning,new_obj=new_obj)    
        
        """
        if self.db_row_injected == False:
            none_array = []
            
            
            for i in list(range(len(self.db.columns))):
                none_array.append(None)

            self.db.loc[self.db.shape[0]] = none_array
            self.db_row_injected=True
        """
        #if self.__db_id==None or self.__db_id=="":
        #    self.__db_id=str(uuid.uuid4())
        self.db.at[self.__db_id, "ID"] = self.__db_id

        if pdf_files_only == False:
            """

            self.db.at[self.__db_id, "Year"] = str(self.__year)
            self.db.at[self.__db_id, "Session"] = self.__session
            self.db.at[self.__db_id, "Timezone"] = str(self.__timezone)
            self.db.at[self.__db_id, "Paper"] = self.__paper
            self.db.at[self.__db_id, "Subject"] = self.__subject
            self.db.at[self.__db_id, "Level"] = self.__level

            self.db.at[self.__db_id, "Mark"] = self.__mark
            self.db.at[self.__db_id, "Maximum"] = self.__maximum
            self.db.at[self.__db_id, "Notes"] = self.__notes
            """

            for attribute in self.attributes_dict:
                self.db.at[self.__db_id,attribute]=self.attributes_dict[attribute]

            self.db.at[self.__db_id, "NormalFormat"] = self.__normal_format
            self.db.at[self.__db_id, "CustomName"] = self.__custom_name
            self.db.at[self.__db_id, "CourseType"] = self.__course_type

            self.db.at[self.__db_id, "CompletedDate"] = str(self.__completed_date)

            
            self.db.at[self.__db_id, "IgnoreUpdate"] = self.__ignore_update
        
            self.db.at[self.__db_id, "GradeBoundaries"] = json.dumps(self.__grade_boundaries)

            self.db.at[self.__db_id, "GBMAX"] = self.__gbmax


        # serialising document objecs
        questionpaper_documents = self.serialise_object_dict(self.__questionpaper_documents)
        markscheme_documents = self.serialise_object_dict(self.__markscheme_documents)
        attachment_documents = self.serialise_object_dict(self.__attachment_documents)

        self.db.at[self.__db_id, "QuestionPaperDocuments"] = json.dumps(questionpaper_documents)
        self.db.at[self.__db_id, "MarkschemeDocuments"] = json.dumps(markscheme_documents)
        self.db.at[self.__db_id, "AttachmentDocuments"] = json.dumps(attachment_documents)
        self.db.to_csv('database.csv',index=True)

        if clean_dir:
            self.mainline.clean_dir()



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

    def move_file_location(self,document_obj,file_type=None,new_directory_path=None,copy=False,ignore_duplicate=False):
        
        """
        Move or copy a document to a new location.

        IN:
        - document (DocumentData object)
        - OPTIONAL new_directory_path (path which the document object needs to be moved to. Default automatically generated based on Paper Object)
        - OPTIONAL copy (default False): sets the copy/replace setting
        - OPTIONAL ignore_duplicate (default False): will override duplicates if set to True
        """
        if new_directory_path==None:
            cwd = os.getcwd()
            document_path = self.create_directory_path()
            new_directory_path=os.path.join(cwd,document_path)

        if os.path.exists(document_obj.get_current_file_path()):

            new_file_name= self.create_file_name(document_obj.get_file_type())

            document_obj.set_directory_path(new_directory_path,new_file_name,copy=copy)



    def delete_path(self,type,index,ignore_removed_pdf=False):
        
        return_msg = ""
        if type == "original":
            return_msg = self.delete_original(index,ignore_removed_pdf=ignore_removed_pdf)
        if type == "markscheme":
            return_msg = self.delete_markscheme(index,ignore_removed_pdf=ignore_removed_pdf)
        if type == "otherattachments":
            return_msg = self.delete_otherattachments(index,ignore_removed_pdf=ignore_removed_pdf)
        return return_msg



    def browse_file_input(self, document_type,override_path="",suffix="",completed_function=None,do_not_update_object=False):
        """
        Prompt user to add a questionpaper, markscheme or attachment to the Paper Object
        
        IN:
        - document_type (str): either "questionpaper", "markscheme" or "attachment" -> this will decide where the generated document is saved
        - completed_function: any method to be run once the process has completed
        """

        if override_path =="":
            # TODO: remove tk filedialog to outside class
            file_path = tk.filedialog.askopenfilename(initialdir = "Downloads",title = f"Select file")
        else:
            file_path=override_path
        if os.path.exists(file_path):
            # file name without extension
            file_name=os.path.splitext(os.path.basename(file_path))[0]   
            file_extension=os.path.splitext(os.path.basename(file_path))[-1]   
            directory_path = os.path.dirname(file_path)

        
            

            if document_type=="questionpaper":
                new_document_obj = self.DocumentData(self.__questionpaper_documents,self)
                self.__questionpaper_documents[new_document_obj.get_id()]=new_document_obj
                new_document_obj.set_file_type("questionpaper")
                new_document_obj.set_suffix(suffix)

            elif document_type=="markscheme":
                new_document_obj = self.DocumentData(self.__markscheme_documents,self)
                self.__markscheme_documents[new_document_obj.get_id()]=new_document_obj
                new_document_obj.set_file_type("markscheme")
                new_document_obj.set_suffix(suffix)
            elif document_type=="attachment":
                new_document_obj = self.DocumentData(self.__attachment_documents,self)
                self.__attachment_documents[new_document_obj.get_id()]=new_document_obj
                new_document_obj.set_file_type("attachment")
                new_document_obj.set_suffix(suffix)

            new_document_obj.set_original_file_name(file_name)
            new_document_obj.set_file_extension(file_extension)
            new_document_obj.set_original_directory_path(directory_path)

            if not do_not_update_object:
                self.update_object(copy=True)
            

            if completed_function != None:
                completed_function()
            
        return new_document_obj
    
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


    def delete_otherattachments(self,index,ignore_removed_pdf=False):
        return_msg = self.remove_file(self.__otherattachments[index]["path"])
        if return_msg == True or ignore_removed_pdf==True: return self.__otherattachments.pop(index)
        else: return str(return_msg)



    def set_original(self,original,index = -1):
        self.__original[index]["path"]=original

    def set_original_path(self, original, index = -1):
        if index == -1: 
            self.__original.append({"path":original,"valid":True,"identifier":""})
            return_index = len(self.__original)-1
        else:
            self.__original[index]["path"]=original
            return_index = index
        return return_index

    def get_questionpaper_documents(self):
        return self.__questionpaper_documents
    def get_markscheme_documents(self):
        return self.__markscheme_documents
    def get_attachment_documents(self):
        return self.__attachment_documents

    def remove_original_path(self,path):
        
        for i,path1 in enumerate(self.__original):
            if path1["path"]==path:
                self.__original.pop(i)

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

    def remove_markscheme_path(self,path):
        for i,path1 in enumerate(self.__markscheme):
            if path1["path"]==path:
                self.__markscheme.pop(i)


    def set_markscheme_valid(self,markscheme,index):

        self.__markscheme[index]["valid"]=markscheme

    def set_markscheme_identifier(self,markscheme,index):
        self.__markscheme[index]["identifier"]=markscheme

    def set_otherattachments_path(self, otherattachments, index = -1,unique_identifier=""):
        if index == -1: 
            self.__otherattachments.append({"path":otherattachments,"valid":True,"identifier":unique_identifier})
            return_index = len(self.__otherattachments)-1
        else:
            self.__otherattachments[index]["path"]=otherattachments
            return_index = index
        return return_index

    def remove_otherattachments_path(self,path):
        for i,path1 in enumerate(self.__otherattachments):
            if path1["path"]==path:
                self.__otherattachments.pop(i)

    def set_otherattachments_valid(self,otherattachments,index):

        self.__otherattachments[index]["valid"]=otherattachments

    def set_otherattachments_identifier(self,otherattachments,index):

        self.__otherattachments[index]["identifier"]=otherattachments

    def set_markscheme(self, markscheme, index = -1):
        if index == -1: 
            self.__markscheme.append(markscheme)
        else:
            self.__markscheme[index]=markscheme

    def set_otherattachments(self, otherattachments, index = -1):
        if index == -1: 
            self.__otherattachments.append(otherattachments)
        else:
            self.__otherattachments[index]=otherattachments

    def set_printed(self, printed):
        self.__printed=printed
    def set_completed_date(self, completed_date):
        if completed_date != None:
            self.__completed_date=completed_date
            if not type(completed_date)==datetime.date:
                self.__completed_date_datetime=self.__completed_date.to_pydatetime()
                if pd.isnull(self.__completed_date_datetime):self.__completed_date_datetime=None
            else:
                self.__completed_date_datetime=completed_date

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
        path = self.create_directory_path()
        if os.path.exists(os.path.join(cwd,path)):
            os.startfile(os.path.join(cwd,path))
        else:
            tk.messagebox.showerror(message=f"Unable to open {str(os.path.join(cwd,path))}. It could be that the path does not exist, or that you do not have the permissions to access it.")

    # getters and setters
    def get_course_type(self):
        return self.__course_type

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
        if len(self.__markscheme) == 0: return ""
        return self.__markscheme[index]["identifier"]
    def get_markscheme_path(self, index):
        if len(self.__markscheme) == 0: return ""
        return self.__markscheme[index]["path"]
    def get_markscheme_valid(self, index):
        if len(self.__markscheme) == 0: return ""
        return self.__markscheme[index]["valid"]


    def get_otherattachments_identifier(self, index):
        if len(self.__otherattachments) == 0: return ""
        return self.__otherattachments[index]["identifier"]
    def get_otherattachments_path(self, index):
        if len(self.__otherattachments) == 0: return ""
        return self.__otherattachments[index]["path"]
    def get_otherattachments_valid(self, index):
        if len(self.__otherattachments) == 0: return ""
        return self.__otherattachments[index]["valid"]

    def pass_setter(self,e):
        pass

    def get_markscheme(self, index = -1):
        return self.__markscheme
    def get_otherattachments(self, index = -1):
        return self.__otherattachments
    def get_printed(self):
        return self.__printed
    def get_completed_date(self):
        return self.__completed_date
    def get_completed_date_pretty(self):
        if self.__completed_date_datetime != None:
            return values_and_rules.format_date(self.__completed_date_datetime)
        else: return ""
    def get_completed_date_datetime(self):
        return self.__completed_date_datetime
    def get_completed(self):
        return self.__completed
    def get_partial(self):
        return self.__partial

    def get_notes(self):
        return self.__notes
    def get_id(self):
        return self.__db_id
    def get_name(self):
        return self.__name

    def set_percentage(self):
        pass
    def get_percentage(self):
        return round(self.__percentage,2)
    def get_percentage_pretty(self):
        if self.__percentage != -1 and self.__maximum != 0:
            rounded_percentage=round(self.__percentage*100,2)

            return str(rounded_percentage) + "%"
        else: return ""

    def get_grade_pretty(self):
        if str(self.__grade) != "-1" and self.__maximum != 0:
            return self.__grade
        else: return ""
    def get_mark(self):
        return self.__mark
    def get_maximum(self):
        return self.__maximum

    def generate_grade(self):
        

        if self.is_valid_gbmax():
            for grade_boundary in self.__grade_boundaries:
                
                grade_boundary_value_percentage = self.__grade_boundaries_percentages[grade_boundary]

                if self.__percentage >= grade_boundary_value_percentage:
                    self.__grade = grade_boundary
                    break # break out of loop
                self.__grade = -1 # edge case

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

    def get_key_from_value(self,dict,value):
        for key in dict:
            if dict[key]==value:

                return key
        return value

    def create_name(self):
        """
        Creates a name for the object based on the data read from the dataframe. This name will either:
        - follow the conventional naming format for past papers
        - take on the custom name provided by the data if the data row does not adhere to the past paper formatting
        """

        session = self.get_key_from_value(self.terminology["dict_session"],self.__session)
        timezone = self.get_key_from_value(self.terminology["dict_timezone"],self.__timezone)
        paper = self.get_key_from_value(self.terminology["dict_paper"],self.__paper)
        level = self.get_key_from_value(self.terminology["dict_level"],self.__level)

        
        
        name = ""
        if self.__normal_format == True:
            name_array = []

            if str(self.__session) != "": name_array.append(str(session))
            if str(self.__year) != "": name_array.append(str(self.pretty_year()))
            if str(self.__timezone) != "": name_array.append(str(timezone))
            if str(self.__paper) != "": name_array.append(str(paper))
            if str(self.__subject) != "": name_array.append(str(self.mainline.settings.get_subject_code(self.__subject)))
            if str(self.__level) != "": name_array.append(str(level))


            name = "-".join(str(i) for i in name_array)
        elif self.__normal_format == False:
            name = self.__custom_name


        return name


class Database():


    def __init__(self, db_path,mainline):

        self.mainline=mainline
        self.db = pd.read_csv(db_path)
        date = datetime.datetime.now()
        
        # make the target directory if it does not yet exist
        if not os.path.exists("Backups"):
            os.makedirs("Backups")
        current_date = date.strftime("%d_%m_%Y-%H_%M_%S")
        self.db.to_csv(f'Backups/database-{current_date}.csv',index=False)
        # formatting
        self.db.dropna(subset = ["NormalFormat"], inplace=True)
        error = False
        try:
            self.db.astype({'NormalFormat': 'bool','Printed': 'bool','Completed': 'bool','Partial': 'bool','IgnoreUpdate':'bool'},errors='raise')
        except Exception as e:
            error = True
            tk.messagebox.showerror(message="Error when parsing data and converting boolean (True/False) datatypes. As to prevent data from being overriden, the database will not be accessed or manipulated until this is fixed.\n\nPlease ensure the CSV data file has either TRUE or FALSE under the boolean columns")
        self.db = self.db.replace(np.nan, '')
        try:
            self.db["CompletedDate"] = pd.to_datetime(self.db['CompletedDate'], dayfirst=True, errors='raise')
        except Exception as e:
            error = True
            tk.messagebox.showerror(message="Error when reading the date fields from the database. As to prevent data from being overriden, the database will not be accessed or manipulated until this is fixed.\n\nPlease ensure the CSV date format has not been corrupted opening it in MS Excel. If so, open the CSV as change the date format to DD/MM/YYYY\n\nError: "+ str(e))
        
        self.db.set_index('ID', inplace=True)
        if not error:
            self.paper_objects = {}
            self.db_index = 0
            for id, row in self.db.iterrows():
                self.paper_objects[id]=PaperObject(self,self.db, self.mainline)
                self.paper_objects[id].assign_db_data(row,id)
        else:
            sys.exit()

    def create_new_row(self):
        """
        Will create a new database element, however will NOT save it to the pandas dataframe or an array. This new object must be passed into the save_row() function to do so.
        """
        new_row_object = PaperObject(self,self.db, self.mainline)
        return new_row_object

    def check_row_exists(self,row_obj):
        """
        Will check if a given row object already exists within the database. Return True if exists, False if not
        - row_obj: the item being checked
        OUT:
        - exists (bool): True if it does already exist, False if it does not
        """
        #print (self.paper_objects)
        for row_id in self.paper_objects:
            row=self.paper_objects[row_id]
            if row != None:
                if row != row_obj and row.get_name() == row_obj.get_name():
                    return True
                else:
                    pass
        return False

    def save_row(self, row, copy = True,override_duplicate_warning = True):

        if self.check_row_exists(row):
            raise custom_errors.ExceptionWarning(message="11The metadata entered already exists in the database. \n\nThe object was not created",title="Duplicate warning")

        self.paper_objects[row.get_id()]=row
        row.update_database(copy = copy,override_duplicate_warning = override_duplicate_warning,new_obj=True)

