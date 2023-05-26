# import modules
import configparser

class Settings:
    def __init__(self,config):
        self.s=""
        self.config=config

    def set_Course_values(self,course_type):
        self.course_type = course_type

    def get_course_type(self):
        return self.course_type

    def set_Window_values(self,geometry,fullscreen):
        self.geometry=geometry
        self.fullscreen=fullscreen
        self.commit_changes()

    def get_Window_geometry(self):
        return self.geometry

    def get_Window_fullscreen(self):
        return self.fullscreen

    def commit_changes(self):
        self.config["Course"]["type"]=self.course_type
        self.config["Window"]["geometry"]=self.geometry
        self.config["Window"]["fullscreen"]=str(self.fullscreen)

        
        self.config.remove_section('Subjects')
        self.config.add_section('Subjects')
        for subject_code in self.subjects:
            
            self.config["Subjects"][subject_code]=self.subjects[subject_code]

        # write to config file
        with open('settings.ini','w') as FileObject:
            self.config.write(FileObject)

    def set_Subject_values(self,subjects):
        self.subjects=subjects



    def subject_name_exists(self,subject_name_test):
        if subject_name_test=="":return True
        for subject in self.subjects:
            if subject_name_test.casefold()==self.subjects[subject].casefold():
                return True
        else:
            return False

    def subject_code_exists(self,subject_code_test):
        for subject_code in self.subjects:
            if subject_code.casefold() == subject_code_test.casefold():
                return True
        return False

    def get_subjects(self):
        return self.subjects

    def generate_subject_code(self,subject_name,subject_code=None):
        
        if subject_code==None:
            subject_code=""

            subject_words = subject_name.split(" ")
            
            # METHOD 1: subject code is the initials from the first 2 OR 3 words of the subject
            if len(subject_words)>1:
                subject_code=subject_words[0][0]
                for word in subject_words[1:]:
                    if len(subject_code)==4:break
                    subject_code+=word[0]
                    if not self.subject_code_exists(subject_code):
                        return subject_code.upper()
                

            # METHOD 2: take 2 or 3 letters from the subject name (if only one word)
            else:
                subject_letters=subject_name
                subject_code=subject_letters[0]
                for letter in subject_letters[1:]:
                    if len(subject_code)==3:break
                    subject_code+=letter
                    if not self.subject_code_exists(subject_code):return subject_code.upper()

        if not self.subject_code_exists(subject_code):
            return subject_code.upper()

        # METHOD 3: from the previous two methods, continually add incrementing numbers onto the subject code
        #              until a unique one is found 
        number=1
        while True:
            if not self.subject_code_exists(subject_code+str(number)):
                return subject_code.upper()+str(number)
            else: number += 1



    def add_subject(self,new_subject,new_subject_code=None):
        if new_subject_code == None or new_subject_code=="":
            new_subject_code=None
            print('create subject code')
            subject_code=self.generate_subject_code(new_subject,new_subject_code)
            print(subject_code)
        else:
            subject_code=new_subject_code
        if self.subject_name_exists(new_subject):
            raise ValueError(f"Subject name {new_subject} already exists. Please enter a different name")
        if subject_code in self.subjects:
            raise ValueError(f"Subject code {subject_code} already exists. Please enter a different code (recommended {self.generate_subject_code(new_subject)})")

        self.subjects[subject_code]=new_subject
        self.commit_changes()
        return subject_code,new_subject

    def change_subject_name(self,subject_code,new_subject_name):
        self.subjects[subject_code]=new_subject_name
        self.commit_changes()
        return new_subject_name
    
    def change_subject_code(self,old_subject_code,new_subject_code,subject_name):
        if new_subject_code in self.subjects and old_subject_code!=new_subject_code:
            raise ValueError(f"Subject code {new_subject_code} already exists. Please enter a different code (recommended {self.generate_subject_code(subject_name)})")
        else:
            if old_subject_code!=new_subject_code:
                subject_name=self.subjects[old_subject_code]
                self.subjects[new_subject_code]=subject_name
                del self.subjects[old_subject_code]
            else:
                return new_subject_code
        
        self.commit_changes()
        return new_subject_code
    def remove_subject(self,subject_code):
        if subject_code in self.subjects:
            del self.subjects[subject_code]
        self.commit_changes()
    

    def get_subject_code(self,subject_name):
        for subject in self.subjects:
            if self.subjects[subject].casefold()==subject_name.casefold():
                return subject
        


def config_check_valid(section, key, config):
    """
    IN:
    - section: the section in the config file
    - key: the key of the value being retrieved
    - config: the confg object
    """
    
    if section not in config:
        config.add_section(section)
    
    if key in config[section]:
        # the value in the config file under Section -> Name
        return config[section][key]
    else: 
        config[section][key]="None"
        return "None"

def config_get_subjects(section,config):
    dict={}
    for item in config[section]:
        dict[item.upper()]=config[section][item]
    return dict

def config_open():
    config = configparser.ConfigParser()
    config.read('settings.ini')

    course_type = config_check_valid("Course","type",config)

    subjects_dict=config_get_subjects("Subjects",config)

    geometry = config_check_valid("Window","geometry",config)
    fullscreen = config_check_valid("Window","fullscreen",config)

    
    settings_obj = Settings(config)
    
    settings_obj.set_Course_values(course_type)
    settings_obj.set_Subject_values(subjects_dict)
    settings_obj.set_Window_values(geometry,fullscreen)

    settings_obj.commit_changes()

    return settings_obj