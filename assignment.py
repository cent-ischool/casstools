import os
import json
import requests
from datetime import datetime
import pandas as pd
from ipylab import JupyterFrontEnd

from .cass_client import CassClient
from .path_parser import PathParser

WARN = "\U000026A0"
CAL = "\U0001F553"
POOP = "\U0001F4A9"
OK = "\U00002705"
BOMB = "\U0001F4A3"
PYTHON = "\U0001F40D"
RCPT = "\U0001F4C3"
QUESTION = "\U00002753"
CANCEL = "\U0000274C"
UP = "\U00002B06"
SAVE = "\U0001F4BE"
THUMBS_DOWN = "\U0001f44e"
THUMBS_UP = "\U0001f44d"
INFO = "\U00002139"
ARROW_RIGHT="\U000027a1"

DATETIME_PARSE_FORMAT = '%Y-%m-%d %H:%M'
DATETIME_DISPLAY_FORMAT = '%Y-%m-%d %H:%M'

SUBMISSION_LOG="/home/jovyan/library/.submission_log.json"


class Assignment(object):

    def __init__(self, 
                 cass_url=os.environ.get("CASS_URL", "http://api:8000"), 
                 auth_token=os.environ.get("JUPYTERHUB_API_TOKEN", "FAKE-TOKEN"), 
                 filespec=None):
        self.client = CassClient(cass_url=cass_url, auth_token=auth_token)
        self.parsed_path = PathParser(filespec)

    def _confirm_submission(self, late, resubmit):
        if not late:
            if not resubmit:
                prompt = "Submit?"
            else:
                prompt = "Submit Again?"
        else:
            if not resubmit:
                prompt = "Assignment is late. Submit?"
            else:
                prompt = "Assignment is late. Submit Again?"

        yn = input(f"{QUESTION} {prompt} [y/n] {QUESTION} ").lower()
        return len(yn) > 0 and yn[0] == "y"

    def read_submission_log(self) -> pd.DataFrame():
        return pd.read_json(SUBMISSION_LOG, lines=True, orient="values")

    def _append_to_submission_log(self,record_dict):
        with open(SUBMISSION_LOG, "a") as f:
            f.write(json.dumps(record_dict) + "\n")

    def _autosave(self):
        # autosave
        app = JupyterFrontEnd()
        app.commands.execute('docmanager:save')

    def submit(self, ui=False):
        dtnow = datetime.now()
        course_key = self.parsed_path.course_key_part
        assignment_file_path = self.parsed_path.fullpath
        assignment_name = self.parsed_path.filename_part

        ####################################
        # save the current notebook
        self._autosave()
        print(f"{OK} TIMESTAMP  : {dtnow.strftime(DATETIME_DISPLAY_FORMAT)}")

        # Course Check
        try:
            course = self.client.get_course(course_key)
            print(f"{OK} COURSE     : {course['course']}")
            print(f"{OK} TERM       : {course['term']}")
        except Exception as e:
            self._course_error(e)
            return 

        ####################################
        # Student Check
        try:
            me = self.client.whoami()
            user = self.client.get_user_course_info(course_key)
            student = user['name']
            print(f"{OK} USER       : {user['name']}")
            print(f"{OK} STUDENT    : {user['student']}")
        except Exception as e:
            self._user_error(e)
            return 

        ####################################
        #Assignment Check
        try:
            assignments_list = self.client.get_course_assignment_names(course_key)
            if self.parsed_path.path not in assignments_list:
                raise Exception(f"{self.parsed_path.filename_part} is not an assignment on the course assignment list.")

            assignments = self.client.get_course_assignments(course_key)
            assignment_points = assignments[ assignments.assignment_name.str.lower() == assignment_name.lower()]['points'].values[0]
            assignment_due_date_raw = assignments[ assignments.assignment_name.str.lower() == assignment_name.lower()]['due_date'].values[0]
            assignment_due_date = datetime.strptime(assignment_due_date_raw, DATETIME_PARSE_FORMAT)
            assignment_late = dtnow > assignment_due_date
            print(f"{OK} PATH       : {self.parsed_path.path}")
            print(f"{OK} ASSIGNMENT : {assignment_name}")
            print(f"{OK} POINTS     : {assignment_points}")
            print(f"{OK} DUE DATE   : {assignment_due_date.strftime(DATETIME_DISPLAY_FORMAT)}")
            print(f"{OK} LATE       : {assignment_late}")
        except Exception as e:
            self._assignment_error(e)
            return 

        ####################################
        # Check for re-submit / new submission
        try:
            results = self.client.submission_info(course_key, assignment_name, student, assignment_name)
            assignment_status =  "Re-Submission" if results['exists'] else "New Submission"            
            print(f"{OK} STATUS     : {assignment_status}")
            print()
        except Exception as e:
            self._file_check_error(e)
            return         

                
        confirm = self._confirm_submission(late = assignment_late, resubmit = results['exists'])
        if not confirm:
            print(f"{THUMBS_DOWN} Submission Cancelled")
            # save the current notebook
            self._autosave()            
            return 
        
        ####################################        
        # Actual Submission
        try:
            results = self.client.submit_assignment(course_key, assignment_file_path, assignment_name, student)
            print()
            print(f"{THUMBS_UP} SUBMITTED")
            print(f"{RCPT} RECIEPT   : {results['etag']}")
            
        except Exception as e:
            self._submission_error(e)
            return 

        data = { 
            "TIMESTAMP": dtnow.strftime(DATETIME_DISPLAY_FORMAT),
            "COURSE": course['course'],
            "TERM": course['term'],
            "USER": user['name'],
            "STUDENT": user['student'],
            "PATH": self.parsed_path.path,
            "ASSIGNMENT": assignment_name,
            "POINTS": str(assignment_points),
            "DUE DATE": assignment_due_date.strftime(DATETIME_DISPLAY_FORMAT),
            "LATE": assignment_late,
            "STATUS": assignment_status,
            "RECIEPT": str(results['etag'])
        }
        self._append_to_submission_log(data)
        # save the current notebook
        self._autosave()
        return 


    
    def _submission_error(self, e):
            print(f"{BOMB} ERROR IN ASSIGNMENT FILE SUBMISSION {BOMB}")
            print(f"{CANCEL} Error Details:", e)
            print("Possible Causes:")
            print(f" - Is the course: {self.parsed_path.course_part} a registered course?")
            print(f" - Is the term: {self.parsed_path.term_part} an term in that course?")
            print(f" - Is: {me['name']} a registered student in the course?")
            print(f" - Is: {self.parsed_path.filename_part} a registered assignment in the course?")        

    def _file_check_error(self, e):
            print(f"{BOMB} FILE CHECK ERROR {BOMB}")
            print(f"{CANCEL} Error Details:", e)
    
    def _course_error(self, e):
            print(f"{BOMB} ERROR GETTING COURSE INFORMATION {BOMB}")
            print(f"{CANCEL} Error Details:", e)
            print("Possible Causes:")
            print(f" - Is the course: '{self.parsed_path.course_part}' a registered course?")
            print(f" - Is the term: '{self.parsed_path.term_part}' an term in that course?")
        
    def _user_error(self, e):
            print(f"{BOMB} ERROR GETTING YOUR USER INFORMATION {BOMB}")
            print(f"{CANCEL} Error Details:", e)
            print("Possible Causes:")
            print(f" - Are you: '{me['name']}' on the class roster?")
            print(f" - Are you: '{me['name']}' listed as a student on class roster?")

    def _assignment_error(self, e):
            print(f"{BOMB} ERROR GETTING ASSIGNMENT INFORMATION {BOMB}")
            print(f"{CANCEL} Error Details:", e)
            print("Possible Causes:")
            print(f" - Is the assignment '{self.parsed_path.filename_part}'on the assignment list?")

