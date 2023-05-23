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


def get_regex_patterns(course):
    return course_import_regexpattens[course]

course_import_regexpattens = {
    "IB":{
        "year_regex":r"[12][0-9]{3}",
        "session_regex":r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b",
        "timezone_regex":r"TZ([0-9]+)",
        "paper_regex":r"Paper[_| ]?([0-9])",
        "subject_regex":r"(\w+)_paper_[0-9]",
        "level_regex":r"HLSL|SLHL|HL|SL",
        "other_regex":r"French|Spanish|German",
        "minimum_requirements":["Year","Paper"],
        "questionpaper_identifier":"",
        "markscheme_identifier":"Markscheme",
        "otherattachments_identifier":["case_study","case study"]
    }
}


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

        "list_year":[str(x) for x in list(range(1950,2100))],
        "dict_session":{"M":"May","N":"November","JU":"June","JL":"July","A":"August"},
        "dict_timezone":{"TZ0":"0","TZ1":"1","TZ2":"2"},
        "dict_paper":{"P1":"1","P2":"2","P3":"3","P4":"4"},
        "dict_level":{"SL":"Standard Level","HL":"Higher Level"}
        
    },
    "AL": {
        "Name":"Name",
        "Year":"Year",
        "Session":"Session",
        "Timezone":"Administrative zone",
        "Paper":"Paper",
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


class Colors:
    def __init__(self):

        self.navbar_button_text = ("gray10", "gray90")
        self.navbar_button_hover = ("gray70", "gray30")
        self.navbar_frame_fg = "gray70"

        self.bubble_background=("gray80","gray20")