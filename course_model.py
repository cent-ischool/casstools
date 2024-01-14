from os import environ, path
import git


class Course(object):

    def __init__(self, course_dict: dict):
        self.course_dict = course_dict
        self.__home = environ.get("HOME", "/home/jovyan")

    @property
    def key(self):
        return self.course_dict.get("course_key", None)

    @property
    def name(self):
        return self.course_dict.get("course", None)

    @property
    def term(self):
        return self.course_dict.get("term", None)

    @property
    def git_url(self):
        return self.course_dict.get("git_url", None)

    @property
    def lms_type(self):
        return self.course_dict.get("lms_type", None)

    @property
    def lms_course_id(self):
        return self.course_dict.get("lms_course_id", None)

    @property
    def name_folder_path(self):
        if self.course_dict.get('course', None) is not None:
            return f"{self.__home}/library/{self.course_dict['course']}"
        else:
            return None

    @property
    def name_folder_exists(self):
        if self.course_dict.get('course', None) is not None:
            return path.exists(self.name_folder_path)
        else:
            return None

    @property
    def term_folder_path(self):
        if self.course_dict.get('term', None) is not None:
            return f"{self.name_folder_path}/{self.course_dict['term']}"
        else:
            return None

    @property
    def term_folder_exists(self):
        if self.course_dict.get('term', None) is not None:
            return path.exists(self.term_folder_path)
        else:
            return None

    @property
    def term_folder_is_git(self):
        if self.course_dict.get('term', None) is not None:
            return path.exists(f"{self.term_folder_path}/.git")
        else:
            return None

    @property
    def term_folder_git_origin(self):
        if self.term_folder_is_git:
            remote = git.cmd.Git(self.term_folder_path).remote(verbose=True).split()[1]
            return remote
        else:
            return None

    @property
    def term_folder_matches_course_git(self):
        if self.course_dict.get('git_url', None) is not None:
            return self.term_folder_git_origin  == self.course_dict['git_url']
        else:
            return None

if __name__ == '__main__':
    data = {
        'course': 'ist256',
         'term': 'spring2024',
         'git_url': 'https://github.com/ist256/spring2024.git',
         'lms_type': 'blackboard',
         'lms_course_id': '',
         'course_key': 'ist256-spring2024',
         'assignments': 'ist256-spring2024/assignments.csv',
         'roster': 'ist256-spring2024/roster.csv'
    }
    test = Course(data)
    assert test.name == data['course']
    assert test.key == data['course_key']
    assert test.name_folder_path == environ.get("HOME", "/home/jovyan") + "/library/" + data['course']
    assert test.name_folder_exists == True
    assert test.term_folder_path == environ.get("HOME", "/home/jovyan") + "/library/" + data['course'] +  "/"  + data['term']
    assert test.term_folder_exists == True
    assert test.term_folder_is_git == True
    assert test.term_folder_git_origin == data['git_url']
    assert test.term_folder_matches_course_git == True

