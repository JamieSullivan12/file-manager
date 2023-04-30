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

    def commit_changes(self):
        self.config["Course"]["type"]=self.course_type
        # write to config file
        print("savechanges")
        with open('settings.ini','w') as FileObject:
            self.config.write(FileObject)


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



def config_open():
    config = configparser.ConfigParser()
    config.read('settings.ini')

    course_type = config_check_valid("Course","type",config)

    settings_obj = Settings(config)
    settings_obj.set_Course_values(course_type)

    settings_obj.commit_changes()
    return settings_obj
config_open()
