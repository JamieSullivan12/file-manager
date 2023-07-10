# third party import
import datetime, json, shutil, os, uuid, dateparser
import pandas as pd
import tkinter as tk
import numpy as np
import pandas


# internal import
import values_and_rules, custom_errors, CommonFunctions



class PastPaper():

    class DocumentItem():
        


        def remove_document_from_dict(self):
            
            del self.master_dict[self.get_id()]


        def remove_document(self):
            try:
                os.remove(self.get_current_file_path())
            except Exception as e:
                #print(e)
                pass
            self.remove_document_from_dict()
            self.__del__()
        def file_path_already_exists(self,new_file_path):

            new_file_path = os.path.join(new_file_path, self.generate_new_file_name(extension=True))

            for document in self.master_dict:
                if self.master_dict[document].get_current_file_path() == new_file_path and self.master_dict[document].get_id()!=self.get_id():
                    return True
            return False

        def generate_new_file_name(self,override_new_file_name=None,extension=False):
            """
            Generate the name of the file based on attributes: prefix, file_name, suffix and 
            
            """
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
        # GETTERS

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
        
        # SETTERS

        def move_file(self,new_directory_path,new_file_name,copy=False):
            """
            Change the object's file path, and apply the change by moving/copying the file over to the new location/path. 

            IN:
            - new_directory_path (str): the path to which the file needs to be moved
            - new_file_name (str): the BASE name which the file will have in the new path
            - copy (Bool): flag indicating whether the file needs to be moved (False) or copied (True)
            """


            self.set_file_name(new_file_name)
            # ensure the destination directory exists
            if not os.path.exists(new_directory_path):
                os.makedirs(new_directory_path)

            # ensure the file being moved with not override an existing file with the same name in the destination directory. 
            # This is done using an incrementing number at the end of the file name (this is hidden from the user)
            self.reset_numberid()
            while self.file_path_already_exists(new_directory_path) == True:
                self.increment_numberid()
        
            # complete the copy or move operation on the file
            new_file_path=self.generate_new_file_path(override_new_directory_path=new_directory_path)
            if new_file_path != self.get_current_file_path():
                if copy == True:
                    shutil.copy(self.get_current_file_path(),new_file_path)
                else:
                    shutil.move(self.get_current_file_path(),new_file_path)

            self.__directory_path=new_directory_path
            self.set_original_file_name(self.generate_new_file_name())

        def set_document_type(self,value):
            self.__file_type=value

        def set_original_file_name(self,value):
            self.__original_file_name=value

        def set_prefix(self,value):
            self.__prefix=value

        def set_file_name(self,value):
            self.__file_name=value

        def set_file_extension(self,value):
            self.__file_extension=value.replace(".","")

        def set_original_directory_path(self,new_directory_path):
            self.__directory_path=new_directory_path

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
            self.set_document_type(dict["file_type"])
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
        
        def __init__(self,master_dict):
            """
            IN:
            - master_dict: the dictionary of DocumentItem objects to which this DocumentItem belongs
            """

            self.__id=str(uuid.uuid4())
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
    
    def create_non_duplicate_name(self):
        new_name = self.__db_obj.generate_non_duplicate_name()
        self.set_custom_name(new_name)
        self.update_object()

    def update_document_objects(self,document_object,valid_directory_path,copy):            
        if document_object.different_file_path(valid_directory_path,self.__name):
            self.move_document_location(document_object,valid_directory_path,copy=copy)

    
    def update_object(self,copy=False,new_obj=False,init_load=False):
        """
        Validate attributes in the object

        RAISE
        - custom_errors.ExceptionWarning in case if insufficient data entry OR an already existing paper in the database
        """

        self.attributes_dict = {"Year":str(self.__year),"Session":str(self.__session),"Timezone":str(self.__timezone),"Paper":str(self.__paper),"Subject":str(self.__subject),"Level":str(self.__level),"Mark":str(self.__mark),"Maximum":str(self.__maximum),"Notes":self.__notes}
        

        # ensure enough data exists to constitute a paper object (defined in the values_and_rules file)
        if not self.validate_minimum_data():
            if not new_obj:
                self.reset_to_db_default()
            required = []
            for x in self.__regex_requirements["minimum_requirements"]:
                required.append(self.__terminology[x])
            required = "\n".join(required)
            raise custom_errors.ExceptionWarning(message=f"The data entered in insufficient to constitute a paper entry. \n\nMinimum required fields:\n{required}.\n\nChanges were not saved.",title="Insufficient data")

        # override name flag
        if self.__custom_name != "":
            self.__normal_format = False
        else:
            self.__normal_format = True

        self.generate_percentage()
        # generate a grade based on given mark and maximum values as well as given grade boundaries
        self.generate_grade()

        # match the given subject to a subject code (or create a new subject code)
        if not self.__mainline.settings.subject_name_exists(self.get_subject()):
            self.__mainline.settings.add_subject(self.get_subject())

        # create past paper name based on all attributes
        self.__name = self.generate_name()
        # ensure no duplicate past papers exist
        if self.validate_no_duplicates():
            if not new_obj and not self.reset_once:
                self.reset_once = True
                if init_load:
                    self.reset_to_db_default(raise_error=False)
                else:
                    self.reset_once = False
                    self.reset_to_db_default(raise_error=True)
                    

                return

            if self.reset_once:
                self.create_non_duplicate_name()
                return

        # validate all attachment documents to this past paper
        valid_directory_path=self.generate_documents_directory()
        for document_id in self.__questionpaper_documents:
            self.update_document_objects(self.__questionpaper_documents[document_id],valid_directory_path,copy=copy)
        for document_id in self.__markscheme_documents:
            self.update_document_objects(self.__markscheme_documents[document_id],valid_directory_path,copy=copy)
        for document_id in self.__attachment_documents:
            self.update_document_objects(self.__attachment_documents[document_id],valid_directory_path,copy=copy)
       

    def generate_documents_directory(self):
        """
        Generate the path for the directory in which document attachments to this paper object are stored
        """

        session = self.get_key_from_value(self.__terminology["dict_session"],self.__session)
        timezone = self.get_key_from_value(self.__terminology["dict_timezone"],self.__timezone)
        level = self.get_key_from_value(self.__terminology["dict_level"],self.__level)

        path = "ExamDocumentManager"
        path += "/" + values_and_rules.get_course_types()[self.__course_type]
        if self.__subject != "": path += "/" + self.__subject
        if level != "": path += "/" + level
        if self.get_year(pretty=True) != "": path += "/" + self.get_year(pretty=True)
        if session != "": path += "/" + session
        if timezone != "": path += "/" + timezone

        return os.path.join(self.__mainline.settings.get_Configuration_path(),path)

    def generate_percentage(self):
        if type(self.get_mark())==float and type(self.get_maximum())==float:
            if self.get_maximum() > self.get_mark() and self.get_mark()>0:
                self.__percentage = self.get_mark()/self.get_maximum()

    def generate_grade(self):
        """
        Generate the grade based on the grade boundaries, mark and maximum mark

        EXAMPLE:
        81/100 will constitute a grade of 7 IF the grade boundary of a 7 is 81/100 or above
        68/100 will constitute a grade of 5 IF the grade boundary of a 5 is 60/100 TO 74/100
        """
        if self.get_gbmax()!="" or self.get_gbmax()==0:
            for grade_boundary in self.__grade_boundaries:
                grade_boundary_value_percentage = self.__grade_boundaries_percentages[grade_boundary]
                if self.__percentage >= grade_boundary_value_percentage:
                    self.__grade = grade_boundary
                    break # break out of loop
                self.__grade = -1 # edge case

        else:
            self.set_gbmax(0)

    def get_key_from_value(self,dict,value):
        for key in dict:
            if dict[key]==value:
                return key
        return value




    def generate_name(self):
        """
        Generate a name for the PastPaper object based on attributes such as the year, session, timezone, subject, paper and level. This name is used in the name of attached files
        and used to display a summary of the PastPaper object attributes to the user

        OUT:
        - name (str): the generated name
        """

        # get the session, timezone, paper and level in a shortened form
        # EXAMPLE: if self.__session == "May" then the shortened value is "M" -> this is defined in self.__terminology
        # the shortened value is in the key of the defined dictionaries in self.__terminology, thus the reason for the function get_key_from_value()
        session = self.get_key_from_value(self.__terminology["dict_session"],self.__session)
        timezone = self.get_key_from_value(self.__terminology["dict_timezone"],self.__timezone)
        paper = self.get_key_from_value(self.__terminology["dict_paper"],self.__paper)
        level = self.get_key_from_value(self.__terminology["dict_level"],self.__level)
        
        name = ""
        if self.__normal_format == True:
            name_array = []

            if str(self.__session) != "": name_array.append(str(session))
            if str(self.__year) != "": name_array.append(str(self.get_year(pretty=True)))
            if str(self.__timezone) != "": name_array.append(str(timezone))
            if str(self.__paper) != "": name_array.append(str(paper))
            if str(self.__subject) != "": name_array.append(str(self.__mainline.settings.get_subject_code(self.__subject)))
            if str(self.__level) != "": name_array.append(str(level))

            name = "-".join(str(i) for i in name_array)
        
        elif self.__normal_format == False:
            name = self.__custom_name
        
        if name=="" or name==None:
            name = "No attributes"

        return name


    def generate_document_name(self, type, suffix = ""):
        """
        Generate a file name for documents attached to this PastPaper object (name based on object attributes such as year, session, timezone and the type of attachment)
        """

        # prefix shows the type of attachment (questionpaper,markscheme,attachment)
        if type == "questionpaper": prefix = "questionpaper"
        if type == "markscheme": prefix = "markscheme"
        if type == "attachment": prefix = "attachment"

        # add the main body of the name (from self.__name which is generated automatically during an object refresh)
        new_file_name = prefix+"-"+self.__name

        # add a custom suffix (defined by the user)
        if suffix != "":
            new_file_name = new_file_name + "-" + suffix
        
        return new_file_name


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


    def deserialise_object_dict(self,dict,object_instantiator,class_args=None):
        """
        Create new instances of an object based on a serialised dictionary where:
        - key is the unique ID of each object
        - value is the serialised dictionary that can be passed into a .deserialise(dict) function in the newly created object

        IN:
        - dict: the dictionary to be deserialised
        - object_instantiator: the class which is to be instantiated for each key in the dictionary
        """
        deserialised_dict={}
        for key in dict:
            if class_args!=None:
                new_object = object_instantiator(deserialised_dict,class_args)
            else: new_object=object_instantiator(deserialised_dict)
            new_object.deserialise(dict[key])
            deserialised_dict[key]=new_object
        return deserialised_dict


    def validate_no_duplicates(self):
        return self.__db_obj.check_row_exists(self)


    def validate_minimum_data(self):
        """
        Check attributes of this Past Paper object to ensure a minimum amount of data requirement is met

        OUT:
        - bool specifying whether the requirements have been met (True) or not (False)
        """
        if self.__custom_name != "" and self.__custom_name != None:
            return True

        for req in self.__regex_requirements["minimum_requirements"]:
            # loop through all attributes needing to be checked (stored in attributes_dict) and reference the respective attribute names 
            # with the minimum requirements from the values_and_rules file
            if self.attributes_dict[req].strip()=="":
                return False
        return True


    def update_database(self,clean_dir = True,copy=False,new_obj=False,init_load=False):
        """
        FUNCTION: sync the internal object elements from this class with those of the original Pandas database
        WARNING: ALL ELEMENTS WITHIN THIS OBJECT MUST BE A VALID DATATYPE FOR THE PANDAS DATAFRAME
        """
        self.update_object(copy=copy,new_obj=new_obj,init_load=init_load)    
        #self.__db.at[self.__db_id, "ID"] = self.__db_id
        for attribute in self.attributes_dict:
            self.__db.at[self.__db_id,attribute]=self.attributes_dict[attribute]
        self.__db.at[self.__db_id, "NormalFormat"] = self.__normal_format
        self.__db.at[self.__db_id, "CustomName"] = self.__custom_name
        self.__db.at[self.__db_id, "CourseType"] = self.__course_type
        self.__db.at[self.__db_id, "CompletedDate"] = str(self.__completed_date)
        self.__db.at[self.__db_id, "GradeBoundaries"] = json.dumps(self.__grade_boundaries)
        self.__db.at[self.__db_id, "GBMAX"] = self.__gbmax

        # serialising document objects
        questionpaper_documents = self.serialise_object_dict(self.__questionpaper_documents)
        markscheme_documents = self.serialise_object_dict(self.__markscheme_documents)
        attachment_documents = self.serialise_object_dict(self.__attachment_documents)

        self.__db.at[self.__db_id, "QuestionPaperDocuments"] = json.dumps(questionpaper_documents)
        self.__db.at[self.__db_id, "MarkschemeDocuments"] = json.dumps(markscheme_documents)
        self.__db.at[self.__db_id, "AttachmentDocuments"] = json.dumps(attachment_documents)
        self.__db.to_csv(self.__db_path,index=True)



    def assign_db_data(self,db_row, db_id):
        """
        Deserialise a pandas database row into the PaperItem class attributes for this object

        IN:
        - rb_row: pandas database row to be deserialised
        - db_id: the ID of the pandas database row to be deserialised
        """

        self.__db_id = db_id
        self.__db_row = db_row

        # reading in all attributes in the data row from the database (text -> Python string)
        self.__normal_format = str(self.__db_row["NormalFormat"])
        self.__custom_name = str(self.__db_row["CustomName"])           

        course_type = self.__db_row["CourseType"]
        if str(course_type) != "":
            if str(course_type) in values_and_rules.get_coursecode_list():
                self.__course_type = self.__db_row["CourseType"]
        else:
            return "ERROR"
        self.set_session(str(self.__db_row["Session"]),override=True)
        self.set_year(str(self.__db_row["Year"]),override=True)
        self.set_timezone(str(self.__db_row["Timezone"]),override=True)
        self.set_paper(str(self.__db_row["Paper"]),override=True)      
        self.set_subject(str(self.__db_row["Subject"]),override=True)
        self.set_level(str(self.__db_row["Level"]),override=True)
        self.set_completed_date(str(self.__db_row["CompletedDate"]))
        self.set_mark(str(self.__db_row["Mark"]),override=True)
        self.set_maximum(str(self.__db_row["Maximum"]),override=True)
        self.set_notes(str(self.__db_row["Notes"]),override=True)
        self.set_gbmax(str(self.__db_row["GBMAX"]),override=True)
        
        # reading in document data (PDF attachments to the PaperObject)
        # must be deserialsied JSON -> Python dictionary of DocumentItem objects (see DocumentItem class for more detailed information)
        # NOTE: data validation is handled by the DocumentItem class
        questionpaper_documents={}
        if str(self.__db_row["QuestionPaperDocuments"]) != "" and str(self.__db_row["QuestionPaperDocuments"]) != None and str(self.__db_row["QuestionPaperDocuments"]) != "{}":
            questionpaper_documents = json.loads(str(self.__db_row["QuestionPaperDocuments"]) or "{}")
        markscheme_documents={}
        if str(self.__db_row["MarkschemeDocuments"]) != "" and str(self.__db_row["MarkschemeDocuments"]) != None and str(self.__db_row["MarkschemeDocuments"]) != "{}":
            markscheme_documents = json.loads(str(self.__db_row["MarkschemeDocuments"]) or "{}")
        attachment_documents={}
        if str(self.__db_row["AttachmentDocuments"]) != "" and str(self.__db_row["AttachmentDocuments"]) != None and str(self.__db_row["AttachmentDocuments"]) != "{}":
            attachment_documents = json.loads(str(self.__db_row["AttachmentDocuments"]) or "{}")
        self.__questionpaper_documents=self.deserialise_object_dict(questionpaper_documents,self.DocumentItem,None)
        self.__markscheme_documents=self.deserialise_object_dict(markscheme_documents,self.DocumentItem,None)
        self.__attachment_documents=self.deserialise_object_dict(attachment_documents,self.DocumentItem,None)

        self.grade_boundaries={}
        self.__grade_boundaries_percentages={}
        # read in all grade boundaries attributed to this PastPaper object (JSON -> Python dictionary)
        if self.__db_row["GradeBoundaries"] != {} and self.__db_row["GradeBoundaries"] != None and self.__db_row["GradeBoundaries"] != "":
            grade_boundaries=json.loads(str(self.__db_row["GradeBoundaries"]) or "{}")
            self.__grade_boundaries = {}
            self.__grade_boundaries_percentages = {}

            for grade_boundary in grade_boundaries:
                self.__grade_boundaries[grade_boundary]=0
                self.__grade_boundaries_percentages[grade_boundary]=0
            
            for grade_boundary in self.__grade_boundaries:
                self.set_grade_boundary(grade_boundaries[grade_boundary],grade_boundary,override=True)
        elif self.__course_type in values_and_rules.get_coursecode_list():
            for grade_boundary in values_and_rules.get_course_grade_boundaries()[self.__course_type]:
                self.__grade_boundaries[grade_boundary]=0
                self.__grade_boundaries_percentages[grade_boundary]=0

        self.update_database(clean_dir=False,copy=False,init_load=True)


    def reset_to_db_default(self,raise_error=False):
        """
        Reset all data attributes in this object to the last saved state in the pandas database row
        """
        try:
            row = self.__db.loc[self.__db_id]
        except KeyError as e:
            raise custom_errors.ExceptionWarning(message="The metadata entered already exists in the database. \n\nThe object was not created",title="Duplicate warning")
        
        if raise_error:
            raise custom_errors.ExceptionWarning(message=f"A paper already exists with the same metadata ({self.__name}). \n\nChanges were not saved.",title="Duplicate warning")

        self.assign_db_data(row,self.__db_id)


    def open_documents_directory(self):
        """
        Open the directory in which all attachment documents are stored for this Paper Object in the file explorer. Note the directory is based on the attributes of this
        PastPaper object class (this is generated)

        Exceptions:
        - custom_errors.ExceptionWarning if the directory cannot be found
        """
        document_location_path = self.__mainline.settings.get_Configuration_path()
        path = self.generate_documents_directory()
        if os.path.exists(os.path.join(document_location_path,path)):
            CommonFunctions.open_file(os.path.join(document_location_path,path))
        else:
            raise custom_errors.ExceptionWarning(title="Unable",message=f"Unable to open {str(os.path.join(document_location_path,path))}. It could be that the path does not exist, or that you do not have the permissions to access it.")


    def move_document_location(self,document_obj,file_type=None,new_directory_path=None,copy=False):
        
        """
        Move or copy a document to a new location.

        IN:
        - document (DocumentItem object)
        - OPTIONAL new_directory_path: path which the document object needs to be moved to. Default automatically generated based on PastPaper object attributes (see self.generate_document_name())
        - OPTIONAL copy (default False): sets the copy/replace setting
        """

        # generate or retrieve the destination path folder of documents for this PastPaper object (based on attribute metadata or an override: new_directory_path)
        if new_directory_path==None:
            cwd = self.__mainline.settings.get_Configuration_path()
            document_path = self.generate_documents_directory()
            new_directory_path=os.path.join(cwd,document_path)

        # move the DocumentItem object: document_obj, to the desired location using in-built methods
        if os.path.exists(document_obj.get_current_file_path()):
            new_file_name= self.generate_document_name(document_obj.get_file_type())
            document_obj.move_file(new_directory_path,new_file_name,copy=copy)


    def create_insert_new_document(self, document_type,override_path="",suffix="",completed_function=None,do_not_update_object=False):
        """
        Create a new document attachment to the PastPaper object. Will prompt with a file selection box if override_path == ""
        
        IN:
        - document_type (str): either "questionpaper", "markscheme" or "attachment" -> this will decide where the generated document is saved
        - suffix (str): a string appended to the file name in the save location (default "")
        - completed_function (method): any method to be run once the process has completed (default None)
        - do_not_update_object (Bool): boolean value determiniming (default False) if the PastPaper object should be updated, meaning all changes are saved (default False)
        
        OUT:
        - the new DocumentItem object OR None if no file was selected in the dialogue box
        """

        if override_path =="":
            # TODO: remove tk filedialog to outside class
            file_path = tk.filedialog.askopenfilename(initialdir = "Downloads",title = f"Select file")
            if file_path=="":
                return None
        else:
            file_path=override_path
        if os.path.exists(file_path):
            # file name without extension
            base_file_name=os.path.splitext(os.path.basename(file_path))[0]   
            # eg pdf or jpg
            file_extension=os.path.splitext(os.path.basename(file_path))[-1] 
            # folder name (e.g. users/name/files -> folder name is "files")
            folder_name = os.path.dirname(file_path)

        
            # create the new DocumentItem objects (based on document_type)
            if document_type=="questionpaper":
                new_document_obj = self.DocumentItem(self.__questionpaper_documents)
                # save the new object to a dictionary of questionpaper DocumentItem objects
                self.__questionpaper_documents[new_document_obj.get_id()]=new_document_obj

            elif document_type=="markscheme":
                new_document_obj = self.DocumentItem(self.__markscheme_documents)
                self.__markscheme_documents[new_document_obj.get_id()]=new_document_obj

            elif document_type=="attachment":
                new_document_obj = self.DocumentItem(self.__attachment_documents)
                self.__attachment_documents[new_document_obj.get_id()]=new_document_obj
                
            # insert document metadata into the new DocumentItem object
            new_document_obj.set_document_type(document_type)
            new_document_obj.set_suffix(suffix)
            new_document_obj.set_original_file_name(base_file_name)
            new_document_obj.set_file_extension(file_extension)
            new_document_obj.set_original_directory_path(folder_name)

            if not do_not_update_object:
                self.update_object(copy=True)
            
            if completed_function != None:
                completed_function()
            
        return new_document_obj


    # GETTERS and SETTERS + validation functions for the setters

    def float_validation(self, validate_string):
        """
        Convert a string to a float. Complete validation check, returning an empty string "" if validation fail

        IN:
        - validate_string: the string needing to be converted to a float

        OUT:
        - EITHER an empty string (if float invalid) OR the float value of the validation string
        """
        try:
            return float(validate_string)
        except ValueError:
            return ""
        
  
    def int_validation(self, validate_string):
        """
        Convert a string to a int. Complete validation check, returning an empty string "" if validation fail

        IN:
        - validate_string: the string needing to be converted to an int

        OUT:
        - EITHER an empty string (if int is invalid) OR the int value of the validation string
        """
        try:
            return int(validate_string)
        except ValueError:
            return ""


    # SETTERS (note: includes validation)
        
    def set_id(self,db_id):
        self.__db_id = db_id

    def set_normal_format(self, normal_format):
        self.__normal_format=normal_format

    def set_custom_name(self, custom_name,override=False):
        self.__custom_name=str(custom_name)
        return True,"","" 

    def set_year(self, year,override=False):
        """
        Validation requirement: int
        """
        if year.isdigit() or year == "":
            self.__year=self.int_validation(year)
        else:
            if override:
                self.__year=""
            return False,"Must be a whole number","Year"
        return True,"",""
    
    def set_session(self, session,override=False):
        self.__session=str(session)
        return True,"","" 

    def set_timezone(self, timezone,override=False):
        self.__timezone=str(timezone)
        return True,"","" 

    def set_paper(self, paper,override=False):
        self.__paper=str(paper)
        return True,"","" 

    def set_subject(self, subject,override=False):
        self.__subject=str(subject)
        return True,"","" 

    def set_level(self, level,override=False):
        self.__level=str(level)
        return True,"","" 

    def set_mark(self, mark,override=False):
        """
        Validation requirement: float
        """
        if CommonFunctions.is_float(mark):
            self.__mark = self.float_validation(mark)
        else:
            if override:
                self.__mark = 0.00
            return False,"Must be a number","Mark"
        return True,"",""
            
    
    def set_maximum(self, maximum,override=False):
        """
        Validation requirement: float
        """
        if CommonFunctions.is_float(maximum):
            self.__maximum = self.float_validation(maximum)
        else:
            if override:
                self.__maximum = 0.00
            return False,"Must be a number","Maximum"
        return True,"",""
       


    def set_gbmax(self,gbmax,override=False):
        """
        Validation requirement: float AND > 0
        """
        if CommonFunctions.is_int(gbmax):
            self.__gbmax=self.int_validation(gbmax)

            if self.__gbmax > 0 and self.__gbmax!="":
                for grade_boundary in self.__grade_boundaries:
                    self.__grade_boundaries_percentages[grade_boundary]=round(float(self.__grade_boundaries[grade_boundary] / self.__gbmax),2)
            else:
                for grade_boundary in self.__grade_boundaries:
                    self.__grade_boundaries_percentages[grade_boundary]=0
 


        else:
            if override:
                self.__gbmax=0
                for grade_boundary in self.__grade_boundaries:
                    self.__grade_boundaries_percentages[grade_boundary]=0
            return False,"Must be a whole number","Grade boundary maximum"

        return True,"",""


    def set_notes(self, notes,override=False):
        self.__notes=str(notes)
        return True,"",""

    def get_completed_date_valid(self):
        if type(self.__completed_date_datetime) == datetime.datetime and self.__completed_date_datetime != "" and self.__completed_date_datetime != None:
            return True
        return False

    def set_completed_date(self, completed_date):
        """
        Set the completed_date attribute as a datetime.date object (will automatically convert from the three datatypes listed below)

        IN:
        - completed_date (pandas date OR string OR datetime.date): 
        """

        if completed_date != None:
            self.__completed_date=completed_date
            # if the passed attribute is not datetime.date then convert it and set self.__completed_date_datetime to the datetime object
            if type(completed_date)==pandas:
                self.__completed_date_datetime=completed_date.to_pydatetime()
                if pd.isnull(self.__completed_date_datetime):self.__completed_date_datetime=None
            elif type(completed_date)==str:
                self.__completed_date_datetime=dateparser.parse(completed_date,settings={'PREFER_DAY_OF_MONTH': 'first'})
            elif type(completed_date)==datetime.date:
                self.__completed_date_datetime=completed_date
        else: self.__completed_date=None
        return True,"",""
    def set_grade_boundary(self,grade_boundary_value,grade_boundary_code,override=False):
        """
        Add a new grade boundary to the PastPaper object. Inserted values are validated as floats
        
        IN:
        - grade_boundary_value (float): the minimum mark needed to achieve a particular grade boundary
        - grade_boundary_code (str): the grade boundary being modified (e.g. 7,6,5 for IB or A*,A,B for A-Levels). If an invalid code is given, the grade boundary will not be added
        """
        if str(grade_boundary_code) in self.__grade_boundaries:
            
            if CommonFunctions.is_int(grade_boundary_value):
                self.__grade_boundaries[grade_boundary_code]=int(grade_boundary_value)
                self.__grade_boundaries_percentages[grade_boundary_code]

                if int(grade_boundary_value) >= 0:
                    if self.get_gbmax()!="" and self.get_gbmax()!=0:
                        self.__grade_boundaries_percentages[grade_boundary_code]=int(grade_boundary_value)/int(self.get_gbmax())

                else:
                    if override:
                        self.__grade_boundaries[grade_boundary_code]=0
                        self.__grade_boundaries_percentages[grade_boundary_code]=0
                    return False,"Must be greater or equal to 0",f"{self.__terminology['Grade']} {grade_boundary_code}"

            else:
                if override:
                    self.__grade_boundaries[grade_boundary_code]=0
                    self.__grade_boundaries_percentages[grade_boundary_code]=0
                return False,"Must be a whole number",f"{self.__terminology['Grade']} {grade_boundary_code}"
        return True,"",""   

    def pass_setter(self,e):
        pass

    def set_percentage(self):
        pass

    # GETTERS

    def get_questionpaper_documents(self):
        return self.__questionpaper_documents
    
    def get_markscheme_documents(self):
        return self.__markscheme_documents
    
    def get_attachment_documents(self):
        return self.__attachment_documents

    def get_grade_boundary(self,grade_boundary_code):
        return self.__grade_boundaries[grade_boundary_code]

    def get_grade_boudary_percentage(self,grade_boundary_code):
        return self.__grade_boundaries_percentages[grade_boundary_code]

    def get_grade(self):
        return self.__grade

    def get_gbmax(self):
        return self.__gbmax
    
    def get_course_type(self):
        return self.__course_type
    
    def get_normal_format(self):
        return self.__normal_format
    
    def get_custom_name(self):
        return self.__custom_name
    
    def get_year(self,pretty=False):
        """
        Return the year attribute

        IN:
        - pretty (Bool): if pretty==True a check will be completed to return the year with 4 digits (e.g. 19 -> 2019)
        """

        if pretty:
            if len(str(self.__year)) == 2: return "20" + str(self.__year)
            else: return str(self.__year)
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

    def get_completed_date(self):
        return self.__completed_date
    
    def get_completed_date_pretty(self):
        """
        Return the completed date in a string format (defined in values_and_rules.py)
        """
        if self.__completed_date_datetime != None:
            return values_and_rules.format_date(self.__completed_date_datetime)
        else: return ""

    def get_completed_date_datetime(self):
        """
        Return the completed date as a datetime.date object
        """
        
        return self.__completed_date_datetime

    def get_notes(self):
        return self.__notes
    
    def get_id(self):
        return self.__db_id
    
    def get_name(self):
        return self.__name

    def get_percentage(self,pretty=False):
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


    def delete_past_paper_obj(self):
        """
        Delete the paper object (also delete all attached documents)
        """

        # remove all document attributes of the PastPaper
        for questionpaper in list(self.__questionpaper_documents.keys()):
            self.__questionpaper_documents[questionpaper].remove_document()
        for markscheme in list(self.__markscheme_documents.keys()):
            self.__markscheme_documents[markscheme].remove_document()
        for attachment in list(self.__attachment_documents.keys()):
            self.__attachment_documents[attachment].remove_document()
        # remove from database
        self.__db.drop(self.__db_id,inplace=True)
        self.__db.to_csv(self.__db_path,index=True)
        self.__db_obj.remove_paper_item(self.__db_id)
        



    def __init__(self, mainline, db_obj):
        """
        A PastPaper contains all attributes and methods pertaining to a single past paper (including year, session, subject etc.).

        IN:
        - mainline: the mainline object 
        - db_obj: the database object (this class instantiates PastPaper objects. A reverse coupling is required for particular methods such as deleting the PastPaper from the
                    database. Otherwise, all atttributes that must not be exchanged between these coupled functions is held private)
        """


        # database object and path
        self.__db_obj=db_obj
        self.__db_path=self.__db_obj.get_db_path()
        self.__db=self.__db_obj.get_pandas_database_obj()
        self.__mainline = mainline
        self.__course_type=self.__mainline.settings.get_course_type()
        
        # aesthetic: using the correct terminology in text on screen based on the course type
        self.__terminology=values_and_rules.get_terminology(self.__course_type)
        self.__regex_requirements = values_and_rules.get_regex_patterns(self.__course_type)

        # create unique ID for PastPaper instance (can be overriden later if read from CSV file)
        self.__db_id = str(uuid.uuid4())
        
        self.__db_row=None
        self.__normal_format = True
        self.reset_once = False


        # all PastPaper attributes - initialised empty
        self.__custom_name = ""  
        self.__year = "" # IB AL
        self.__session = "" # IB AL
        self.__timezone = "" # IB AL
        self.__paper = "" # IB AL
        self.__subject = "" # IB AL  
        self.__level = "" # IB
        self.__questionpaper_documents = {}
        self.__markscheme_documents = {}
        self.__attachment_documents = {}
        self.__completed_date = ""
        self.__completed_date_datetime = None
        self.__mark = 0.00
        self.__maximum = 0.00
        self.__percentage=-1
        self.__notes = ""

        # define a dictionary with key: grade boundary codes, value: grade boundary value            
        self.__grade_boundaries = {}
        self.__grade_boundaries_percentages = {}

        # setup all grade boundaries for this object (default value 0 for everything)
        for grade_boundary in values_and_rules.get_course_grade_boundaries()[self.__course_type]:
            self.__grade_boundaries[grade_boundary]=0
            self.__grade_boundaries_percentages[grade_boundary]=0
        self.__gbmax = 0
        self.__grade = -1

        self.__name = ""


    
