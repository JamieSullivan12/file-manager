import os
import subprocess
import sys
import uuid
import datetime
import pandas as pd
import dateparser
import tkinter as tk
from tkinter import filedialog
import custom_errors
import shutil
import CommonFunctions
import sqlite3


from enum import Enum

class DocumentType(Enum):
    QUESTION_PAPER = "questionpaper"
    MARK_SCHEME = "markscheme"
    ATTACHMENT = "attachment"

# Define the ALL_TYPES attribute to hold all document types
ALL_DOCUMENT_TYPES = (DocumentType.QUESTION_PAPER, DocumentType.MARK_SCHEME, DocumentType.ATTACHMENT)

class PastPaperDatabase:
    def __init__(self, mainline, db_directory, db_name):
        """
        A PastPaperDatabase contains all attributes and methods pertaining to the management of past paper data
        including attributes and methods for storage, retrieval, and manipulation.

        IN:
        - mainline (Mainline): the mainline object.
        - db_path (str): The path to the database file.
        """
        self.__mainline = mainline
        self.__course_type = self.__mainline.settings.get_course_type()
        self.__course_values = mainline.get_course_values()
        self.db_directory=db_directory
        self.db_name=db_name
        self.__db_path = os.path.join(db_directory,db_name)
        self.__connection = None
        self.__cursor = None
        self.__past_papers = {}
        self.__load_database()


    def __load_database(self):
        """
        Load the database file and create tables if not exist.
        """
        try:
            self.__connection = sqlite3.connect(self.__db_path)
            self.__cursor = self.__connection.cursor()
            self.__cursor.execute('''CREATE TABLE IF NOT EXISTS past_papers (
                                        id TEXT PRIMARY KEY,
                                        name TEXT,
                                        custom_name TEXT,
                                        year TEXT,
                                        session TEXT,
                                        timezone TEXT,
                                        paper TEXT,
                                        subject TEXT,
                                        level TEXT,
                                        completed_date TEXT,
                                        mark REAL,
                                        maximum REAL,
                                        percentage REAL,
                                        notes TEXT,
                                        gbmax INTEGER
                                    )''')

            self.__cursor.execute('''CREATE TABLE IF NOT EXISTS grade_boundaries (
                                        id TEXT PRIMARY KEY,
                                        past_paper_id TEXT,
                                        grade TEXT,
                                        value INTEGER,
                                        percentage REAL
                                    )''')

            self.__cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
                                        id TEXT PRIMARY KEY,
                                        document_type TEXT,
                                        past_paper_id TEXT,
                                        filename TEXT,
                                        filepath TEXT,
                                        suffix TEXT
                                    )''')

            self.__connection.commit()
            self.__load_past_papers()
        except sqlite3.Error as e:
            raise custom_errors.ExceptionWarning(title="Database Error", message=str(e))

    def __load_past_papers(self):
        """
        Load past paper data from the database and instantiate PastPaper objects.
        """
        try:
            self.__cursor.execute("SELECT * FROM past_papers")
            rows = self.__cursor.fetchall()
            for row in rows:
                past_paper = PastPaper(self.__mainline, self, db_id=row[0])
                past_paper.set_custom_name(row[2])
                past_paper.set_year(row[3])
                past_paper.set_session(row[4])
                past_paper.set_timezone(row[5])
                past_paper.set_paper(row[6])
                past_paper.set_subject(row[7])
                past_paper.set_level(row[8])
                past_paper.set_completed_date(row[9])
                past_paper.set_mark(row[10])
                past_paper.set_maximum(row[11])
                past_paper.set_percentage()
                past_paper.set_notes(row[13])
                past_paper.set_gbmax(row[14])
                self.__past_papers[past_paper.get_id()] = past_paper

                past_paper_id = past_paper.get_id()

                #  Load grade boundaries for the past paper
                self.__cursor.execute("SELECT * FROM grade_boundaries WHERE past_paper_id=?", (past_paper_id,))
                grade_boundary_rows = self.__cursor.fetchall()
                for row in grade_boundary_rows:
                    past_paper.set_grade_boundary(row[3], row[2])

                # Load documents for the past paper
                self.__cursor.execute("SELECT * FROM documents WHERE past_paper_id=?", (past_paper_id,))
                document_rows = self.__cursor.fetchall()
                for row in document_rows:
                    past_paper.add_document_item(row[0],row[3], row[4],row[1],row[5])
                
                
                past_paper.update_to_database(copy_documents=False)
            
            
        
        except sqlite3.Error as e:
            raise custom_errors.ExceptionWarning(title="Database Error", message=str(e))


    def get_db_path(self):
        return self.__db_path

    def get_connection(self):
        """
        Get the SQLite connection object.

        OUT:
        - SQLite connection object.
        """
        return self.__connection

    def get_pandas_database_obj(self):
        return self.__db

    def get_past_papers(self):
        return self.__past_papers

    def get_pandas_database_obj(self):
        return self.__db

    def get_past_papers(self):
        return self.__past_papers

    def get_base_directory(self):
        return self.db_directory

    def add_past_paper(self, past_paper):
        """
        Add a PastPaper object to the database.

        IN:
        - past_paper (PastPaper): The PastPaper object to add to the database.
        """
        
        self.__past_papers[past_paper.get_id()] = past_paper
        self.__cursor.execute('''INSERT INTO past_papers (id, name, custom_name, year, session, timezone, paper, subject, level, completed_date, mark, maximum, percentage, notes, gbmax)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (past_paper.get_id(),
                                                                                        past_paper.get_name(),
                                                                                        past_paper.get_custom_name(),
                                                                                        past_paper.get_year(),
                                                                                        past_paper.get_session(),
                                                                                        past_paper.get_timezone(),
                                                                                        past_paper.get_paper(),
                                                                                        past_paper.get_subject(),
                                                                                        past_paper.get_level(),
                                                                                        past_paper.get_completed_date(),
                                                                                        past_paper.get_mark(),
                                                                                        past_paper.get_maximum(),
                                                                                        past_paper.get_percentage(),
                                                                                        past_paper.get_notes(),
                                                                                        past_paper.get_gbmax()))
        self.__connection.commit()

        for grade_boundary_code, grade_boundary_value in past_paper.get_grade_boundaries().items():
            self.__cursor.execute('''INSERT INTO grade_boundaries (id, past_paper_id, grade, value, percentage)
                                     VALUES (?, ?, ?, ?, ?)''', (str(uuid.uuid4()), past_paper.get_id(), grade_boundary_code, grade_boundary_value, past_paper.get_grade_boundary_percentage(grade_boundary_code)))

        documents = {}
        documents.update(past_paper.get_questionpaper_documents())
        documents.update(past_paper.get_markscheme_documents())
        documents.update(past_paper.get_attachment_documents())

        for document in documents.values():
            self.__cursor.execute('''INSERT INTO documents (id, past_paper_id, filename, filepath)
                                     VALUES (?, ?, ?, ?)''', (document.get_id(), past_paper.get_id(), document.get_filename(), document.get_filedirectory()))

        self.__connection.commit()

    def remove_past_paper_from_primary(self, past_paper_id):
        if past_paper_id in self.__past_papers:
            self.__past_papers.pop(past_paper_id)



    def close_database(self):
        """
        Close the database connection.
        """
        if self.__connection:
            self.__connection.close()


    def create_new_row(self, temporary=False):
        """
        Create a new PastPaper object and optionally add it to the database.

        Parameters:
            temporary (bool, optional): If True, the new PastPaper object will not be added to the database.
                Defaults to False.

        Returns:
            PastPaper: A new PastPaper object.

        Description:
            This method creates a new PastPaper object. By default, the new object is added to the database,
            but you can set the 'temporary' parameter to True if you want to create a temporary PastPaper
            object without adding it to the database (could be used, for example, during bulk import).
        """
        new_past_paper = PastPaper(self.__mainline, self)

        if not temporary:
            self.add_past_paper(new_past_paper)
        return new_past_paper

    
    def get_filtered_paper_items(self, name_filter="", year_filter="", session_filter="", timezone_filter="", paper_filter="", subject_filter="", level_filter=""):
        """
        Get a list of PastPaper objects filtered by the provided attributes.

        IN:
        - name_filter (str): Filter by name attribute.
        - year_filter (str): Filter by year attribute (range allowed, e.g., "2018-2022").
        - session_filter (str): Filter by session attribute.
        - timezone_filter (str): Filter by timezone attribute.
        - paper_filter (str): Filter by paper attribute.
        - subject_filter (str): Filter by subject attribute.
        - level_filter (str): Filter by level attribute.

        OUT:
        - A list of PastPaper objects that match the filters.
        """

        def extract_multiple_values(filter_string):
            return [value.strip() for value in filter_string.split(",")]

        filtered_papers = []
        for past_paper in self.__past_papers.values():
            if (
                (not name_filter or any(name_filter.casefold() in value.casefold() for value in extract_multiple_values(name_filter)))
                and (not session_filter or any(session_filter.casefold() in value.casefold() for value in extract_multiple_values(session_filter)))
                and (not timezone_filter or any(timezone_filter.casefold() in value.casefold() for value in extract_multiple_values(timezone_filter)))
                and (not paper_filter or any(paper_filter.casefold() in value.casefold() for value in extract_multiple_values(paper_filter)))
                and (not subject_filter or any(subject_filter.casefold() in value.casefold() for value in extract_multiple_values(subject_filter)))
                and (not level_filter or any(level_filter.casefold() in value.casefold() for value in extract_multiple_values(level_filter)))
            ):
                # Handle the year filter separately
                if year_filter:
                    year_filter = year_filter.strip()  # Remove any leading/trailing whitespaces
                    years = year_filter.split("-")
                    if len(years) == 1:
                        # Single year filter
                        if years[0].isdigit() and str(years[0]) in str(past_paper.get_year()):
                            filtered_papers.append(past_paper)
                    elif len(years) == 2:
                        # Range of years filter
                        start_year = int(years[0]) if years[0].isdigit() else None
                        end_year = int(years[1]) if years[1].isdigit() else None
                        paper_year = past_paper.get_year()
                        if start_year is not None and end_year is not None and start_year <= paper_year <= end_year:
                            filtered_papers.append(past_paper)

                else:
                    filtered_papers.append(past_paper)

        return filtered_papers



