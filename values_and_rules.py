IB_code = "IB"
IB_name = "International Baccalaureate"
IB_gradeboundaries = ["7","6","5","4","3","2","1"]

HSC_code = "HS"
HSC_name = "Higher School Certificate"
HSC_gradeboundaries = ["6","5","4","3","2","1"]

ALevel_code = "AL"
ALevel_name = "A-Levels"
ALevel_gradeboundaries = ["A*","A","B","C","D","E"]




def get_course_types():
    """
    Return a dictionary containing all courses:
        key = course code (two string)
        value = course name
    """
    course_types = {
        IB_code:IB_name,
        HSC_code:HSC_name,
        ALevel_code:ALevel_name
    }
    return course_types

def get_course_grade_boundaries():
    course_gradeboundaries = {
        IB_code:IB_gradeboundaries,
        HSC_code:HSC_gradeboundaries,
        ALevel_code:ALevel_gradeboundaries
    }
    return course_gradeboundaries

def write_course_type(value,config):
    if value in get_course_types():
        config["Course","type"]=value
    else: pass


# variables

course_variable_modifiers = {
    "IB": {
        "Name":"Name",
        "Year":"Year",
        "Session":"Session",
        "Timezone":"Timezone",
        "Paper":"Paper",
        "Subject":"Subject",
        "Level":"Level",
        "Grade boundaries":"Grade boundaries",
        "Original":"Question paper",
        "Markscheme":"Markscheme",
        "Grade":"Grade",
        "Grades":"Grades",
        "Notes":"Notes",

        "show_name":True,
        "show_year":True,
        "show_notes":True,
        "show_session":True,
        "show_timezone":True,
        "show_paper":True,
        "show_subject":True,
        "show_level":True,
        "show_grade_boundaries":True,

        "acr_timezone":"tz",
        "acr_original":"qp",
        "acr_markscheme":"ms",
        
    },
    "AL": {
        "Name":"Name",
        "Year":"Year",
        "Session":"Session",
        "Timezone":"Administrative zone",
        "Paper":"Paper 1",
        "Subject":"Subject",
        "Level":"",
        "Grade boundaries":"Grade thresholds",
        "Original":"Question paper",
        "Markscheme":"Markscheme",
        "Grade":"Grade",
        "Grades":"Grades",
        "Notes":"Notes",

        "show_name":True,
        "show_year":True,
        "show_notes":True,
        "show_session":True,
        "show_timezone":True,
        "show_paper":True,
        "show_subject":True,
        "show_level":False,
        "show_grade_boundaries":True,

        "acr_timezone":"az",
        "acr_original":"qp",
        "acr_markscheme":"ms"
    },
    "HS": {
        "Name":"Name",
        "Year":"Year",
        "Session":"",
        "Timezone":"",
        "Paper":"Paper",
        "Subject":"Subject",
        "Level":"",
        "Grade boundaries":"Bands",
        "Original":"Examination paper",
        "Markscheme":"Marking guidelines",
        "Grade":"Band",
        "Grades":"Bands",
        "Notes":"Notes",

        "show_name":True,
        "show_year":True,
        "show_notes":True,
        "show_session":False,
        "show_timezone":False,
        "show_paper":True,
        "show_subject":True,
        "show_level":False,
        "show_grade_boundaries":True,

        "acr_timezone":"",
        "acr_original":"ep",
        "acr_markscheme":"mg"
    }
}

def get_terminology(course):
    """Return all terminology for a specific course"""
    return course_variable_modifiers[course]
