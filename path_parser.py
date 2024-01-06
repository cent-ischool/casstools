import ipynb_path


class PathParser(object):

    def __init__(self, path=None):
        if path is None:
            self.fullpath = ipynb_path.get()
        else:
            self.fullpath = path
            
        self.path = self.fullpath.replace("/home/jovyan/library/","")

    @property
    def filename_part(self):
        return self.path.split("/")[-1]

    @property
    def course_part(self):
        return self.path.split("/")[0]
    @property
    def term_part(self):
        return self.path.split("/")[1]

    @property
    def course_key_part(self):
        return f"{self.course_part}-{self.term_part}"
        
if __name__ == '__main__':
    demo = "/home/jovyan/library/ist256/spring2024/lessons/00-demo/A1.ipynb"
    p = PathParser(demo)
    assert p.path == demo.replace("/home/jovyan/library/","")
    assert p.filename_part == "A1.ipynb"
    assert p.course_part == "ist256"
    assert p.term_part == "spring2024"
    assert p.course_key_part == "ist256-spring2024"
    print(p.path)
    print(p.filename_part)
    print(p.course_part)
    print(p.term_part)
    print(p.course_key_part)