class DocumentItem:
    def __init__(self, past_paper, document_type, filename, filepath,suffix=""):
        """
        A DocumentItem represents a document (question paper, mark scheme, or attachment) attached to a PastPaper.

        IN:
        - past_paper (PastPaper): The parent PastPaper object that this DocumentItem is attached to.
        - document_type (str): The type of document ("questionpaper", "markscheme", or "attachment").
        - filename (str): The name of the file.
        - filepath (str): The file path of the document.
        """
        self.__id = str(uuid.uuid4())  # Unique ID for the DocumentItem instance
        self.__past_paper = past_paper
        self.__db_obj=past_paper.get_db_obj()
        self.__document_type = document_type
        self.__filename = filename

        self.__base_directory = self.__db_obj.get_base_directory()

        self.__filedirectory = filepath
        self.__absolute_filedirectory = os.path.join(self.__base_directory,filepath)
        self.__custom_suffix = suffix
        self.__custom_id = ""

        #self.set_filename()

    def get_id(self):
        return self.__id

    def get_past_paper(self):
        return self.__past_paper

    def get_document_type(self):
        return self.__document_type

    def get_filename(self):
        return self.__filename

    def get_filedirectory(self):
        return self.__filedirectory

    def get_absolute_filedirectory(self):
        return self.__absolute_filedirectory

    #def get_full_filepath(self):
    #    return os.path.join(self.__filedirectory,self.__filename)

    def get_suffix(self):
        return self.__custom_suffix

    def open_document(self):
        """
        Open the document in the default application for its file type.
        """
        if os.path.exists(self.__absolute_filedirectory):
            try:
                document_path = os.path.join(self.__absolute_filedirectory, self.__filename)
                if sys.platform.startswith("win32"):
                    # For Windows
                    subprocess.run(["start", "", document_path], shell=True)
                elif sys.platform.startswith("darwin"):
                    # For macOS
                    subprocess.run(["open", document_path])
                elif sys.platform.startswith("linux"):
                    # For Linux
                    subprocess.run(["xdg-open", document_path])
                else:
                    print("Platform not supported.")
            except Exception as e:
                print(f"Error opening the document: {e}")
        else:
            print("Document file does not exist.")
    
  

    def remove_document(self,keep_file=False):
        """
        Remove the document from the PastPaper object, the associated database entry, and delete the file.
        """
        try:

            if not keep_file:
                # Remove the file from the disk
                file_path = os.path.join(self.__absolute_filedirectory,self.__filename)
                if os.path.exists(file_path):
                    os.remove(file_path)

            try:
                # Remove the document from the database
                db = self.__db_obj.get_connection()
                db.execute("DELETE FROM documents WHERE id=?", (self.__id,))
                db.commit()
            except sqlite3.Error as e:
                raise custom_errors.ExceptionWarning(title="Database Error", message=str(e))

            # Also remove the document from the PastPaper object's document dictionary
            document_type = self.get_document_type()
            past_paper = self.get_past_paper()
            past_paper.remove_document_from_documents_dict(self.__id, document_type)

        except sqlite3.Error as e:
            raise custom_errors.ExceptionWarning(title="Database Error", message=str(e))
        except Exception as ex:
            raise custom_errors.ExceptionWarning(title="Error", message=str(ex))

    def set_filename(self,copy=True):
        """
        Generate the filename based on the attributes of the PastPaper, custom suffix, and custom ID.

        IN:
        - past_paper (PastPaper): The parent PastPaper object that this DocumentItem is attached to.
        - custom_suffix (str): A custom suffix to add to the filename (optional).
        """
        filename_parts = [self.__document_type]

        filename_extension = self.__filename.split(".")[-1]

        if self.__past_paper.get_name():
            filename_parts.append(self.__past_paper.get_name())

        if self.__custom_suffix:
            filename_parts.append(self.__custom_suffix)

        relative_target_directory = self.__filedirectory
        base_filename = "-".join(filename_parts)

        change_directory=False
        relative_target_directory = self.__past_paper.generate_documents_directory(relative=True)
        absolute_target_directory = self.__past_paper.generate_documents_directory(relative=False)
        if relative_target_directory != self.__filedirectory:
            change_directory=True

        change_filename=True
        new_filename = f"{base_filename}.{filename_extension}"
        if new_filename == self.__filename:
            change_filename=False
        else:
            # Append a custom ID to the filename if it already exists in the target directory
            counter = 1
            while os.path.exists(os.path.join(absolute_target_directory,new_filename)):
                new_filename = f"{base_filename} ({counter}).{filename_extension}"
                # Check if the new filename is the same as the old filename
                if new_filename == self.__filename:
                    change_filename=False
                counter += 1

        # Change the filename and/or directory if necessary
        if change_filename or change_directory: 
            print("ABS",absolute_target_directory)
            old_filepath = os.path.join(self.__absolute_filedirectory,self.__filename)
            new_filepath = os.path.join(absolute_target_directory,new_filename)

            print(old_filepath,new_filename)

            if copy:
                shutil.copy(old_filepath, new_filepath)  
            else:
                shutil.move(old_filepath, new_filepath)  
            self.__filename = new_filename
            self.__filedirectory = relative_target_directory
            self.__absolute_filedirectory=absolute_target_directory

    def set_custom_suffix(self, custom_suffix):
        """
        Set the custom suffix for the filename.

        IN:
        - custom_suffix (str): A custom suffix to add to the filename.
        """
        self.__custom_suffix = custom_suffix

    def set_custom_id(self, custom_id):
        """
        Set the custom ID to append to the filename.

        IN:
        - custom_id (str): A custom ID to append to the filename.
        """
        self.__custom_id = custom_id

    def validitycheck_file_path(self):
        if os.path.exists(os.path.join(self.__absolute_filedirectory,self.__filename)):
            return True
        else:
            return False