class PastPaperDatabase():


    def get_pandas_database_obj(self):
        return self.__db

    def get_db_path(self):
        return self.__db_path

    def __init__(self,mainline, db_path):
        """
        Initialise, read and convert the past paper database into objects
        IN:
        - mainline object
        - path of the database
        """
        self.duplicate_counter=0
        self.__mainline=mainline
        self.__db_path=db_path
        self.__terminology=values_and_rules.get_terminology(self.__mainline.settings.get_course_type())

        headings = {"ID":str,"NormalFormat":str,"CustomName":str,"Year":str,"Session":str,"Timezone":str,"Paper": str,"Subject":str,"Level":str,"CompletedDate":str,"Mark":str,"Maximum":str,"Notes":str,"GBMAX":str,"GradeBoundaries":str,"CourseType":str,"QuestionPaperDocuments":str,"MarkschemeDocuments":str,"AttachmentDocuments":str}

        if os.path.exists(db_path):
            # import paper data into a pandas object
            self.__db = pd.read_csv(db_path,dtype=headings)
        else:
            self.__db = pd.DataFrame(columns=list(headings.keys()))

        if "ID" not in list(headings.keys()):
            raise custom_errors.CriticalError(title="CRITICAL: DATA CORRUPTION",message="The identifier (ID) column in the database has been removed or corrupted. Please either fix this or remove the database")


        for item in list(headings.keys()):
            if item not in self.__db.columns:
                self.__db = self.__db.reindex(columns = self.__db.columns.tolist() + [item])


        # create database backup
        date = datetime.datetime.now()
        if not os.path.exists("Backups"):
            os.makedirs("Backups")
        current_date = date.strftime("%d_%m_%Y-%H_%M_%S")
        self.__db.to_csv(f'Backups/database-{current_date}.csv',index=False)
        

        # formatting pandas data
        #self.__db.dropna(subset = ["NormalFormat"], inplace=True)
        error = False
        try:
            self.__db.astype({'NormalFormat': 'bool'},errors='raise')
        except Exception as e:
            error = True
            error_msg="Error when parsing data and converting boolean (True/False) datatypes. As to prevent data from being overriden, the database will not be accessed or manipulated until this is fixed.\n\nPlease ensure the CSV data file has either TRUE or FALSE under the boolean columns"
        self.__db = self.__db.replace(np.nan, '')
 
        try:

            import progressbar
            initload_progress = progressbar.CustomProgressBar(self.__mainline.top_frame,text="loading",total_number=len(list(self.__db.iterrows())))
            initload_progress.grid(row=1,column=0,sticky="new",padx=15,pady=15)
            counter = 0
            # use the ID column as the pandas index
            self.__db.set_index('ID', inplace=True)
            if not error:
                self.__paper_items = {}
                for id, row in self.__db.iterrows():
                    counter = counter + 1
                    initload_progress.update_progress_bar(counter)

                    if row["CourseType"]==self.__mainline.settings.get_course_type():
                        temp_paper_item=PastPaper(self.__mainline,self)
                        returned = temp_paper_item.assign_db_data(row,id)
                        if returned != "ERROR":
                            self.__paper_items[id]=temp_paper_item
                    else:
                        temp_paper_item=PastPaper(self.__mainline,self)
                        returned = temp_paper_item.assign_db_data(row,id)    
                        del temp_paper_item

                if self.duplicate_counter > 0:
                    custom_errors.ExceptionWarning(title="Duplicate documents found",message=f"{self.duplicate_counter} duplicate documents have been found in the database.\n\nNote: all duplicate documents have been given a temporary name such as 'Duplicate (number)' to prevent name overlap.")
            else:
                initload_progress.destroy()
                raise custom_errors.CriticalError(title="CRITICAL: DATA CORRUPTION",message=error_msg)
            initload_progress.destroy()
        except Exception as e:
            CommonFunctions.open_file(os.getcwd())
            raise custom_errors.CriticalError(title="Data corruption has occured",message="The database is in an invalid format that could not be automatically resolved, and has produced the following error:\n\n"+str(e)+"\n\nThe folder containing the database for this application will now be opened where you can manually fix the issue, or request support. \n\nDeleting the database will also solv the issue (however all data will be lost).")
            
            
    def create_new_row(self):
        """
        Create a new PastPaper instance.
        NOTE: this object is not saved to secondary storage until instructed to do so (through PastPaper.update_database())
        """
        new_row_object = PastPaper(self.__mainline,self)
        return new_row_object

    def get_paper_items(self):
        """
        Return the database of paper_items (no filters)
        """
        return self.__paper_items

    def get_filtered_paper_items(self,name_filter="",year_filter="",session_filter="",timezone_filter="",paper_filter="",subject_filter="",level_filter="",course_filter=""):
        """
        Filter the database of paper_items to adhere to filter requirements. 
        
        IN:
        - name_filter (default: None): string definig the filter for the name attribute
        - year_filter (default: None): string definig the filter for the year attribute
        - session_filter (default: None): string definig the filter for the session attribute
        - timezone_filter (default: None): string definig the filter for the timezone attribute
        - paper_filter (default: None): string definig the filter for the paper attribute
        - subject_filter (default: None): string definig the filter for the subject attribute
        - level_filter (default: None): string definig the filter for the level attribute

        OUT:
        - the filtered dictionary of paper_items (key=paper object ID,value=class object)
        """

        filtered_paper_items={}

        for paper_item_id in self.__paper_items:
            paper_item=self.__paper_items[paper_item_id]
            filter_flag = True


            def filter_contains(entered_value,search_strings):
                """
                Simple filter (matching entered_value in search_strings)
                
                IN:
                - entered_value (string): the user-entered value to be used in the search (note: comma's (,) will be used to separate user entries)
                - search_strings (list of strings): list of strings containing the data to be searched

                OUT:
                - boolean value indicating whether the search was successful (True) or unsuccessful (False) 
                """
                for seperate_entered_section in entered_value.split(","):
                    for search_string in search_strings:
                        if seperate_entered_section.casefold() in search_string.casefold():
                            return True
                    if seperate_entered_section=="" and  "".join(search_strings)=="":return True

                return False
        
            def filter_range_contains(entered_value,search_string):
                """
                Range filter, meaning the entered value is split by commas (,) and dashes (-) where:
                - commas indicate separate search entries
                - dashes indicate a range of values (e.g. 4-6 = 4,5,6)

                IN:
                - entered_value (string): the user-entered value to be used in the search
                - search_strings (list of strings): list of strings containing the data to be searched

                OUT:
                - boolean value indicating whether the search was successful (True) or unsuccessful (False) 
                
                """
                if entered_value == "":return True

                # split by comma
                for seperate_entered_section in entered_value.split(","):
                    # split by dash
                    range_split = seperate_entered_section.split("-")
                        
                    # validity check on numbers at both sides of the dash (must be int)
                    for i,range_split_item in enumerate(range_split):
                        if range_split_item.isdigit():
                            range_split[i]=int(range_split_item)
                        else:return False
                    
                    # create list of all numbers between the max and min search value
                    range_split.sort()
                    min = range_split[0]
                    max = range_split[-1]

                    # prevent any searches with too large range
                    if max-min > 50: return False
                    range_values = range(min,max+1,1)
                    for range_item in range_values:
                        if filter_contains(str(range_item),[str(search_string)]):
                            return True
                return False
            # apply filters
            if not filter_contains(name_filter,[paper_item.get_name()]):filter_flag=False
            if not filter_contains(session_filter,[paper_item.get_session(),paper_item.get_key_from_value(self.__terminology["dict_session"],paper_item.get_session()) + " " + paper_item.get_session()]):filter_flag=False
            if not filter_contains(timezone_filter,[paper_item.get_timezone(),paper_item.get_key_from_value(self.__terminology["dict_timezone"],paper_item.get_timezone()) + " " + paper_item.get_timezone()]):filter_flag=False
            if not filter_contains(paper_filter,[paper_item.get_paper(),paper_item.get_key_from_value(self.__terminology["dict_paper"],paper_item.get_paper()) + " " + paper_item.get_paper()]):filter_flag=False
            if not filter_contains(subject_filter,[paper_item.get_subject(),self.__mainline.settings.get_subject_code(paper_item.get_subject())]):filter_flag=False
            if not filter_contains(level_filter,[paper_item.get_level(),paper_item.get_key_from_value(self.__terminology["dict_level"],paper_item.get_level()) + " " + paper_item.get_level()]):filter_flag=False
            if not filter_range_contains(year_filter,paper_item.get_year()):filter_flag=False


            if filter_flag:filtered_paper_items[paper_item_id]=paper_item

        return filtered_paper_items

    def generate_non_duplicate_name(self):
        name = "Duplicate"
        counter = 1
        names = []
        for row_id in self.__paper_items:
            row_obj = self.__paper_items[row_id]
            names.append(row_obj.get_name())
        while name in names:
            name = f"Duplicate ({counter})"
            counter += 1
        self.duplicate_counter += 1
        return name




    def check_row_exists(self,row_obj):
        """
        Check if a given row object already exists within the database. Return True if exists, False if not
        
        IN:
        - row_obj: the item being checked
        
        OUT:
        - exists (bool): True if it does already exist, False if it does not
        """
        for row_id in self.__paper_items:
            row=self.__paper_items[row_id]
            if row != None:
                if row != row_obj and row.get_name() == row_obj.get_name() and row.get_course_type() == row_obj.get_course_type():
                    return True
                else:
                    pass
        return False

    def remove_paper_item(self,db_id):
        del self.__paper_items[db_id]

    def save_row(self, row, copy = True):
        """
        Save a paper object to secondary storage

        IN:
        - row: the ID of the paper object being saved
        - (optional) copy: whether any document attachments of the paper object should be copied (True) or moved (False)
        """

        if self.check_row_exists(row):
            raise custom_errors.ExceptionWarning(message="The metadata entered already exists in the database. \n\nThe object was not created",title="Duplicate warning")

        self.__paper_items[row.get_id()]=row
        row.update_database(copy = copy,new_obj=True)

