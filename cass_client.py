from os import environ
from io import StringIO
import requests
import pandas as pd


class CassClient(object):

    def __init__(self,
                 cass_url=environ.get("CASS_URL",'http://api:8000'), 
                 auth_token=environ.get("JUPYTERHUB_API_TOKEN", "FAKE-TOKEN")):
        self._cass_url_ = cass_url
        self._auth_token_ = auth_token

    def get_courses(self):
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        response = requests.get(f"{self._cass_url_}/courses/", headers=headers)
        response.raise_for_status()
        return response.json()

    def add_course(self,
        course: str,
        term: str,
        git_url: str,
        lms_course_id: str = "",
        lms_type: str = "blackboard"
    ):
        data = {'course': course, 'term': term, 'git_url': git_url, 'lms_course_id': lms_course_id, 'lms_type': lms_type}
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        response = requests.post(f"{self._cass_url_}/courses/", headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_course(self, course_key):
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        response = requests.get(f"{self._cass_url_}/courses/{course_key}", headers=headers)
        response.raise_for_status()
        return response.json()

    def whoami(self):
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        response = requests.get(f"{self._cass_url_}/user/auth/", headers=headers)
        response.raise_for_status()
        return response.json()

    def add_course_assignments(self, course_key, csv_file_path):
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        with open(csv_file_path, "rb") as f:
            file = { 'file': ("assignments.csv", f, 'text/csv') }
            response = requests.post(f"{self._cass_url_}/courses/{course_key}/assignments", headers=headers, files=file)
            response.raise_for_status()
            return response.json()

    def add_course_roster(self, course_key, csv_file_path):
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        with open(csv_file_path, "rb") as f:
            file = { 'file': ("roster.csv", f, 'text/csv') }
            response = requests.post(f"{self._cass_url_}/courses/{course_key}/roster", headers=headers, files=file)
            response.raise_for_status()
            return response.json()

    def get_course_assignments(self, course_key) -> pd.DataFrame:
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        response = requests.get(f"{self._cass_url_}/courses/{course_key}/assignments", headers=headers)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))

    def get_course_assignment_names(self, course_key) -> list[str]:
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        response = requests.get(f"{self._cass_url_}/courses/{course_key}/assignments/list", headers=headers)
        response.raise_for_status()
        names = response.json()
        names_only = [ n.split("/")[-1] for n in names]
        return names_only

    def get_course_roster(self, course_key) -> pd.DataFrame:
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        response = requests.get(f"{self._cass_url_}/courses/{course_key}/roster", headers=headers)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))

    def get_user_course_info(self, course_key):
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        response = requests.get(f"{self._cass_url_}/courses/{course_key}/roster/myroles", headers=headers)
        response.raise_for_status()
        return response.json()

    def submission_info(self, course_key, assignment_name, student, filename):        
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        response = requests.get(f"{self._cass_url_}/courses/{course_key}/submission/{assignment_name}/submit/{student}/fileinfo/{filename}", headers=headers)
        response.raise_for_status()
        return response.json()

    def submit_assignment(self, course_key, assignment_file_path, assignment_name, student):
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        with open(assignment_file_path, "rb") as f:
            file = { 'file': f }
            response = requests.post(f"{self._cass_url_}/courses/{course_key}/submission/{assignment_name}/submit/{student}", headers=headers, files=file)
            response.raise_for_status()
            return response.json()

    def get_assignment_submission(self, course_key, assignment_name, student, filename):
        headers = {"X-JUPYTERHUB-API-TOKEN": self._auth_token_}
        response = requests.get(f"{self._cass_url_}/courses/{course_key}/submission/{assignment_name}/fetch/{student}/file/{filename}", headers=headers)
        response.raise_for_status()
        return response.json()

if __name__ == '__main__':
    client = CassClient()
    course = client.add_course("ist256","spring2024","https://github.com/ist256/spring2024.git")
    courses = client.get_courses()