class QuestionPaper(DocumentItem):
    def __init__(self, past_paper, filename, filepath,suffix=""):
        super().__init__(past_paper, "questionpaper", filename, filepath,suffix=suffix)

class MarkScheme(DocumentItem):
    def __init__(self, past_paper, filename, filepath,suffix=""):
        super().__init__(past_paper, "markscheme", filename, filepath,suffix=suffix)

class Attachment(DocumentItem):
    def __init__(self, past_paper, filename, filepath,suffix=""):
        super().__init__(past_paper, "attachment", filename, filepath,suffix=suffix)

class PastPaper:

    def __init__(self, mainline, db_obj, db_id=None):
        """
        A PastPaper contains all attributes and methods pertaining to a single past paper
        (including year, session, subject, etc.).

        IN:
        - mainline: the mainline object 
        - db_obj: the database object
        - db_id (str, optional): The unique ID of the PastPaper instance. If None, a new ID will be generated.
        """
        self.__db_obj = db_obj
        self.__db = self.__db_obj.get_connection()
        self.__mainline = mainline
        self.__course_type = self.__mainline.settings.get_course_type()
        self.__course_values = mainline.get_course_values()

        # create unique ID for PastPaper instance (can be overridden later if read from the database)
        self.__db_id = db_id if db_id else str(uuid.uuid4())

        self.__db_row = None
        self.__normal_format = True
        self.reset_once = False
        self.new_obj_flag = True

        # all PastPaper attributes - initialized empty
        self.__custom_name = ""
        self.__year = ""
        self.__session = ""
        self.__timezone = ""
        self.__paper = ""
        self.__subject = ""
        self.__level = ""
        self.__questionpaper_documents = {}
        self.__markscheme_documents = {}
        self.__attachment_documents = {}
        self.__completed_date = ""
        self.__completed_date_datetime = None
        self.__mark = 0.00
        self.__maximum = 0.00
        self.__percentage = -1
        self.__notes = ""

        # define a dictionary with key: grade boundary codes, value: grade boundary value
        self.__grade_boundaries = {}
        self.__grade_boundaries_percentages = {}

        # setup all grade boundaries for this object (default value 0 for everything)
        for grade_boundary in self.__mainline.get_course_values().grade_boundaries:
            self.__grade_boundaries[grade_boundary] = 0
            self.__grade_boundaries_percentages[grade_boundary] = 0
        self.__gbmax = 0
        self.__grade = -1

        self.__name = ""
    
    def get_db_obj(self):
        return self.__db_obj
    
    # SETTERS (note: includes validation)

    def set_id(self, db_id):
        self.__db_id = db_id

    def set_normal_format(self, normal_format):
        self.__normal_format = normal_format

    def set_custom_name(self, custom_name, override=False):
        self.__custom_name = str(custom_name)
        return True, "", ""

    def set_year(self, year, override=False):
        """
        Validation requirement: int
        """
        if year.isdigit() or year == "":
            self.__year = self.int_validation(year)
        else:
            if override:
                self.__year = ""
            return False, "Must be a whole number", "Year"
        return True, "", ""

    def set_session(self, session, override=False):
        self.__session = str(session)
        return True, "", ""

    def set_timezone(self, timezone, override=False):
        self.__timezone = str(timezone)
        return True, "", ""

    def set_paper(self, paper, override=False):
        self.__paper = str(paper)
        return True, "", ""

    def set_subject(self, subject, override=False):
        self.__subject = str(subject)
        return True, "", ""

    def set_level(self, level, override=False):
        self.__level = str(level)
        return True, "", ""

    def set_mark(self, mark, override=False):
        """
        Validation requirement: float
        """
        if CommonFunctions.is_float(mark):
            self.__mark = self.float_validation(mark)
        else:
            if override:
                self.__mark = 0.00
            return False, "Must be a number", "Mark"
        return True, "", ""

    def set_maximum(self, maximum, override=False):
        """
        Validation requirement: float
        """
        if CommonFunctions.is_float(maximum):
            self.__maximum = self.float_validation(maximum)
        else:
            if override:
                self.__maximum = 0.00
            return False, "Must be a number", "Maximum"
        return True, "", ""

    def set_gbmax(self, gbmax, override=False):
        """
        Validation requirement: float AND > 0
        """
        if CommonFunctions.is_int(gbmax):
            self.__gbmax = self.int_validation(gbmax)

            if self.__gbmax > 0 and self.__gbmax != "":
                for grade_boundary in self.__grade_boundaries:
                    self.__grade_boundaries_percentages[grade_boundary] = round(float(self.__grade_boundaries[grade_boundary] / self.__gbmax), 2)
            else:
                for grade_boundary in self.__grade_boundaries:
                    self.__grade_boundaries_percentages[grade_boundary] = 0

        else:
            if override:
                self.__gbmax = 0
                for grade_boundary in self.__grade_boundaries:
                    self.__grade_boundaries_percentages[grade_boundary] = 0
            return False, "Must be a whole number", "Grade boundary maximum"

        return True, "", ""

    def set_notes(self, notes, override=False):
        self.__notes = str(notes)
        return True, "", ""

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
            self.__completed_date = completed_date
            # if the passed attribute is not datetime.date then convert it and set self.__completed_date_datetime to the datetime object
            if isinstance(completed_date, pd.Timestamp):
                self.__completed_date_datetime = completed_date.to_pydatetime()
                if pd.isnull(self.__completed_date_datetime):
                    self.__completed_date_datetime = None
            elif isinstance(completed_date, str):
                self.__completed_date_datetime = dateparser.parse(completed_date, settings={'PREFER_DAY_OF_MONTH': 'first'})
            elif isinstance(completed_date, datetime.date):
                self.__completed_date_datetime = completed_date
        else:
            self.__completed_date = None
            self.__completed_date_datetime = None
        return True, "", ""

    def set_grade_boundary(self, grade_boundary_value, grade_boundary_code, override=False):
        """
        Add a new grade boundary to the PastPaper object. Inserted values are validated as floats

        IN:
        - grade_boundary_value (float): the minimum mark needed to achieve a particular grade boundary
        - grade_boundary_code (str): the grade boundary being modified (e.g. 7,6,5 for IB or A*,A,B for A-Levels). If an invalid code is given, the grade boundary will not be added
        """
        if str(grade_boundary_code) in self.__grade_boundaries:
            if CommonFunctions.is_int(grade_boundary_value):
                self.__grade_boundaries[grade_boundary_code] = int(grade_boundary_value)
                self.__grade_boundaries_percentages[grade_boundary_code]

                if int(grade_boundary_value) >= 0:
                    if self.get_gbmax() != "" and self.get_gbmax() != 0:
                        self.__grade_boundaries_percentages[grade_boundary_code] = int(grade_boundary_value) / int(self.get_gbmax())
                else:
                    if override:
                        self.__grade_boundaries[grade_boundary_code] = 0
                        self.__grade_boundaries_percentages[grade_boundary_code] = 0
                    return False, "Must be greater or equal to 0", f"{self.__course_values.grade} {grade_boundary_code}"
            else:
                if override:
                    self.__grade_boundaries[grade_boundary_code] = 0
                    self.__grade_boundaries_percentages[grade_boundary_code] = 0
                return False, "Must be a whole number", f"{self.__course_values.grade} {grade_boundary_code}"
        return True, "", ""

    def pass_setter(self, e):
        pass

    def set_percentage(self):
        """
        Calculate and set the percentage based on the mark and maximum attributes.
        If the maximum is zero, set the percentage to -1.
        """
        if self.__maximum != 0:
            self.__percentage = self.__mark / self.__maximum
        else:
            self.__percentage = -1

    # GETTERS
    def get_questionpaper_documents(self):
        return self.__questionpaper_documents

    def get_markscheme_documents(self):
        return self.__markscheme_documents

    def get_attachment_documents(self):
        return self.__attachment_documents

    def get_grade_boundary(self, grade_boundary_code):
        return self.__grade_boundaries[grade_boundary_code]

    def get_grade_boundary_percentage(self, grade_boundary_code):
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

    def get_grade_boundaries(self):
        """
        Get the grade boundaries for the PastPaper object.

        OUT:
        - A dictionary with grade boundary codes as keys and grade boundary values as values.
        """
        return self.__grade_boundaries

    def get_year(self, pretty=False):
        """
        Return the year attribute

        IN:
        - pretty (Bool): if pretty==True a check will be completed to return the year with 4 digits (e.g. 19 -> 2019)
        """

        if pretty:
            if len(str(self.__year)) == 2:
                return "20" + str(self.__year)
            else:
                return str(self.__year)
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
        if self.__completed_date_datetime is not None:
            return CommonFunctions.format_date(self.__completed_date_datetime)
        else:
            return ""

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

    def get_percentage(self, pretty=False):
        return round(self.__percentage, 2)

    def get_percentage_pretty(self):
        if self.__percentage != -1 and self.__maximum != 0:
            rounded_percentage = round(self.__percentage * 100, 2)
            return str(rounded_percentage) + "%"
        else:
            return ""

    def get_grade_pretty(self):
        if str(self.__grade) != "-1" and self.__maximum != 0:
            return self.__grade
        else:
            return ""

    def get_mark(self):
        return self.__mark

    def get_maximum(self):
        return self.__maximum


    def remove_past_paper(self):
        self.__db_obj.remove_past_paper_from_primary(self.__db_id)
        self.__remove_object_from_secondary()

    def __remove_object_from_secondary(self):
        """
        Delete the paper object (also delete all attached documents).
        """
        try:
            # Remove all document attributes of the PastPaper
            for questionpaper in list(self.__questionpaper_documents.keys()):
                self.__questionpaper_documents[questionpaper].remove_document()
            for markscheme in list(self.__markscheme_documents.keys()):
                self.__markscheme_documents[markscheme].remove_document()
            for attachment in list(self.__attachment_documents.keys()):
                self.__attachment_documents[attachment].remove_document()

            # Remove the past paper object from the database
            db = self.__db_obj.get_connection()
            db.execute("DELETE FROM past_papers WHERE id=?", (self.__db_id,))
            db.commit()

            # Remove the grade boundaries for this past paper from the database
            db.execute("DELETE FROM grade_boundaries WHERE past_paper_id=?", (self.__db_id,))
            db.commit()

            db.execute("DELETE FROM documents WHERE past_paper_id=?", (self.__db_id,))
            db.commit()


        except sqlite3.Error as e:
            raise custom_errors.ExceptionWarning(title="Database Error", message=str(e))
        except Exception as ex:
            raise custom_errors.ExceptionWarning(title="Error", message=str(ex))
    def int_validation(self, x):
        """
        Attempt to cast a variable to a integer. If this cannot be done (e.g. due to a non-numeric string being provided), the function will
        return the variable as a string.
        """
        try:
            return int(x)
        except:
            return str(x)

    def float_validation(self, x):
        """
        Attempt to cast a variable to a float. If this cannot be done (e.g. due to a non-numeric string being provided), the function will
        return the variable as a string.
        """
        try:
            return float(x)
        except:
            return str(x)

    def serialize_documents(self, documents):
        """
        Serialize the DocumentItem objects into a list of dictionaries.

        IN:
        - documents (dict): A dictionary containing DocumentItem objects.

        OUT:
        - serialized_documents (list): A list of dictionaries containing serialized DocumentItem objects.
        """
        serialized_documents = [document.to_dict() for document in documents.values()]
        return serialized_documents

    def deserialize_documents(self, serialized_documents):
        """
        Deserialize the DocumentItem objects from a list of dictionaries.

        IN:
        - serialized_documents (list): A list of dictionaries containing serialized DocumentItem objects.

        OUT:
        - documents (dict): A dictionary containing deserialized DocumentItem objects.
        """
        documents = {document_data["filename"]: DocumentItem.from_dict(document_data) for document_data in serialized_documents}
        return documents

    def generate_grade(self):
        """
        Generate the grade based on the grade boundaries, mark, and maximum mark.

        This function calculates the grade of the PastPaper object based on the provided grade boundaries,
        the mark obtained, and the maximum mark possible. It compares the percentage of the mark obtained
        to the grade boundary percentages and assigns the corresponding grade based on the highest matching
        grade boundary.

        If the grade boundary for a certain grade is not specified, the function will set the grade to -1,
        indicating that the grade could not be determined due to missing grade boundaries.

        EXAMPLES:
        - For a PastPaper object with a mark of 81/100 and a grade boundary of 7 as 81/100 or above, the
        function will assign a grade of 7.
        - For a PastPaper object with a mark of 68/100 and a grade boundary of 5 as 60/100 to 74/100, the
        function will assign a grade of 5.
        - If the grade boundaries are not provided (grade boundary maximum not set), the function will set
        the grade to -1 as an edge case.

        """
        if self.get_gbmax() != "" or self.get_gbmax() == 0:
            for grade_boundary in self.__grade_boundaries:
                grade_boundary_value_percentage = self.__grade_boundaries_percentages[grade_boundary]
                if self.__percentage >= grade_boundary_value_percentage:
                    self.__grade = grade_boundary
                    break  # Break out of the loop since the grade is determined
            else:
                # If the loop completes without finding a matching grade boundary, set grade to -1
                self.__grade = -1  # Edge case where grade boundary is missing

        else:
            # If grade boundary maximum is not provided, set grade to 0
            self.set_gbmax(0)

    def generate_name(self):
        """
        Generate the name of the PastPaper based on its attributes.
        Format: year-session-timezone-subject-level-paper
        """
        name_parts = []

        if self.__year:
            name_parts.append(str(self.__year))

        if self.__session:
            name_parts.append(self.__session)

        if self.__timezone:
            name_parts.append(self.__timezone)

        if self.__subject:
            name_parts.append(self.__subject)

        if self.__level:
            name_parts.append(self.__level)

        if self.__paper:
            name_parts.append(self.__paper)

        self.__name = "-".join(name_parts)

        return self.__name

    def get_key_from_value(self,dict,value):
        for key in dict:
            if dict[key].casefold()==value.casefold():
                return key
        return value



    def generate_documents_directory(self,relative=True):
        """
        Generate the path for the directory in which document attachments to this paper object are stored.
        """
        session = self.get_key_from_value(self.__course_values.dict_session, self.__session)
        timezone = self.get_key_from_value(self.__course_values.dict_timezone, self.__timezone)
        level = self.get_key_from_value(self.__course_values.dict_level, self.__level)

        relative_path = "ExamDocumentManager"
        relative_path += "/" + self.__mainline.get_course_values().course_name
        if self.__subject != "":
            relative_path += "/" + self.__subject
        if level != "":
            relative_path += "/" + level
        if self.get_year(pretty=True) != "":
            relative_path += "/" + self.get_year(pretty=True)
        if session != "":
            relative_path += "/" + session
        if timezone != "":
            relative_path += "/" + timezone

        # Combine the relative_path with the configuration path to get the full directory path
        full_path = os.path.join(self.__mainline.settings.get_Configuration_path(), relative_path)

        # Create the directory if it doesn't exist
        if not os.path.exists(full_path):
            os.makedirs(full_path)


        if not relative:
            return full_path
        else:
            return relative_path

    def update_values(self):
        """
        Update the PastPaper object attributes based on the values in the database.
        """

        self.generate_name()
        self.set_percentage()
        self.generate_grade()


    def update_to_database(self, copy_documents=True):
        """
        Update the PastPaper object attributes to the database.
        """

        self.update_values()

        # Call set_filename for all question papers, mark schemes, and attachments
        for document_type in "questionpaper", "markscheme", "attachment":
            documents = self.get_documents_by_type(document_type)
            for document in documents:
                documents[document].set_filename(copy=copy_documents)

        try:
            db = self.__db_obj.get_connection()

            # Update the corresponding row in the database
            db.execute(
                """UPDATE past_papers SET 
                name = ?,
                custom_name = ?,
                year = ?,
                session = ?,
                timezone = ?,
                paper = ?,
                subject = ?,
                level = ?,
                completed_date = ?,
                mark = ?,
                maximum = ?,
                percentage = ?,
                notes = ?,
                gbmax = ?
                WHERE id = ?""",
                (
                    self.__name,
                    self.__custom_name,
                    self.__year,
                    self.__session,
                    self.__timezone,
                    self.__paper,
                    self.__subject,
                    self.__level,
                    self.__completed_date,
                    self.__mark,
                    self.__maximum,
                    self.__percentage,
                    self.__notes,
                    self.__gbmax,
                    self.__db_id,
                ),
            )

            # Update grade boundaries to the database
            db.execute("DELETE FROM grade_boundaries WHERE past_paper_id=?", (self.__db_id,))
            for grade_boundary_code, grade_boundary_value in self.__grade_boundaries.items():
                db.execute(
                    """INSERT INTO grade_boundaries (id, past_paper_id, grade, value, percentage)
                                     VALUES (?, ?, ?, ?, ?)""",
                    (
                        str(uuid.uuid4()),
                        self.__db_id,
                        grade_boundary_code,
                        grade_boundary_value,
                        self.__grade_boundaries_percentages[grade_boundary_code],
                    ),
                )

            # Update documents to the database
            db.execute("DELETE FROM documents WHERE past_paper_id=?", (self.__db_id,))
            
            documents={}
            # Add all documents to the documents dictionary
            documents.update(self.get_questionpaper_documents())
            documents.update(self.get_markscheme_documents())
            documents.update(self.get_attachment_documents())

            for document in documents.values():
                db.execute(
                    """INSERT INTO documents (id, document_type, past_paper_id, filename, filepath, suffix)
                                     VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        document.get_id(),
                        document.get_document_type(),
                        self.__db_id,
                        document.get_filename(),
                        document.get_filedirectory(),
                        document.get_suffix(),
                    ),
                )

            db.commit()

        except sqlite3.Error as e:
            raise custom_errors.ExceptionWarning(title="Database Error", message=str(e))



    def open_documents_directory(self):
        """
        Open the documents directory in the default file manager for the platform.
        """
        directory_path = self.generate_documents_directory(relative=False)

        if not os.path.exists(directory_path):
            try:
                os.makedirs(directory_path, exist_ok=True)  # Create the directory if it does not exist
            except Exception as e:
                print(f"Error creating the documents directory: {e}")

        if os.path.exists(directory_path):
            try:
                if sys.platform.startswith("win32"):
                    # For Windows
                    subprocess.run(["start", "", directory_path], shell=True)
                elif sys.platform.startswith("darwin"):
                    # For macOS
                    subprocess.run(["open", directory_path])
                elif sys.platform.startswith("linux"):
                    # For Linux
                    subprocess.run(["xdg-open", directory_path])
                else:
                    print("Platform not supported.")
            except Exception as e:
                print(f"Error opening the documents directory: {e}")
        else:
            print("Documents directory does not exist.")

    def get_documents_by_type(self, document_type):
        """
        Get a list of DocumentItem objects of a specific document type attached to this PastPaper.

        IN:
        - document_type (str): The type of document ("questionpaper", "markscheme", or "attachment").

        OUT:
        - A list of DocumentItem objects of the specified document type.
        """
        if document_type == "questionpaper":
            return self.__questionpaper_documents
        elif document_type == "markscheme":
            return self.__markscheme_documents
        elif document_type == "attachment":
            return self.__attachment_documents
        else:
            raise ValueError(f"Invalid document_type: {document_type}. Required one of the following values: questionpaper, markscheme, attachment")

    def create_insert_new_document(self, doc_type, override_path="",suffix=""):
        """
        Create and insert a new document (question paper, mark scheme, or attachment) into the PastPaper.

        IN:
        - doc_type (str): The type of document to create. Can be "questionpaper", "markscheme", or "attachment".

        OUT:
        - The new DocumentItem object.
        """
        # Create a Tkinter file dialog to get the file path
        root = tk.Tk()
        root.withdraw()  # Hide the main window


        if not override_path:
            file_path = filedialog.askopenfilename()
        else:
            file_path = override_path
        
        if file_path:
            # Extract the file name from the file path
            file_name = os.path.basename(file_path)
            file_path = file_path.replace(file_name, "")

            # Create the appropriate DocumentItem object based on the doc_type
            if doc_type == "questionpaper":
                new_document = QuestionPaper(self, file_name, file_path,suffix=suffix)
            elif doc_type == "markscheme":
                new_document = MarkScheme(self, file_name, file_path,suffix=suffix)
            elif doc_type == "attachment":
                new_document = Attachment(self, file_name, file_path,suffix=suffix)
            else:
                raise ValueError("Invalid document type. Must be 'Question Paper', 'Mark Scheme', or 'Attachment'.")

            # Add the new DocumentItem object to the appropriate dictionary based on its type
            if doc_type == "questionpaper":
                self.__questionpaper_documents[new_document.get_id()] = new_document
            elif doc_type == "markscheme":
                self.__markscheme_documents[new_document.get_id()] = new_document
            elif doc_type == "attachment":
                self.__attachment_documents[new_document.get_id()] = new_document

            # Return the new DocumentItem object
            return new_document
        else:
            return None
        

    def add_document_item(self, document_id, filename, filepath, document_type,suffix):
        """
        Add a DocumentItem object to the PastPaper.

        IN:
        - document_id (str): The unique ID of the document item.
        - filename (str): The name of the file.
        - filepath (str): The file path of the document item.
        - document_type (str): The type of the document ("questionpaper", "markscheme", or "attachment").
        """


        if document_type == "questionpaper":
            document_item = QuestionPaper(self,filename, filepath,suffix=suffix)
            self.__questionpaper_documents[document_item.get_id()] = document_item
        elif document_type == "markscheme":
            document_item = MarkScheme(self,filename, filepath,suffix=suffix)
            self.__markscheme_documents[document_item.get_id()] = document_item
        else:
            document_item = Attachment(self,filename, filepath,suffix=suffix)
            self.__attachment_documents[document_item.get_id()] = document_item
        
    def remove_document_from_documents_dict(self, document_id, document_type):
        """
        Remove the document with the given ID from the appropriate document dictionary.

        IN:
        - document_id (str): The ID of the document to remove.
        - document_type (str): The type of the document ("questionpaper", "markscheme", or "attachment").
        """
        if document_type == "questionpaper":
            self.__questionpaper_documents.pop(document_id, None)
        elif document_type == "markscheme":
            self.__markscheme_documents.pop(document_id, None)
        elif document_type == "attachment":
            self.__attachment_documents.pop(document_id, None)
        else:
            raise ValueError("Invalid document type.")