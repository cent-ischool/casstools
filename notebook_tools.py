import nbformat
from casstools.path_parser import PathParser
from casstools import code_tools as ct


OK = "\U00002705"
QUESTION = "\U00002753"
CANCEL = "\U0000274C"


class NotebookFile(object):

    def __init__(self, filespec = None):

        if filespec is None:
            filespec = PathParser().fullpath

        self.filespec = filespec
        self.contents = self.load_notebook(filespec)
        self.filetype = self.__get_file_type(filespec)

    def __get_file_type(self, filespec):
        file_type = filespec.split("/")[-1].split("-")[0].upper()
        return file_type

    def load_notebook(self, path: str):
        with open(path, "r") as f:
            return nbformat.read(f, as_version=4)

    def _extract_metadata_value(self, cell, key):
        '''
        Extracts metadata value from cell using key 
        first checks under ['metadata']['cass'][key]
        then under legaccy ['metadata'][key]
        '''
        md = cell['metadata']
        if md.get("cass", None) is not None:
            return md['cass'].get(key, None)
        else:
            return md.get(key, None)

    @property
    def code_cells(self):
        return [c for c in self.contents.cells if c.cell_type == "code"]

    @property
    def markdown_cells(self):
        return [c for c in self.contents.cells if c.cell_type == "markdown"]

    @property
    def raw_cells(self):
        return [c for c in self.contents.cells if c.cell_type == "raw"]


    def has_submission_cell(self):
        submission = "from casstools.assignment import Assignment\nAssignment().submit()"
        for c in self.code_cells:
            if c['source'].find(submission) >=0:
                return True
        return False
            

    def code_cells_of_type(self, cell_type, executed_only=False):
        '''
        return a list of code cells with the "cell_type" as their designation
        designation is found in:
        1) ['metadata']['cass']['code_cell_type'] or 
        2) ['metadata']['code_cell_type'] if the "cass" key does not exist.
        '''
        cells = [c for c in self.code_cells if self._extract_metadata_value(c, "code_cell_type") == cell_type]
        if executed_only:
            return [c for c in cells if c.execution_count is not None and c.execution_count >=1]
        else:
            return cells

    def markdown_cells_of_type(self, cell_type):
        cells = [c for c in self.markdown_cells if self._extract_metadata_value(c, "label") == cell_type]
        return cells 
        
    @property
    def exercise_code_cells(self):
        cells = [c for c in self.code_cells if self._extract_metadata_value(c, "code_cell_type") in ["debug_code", "write_code"]]
        return cells

    
    def __check(self, boolean_expression):
        if boolean_expression:
            return OK
        else:
            return CANCEL


    def validate_lab(self):
        '''
        validated the lab file has the necessary metadata cells for the self-check, and lab is ready to publish. This is an author's tool to make sure check_lab will work.
        '''
        check1 = self.__check(self.has_submission_cell)
        print(f"{check1} notebook: has submission cell")
        
        for rc_cell in self.code_cells_of_type("run_code"):

            print("CELL:", rc_cell)
            
            check1 = self.__check(len(rc_cell['source']) > 0)
            print(f"\t{check1} run_code cell: should have has code")
            
            check2 = self.__check(rc_cell['execution_count'] is None)
            print(f"\t{check2} run_code cell: should be no execution_count")                

        for ec_cell in self.exercise_code_cells:

            print("CELL", ec_cell)

            label = self._extract_metadata_value(ec_cell, "label")
            check1 = self.__check(label is not None)           
            print(f"\t{check1} exercise_code cell: has label {label}")

            code_cell_type = self._extract_metadata_value(ec_cell, "code_cell_type")
            check2 = self.__check(code_cell_type is not None)           
            print(f"\t{check2} exercise_code cell: has code_cell_type {code_cell_type}")

            if code_cell_type == "write_code":
                student_code = "\n".join([line for line in ec_cell.source.split("\n") if not line.strip().startswith("#")]).strip()
                check3 = self.__check(student_code == "")
                print(f"\t{check3} exercise_code cell: code_cell_type='write_code' cell should be empty {student_code}")

            solution_code = "".join(self._extract_metadata_value(ec_cell, "solution"))
            check4 = self.__check(solution_code is not None)
            print(f"\t{check4} exercise_code cell: should have solution_code metadata")

        comfort_cells = self.markdown_cells_of_type("comfort_cell")
        print("CELL", comfort_cells)
        check1 = self.__check(len(comfort_cells)==1)       
        print(f"\t{check1} comfort_cell: should have ONE comfort cell")
        check2 = self.__check(comfort_cells[0]['source'].strip()=="")
        print(f"\t{check1} comfort_cell: should should be empty")

        questions_cells = self.markdown_cells_of_type("question_cell")
        print("CELL", questions_cells)
        check1 = self.__check(len(questions_cells)==1)       
        print(f"\t{check1} question_cell: should have ONE questions cell")
        check2 = self.__check(questions_cells[0]['source'].strip()=="")
        print(f"\t{check1} question_cell: should should be empty")
        

    
    def check_lab(self, output_issues=True):
        '''
        Pre-check/ pre-grade lab before submission.
        '''
        row = { 'issues': [], 'details': [] }
        # INVENTORY
        run_code_cells = self.code_cells_of_type("run_code")
        exercise_code_cells =  self.exercise_code_cells
        all_code_cells = run_code_cells + exercise_code_cells
        executed_cells = [c for c in all_code_cells if c.execution_count is not None and c.execution_count >=1]
        row['code_cells'] = len(all_code_cells)
        row['code_cells_executed'] = len(executed_cells)
        row['code_cells_pct'] = f"{row['code_cells_executed']/row['code_cells']}"
        if float(row['code_cells_pct']) < 1.0:
            row['issues'].append("Not all code cells were executed.")
            
        try:
            comfort_cell = self.markdown_cells_of_type("comfort_cell")[0]
            row['comfort_level'] = comfort_cell['source'].strip()
            if row['comfort_level'] == "":
                row['issues'].append("Comfort level is blank.")
            elif row['comfort_level'].isdigit():
                c = int(row['comfort_level']) 
                if not c in [1,2,3,4]:
                    row['issues'].append("Comfort level should be 1,2,3 or 4.")
            else:
                 row['issues'].append("Comfort level should be 1,2,3 or 4.")
                
        except IndexError:
            print("ERROR: Missing Comfort Cell. Did you erase it?")

        try:
            question_cell = self.markdown_cells_of_type("question_cell")[0]
            row['questions'] = question_cell['source'].strip()
            if row['questions'] == "":
                row['issues'].append("Questions cell is blank. You should have a question or comment.")
    
        except IndextError:
            print("ERROR: Missing Question Cell. Did you erase it?")

        
        for cell in exercise_code_cells:
            label = self._extract_metadata_value(cell, "label")
            student_code = "\n".join([line for line in cell.source.split("\n") if not line.strip().startswith("#")]).strip()
            solution_code = "".join(self._extract_metadata_value(cell, "solution"))
            syntax = ct.syntax_check(student_code)
            similarity = ct.code_similarity_check(solution_code, student_code)

            row[label] = { 
                'has_code': 'no' if student_code == "" else 'yes',
                'syntax': 'ok' if syntax['ok'] else 'error',
                'similarity': similarity['pct_similar']
            }
            details = {
                'label': label,
                'data' : row[label],
                'syntax': syntax,
                'similarity': similarity,
                'student': student_code,
                'solution': solution_code
            }
            row['details'].append(details)

            if row[label]['has_code'] == 'no':
                row['issues'].append(f"{label} does not have a code solution.")
            elif row[label]['syntax'] == 'error':
                row['issues'].append(f"{label} code has syntax error: {syntax['error']}")
            elif float(row[label]['similarity']) < 0.5:
                row['issues'].append(f"{label} code not at least 50% similar to expected solution.")

        
        if output_issues:
            for issue in row['issues']:
                print(f"{CANCEL} {issue}")
            if len(row['issues']) == 0:    
                print(f"{OK} The lab submission appears to have no issues.")
                print(f"  {row['code_cells_pct']} Percent of cell executed.")
                print("  Summary of code Exercises")
                print("  CODE\tSYNTAX\tSIMILARITY")
                for d in row['details']:
                    print(f"  {d['label']}\t{d['data']['syntax']}\t{d['data']['similarity']}")
        else:       
            return row


    def validate_homework(self):
        '''
        validated the homework file has the necessary metadata cells for the self-check, and lab is ready to publish. This is an author's tool to make sure check_lab will work.
        '''
        check1 = self.__check(self.has_submission_cell)
        print(f"{check1} notebook: has submission cell")

        cell_types = ['analysis_output_cell', "analysis_input_cell", "analysis_plan_cell", "learned_cell", "challenges_cell", "prepared_cell", "help_cell", "comfort_cell"]

        for cell_type in cell_types:            
            cells = self.markdown_cells_of_type(cell_type)
            print("CELL", cells)
            check1 = self.__check(len(cells)==1)       
            print(f"\t{check1} {cell_type}: should have ONE {cell_type.replace('_cell','')} cell")
            check2 = self.__check(cells[0]['source'].strip()=="")
            print(f"\t{check1} {cell_type}: should should be empty")

        code_cells = self.code_cells_of_type("write_code")
        for ec_cell in code_cells:
            print(ec_cell)
            student_code = "\n".join([line for line in ec_cell.source.split("\n") if not line.strip().startswith("#")]).strip()
            check3 = self.__check(student_code == "")
            print(f"\t{check3} exercise_code cell: code_cell_type='write_code' cell should be empty {student_code}")

    def check_homework(self, output_issues=True):
        '''
        Pre-check/ pre-grade homework before submission.
        '''
        row = { 'issues': [], 'details': [] }
        # INVENTORY
        exercise_code_cells =  self.exercise_code_cells

        mandatory_cells = ['analysis_output_cell', "analysis_input_cell", "analysis_plan_cell", "learned_cell", "challenges_cell", "prepared_cell", "help_cell"]
        friendly_names = [ 'Problem Analysis 1.1 Program Outputs', 'Problem Analysis 1.2 Program Inputs', 'Problem Analysis 1.3 The Plan (Algorithm)', 'Metacognition 3.1', 'Metacognition 3.2', 'Metacognition 3.3', 'Metacognition 3.4']
        index = 0
        for cell_type in mandatory_cells:
            try:
                cell = self.markdown_cells_of_type(cell_type)[0]
                row[cell_type] = cell['source'].strip()
                if row[cell_type] == "":
                    row['issues'].append(f"{friendly_names[index]} cell is blank. Thoughtful completion of this section factors into your grade.")
        
            except IndextError:
                print(f"ERROR: Missing {friendly_names[index]} Cell. Did you erase it?")
            index +=1
        
        try:
            comfort_cell = self.markdown_cells_of_type("comfort_cell")[0]
            row['comfort_level'] = comfort_cell['source'].strip()
            if row['comfort_level'] == "":
                row['issues'].append("Metacognition 3.5 Comfort level is blank.")
            elif row['comfort_level'].isdigit():
                c = int(row['comfort_level']) 
                if not c in [1,2,3,4]:
                    row['issues'].append("Metacognition 3.5 Comfort level should be 1,2,3 or 4.")
            else:
                 row['issues'].append("Metacognition 3.5 Comfort level should be 1,2,3 or 4.")                
        except IndexError:
            print("ERROR: Missing Metacognition 3.5 Cell. Did you erase it?")

        
        for cell in exercise_code_cells:
            label = self._extract_metadata_value(cell, "label")
            student_code = "\n".join([line for line in cell.source.split("\n") if not line.strip().startswith("#")]).strip()
            solution_code = "".join(self._extract_metadata_value(cell, "solution"))
            syntax = ct.syntax_check(student_code)
            similarity = ct.code_similarity_check(solution_code, student_code)

            row[label] = { 
                'has_code': 'no' if student_code == "" else 'yes',
                'syntax': 'ok' if syntax['ok'] else 'error',
                'similarity': similarity['pct_similar']
            }
            details = {
                'label': label,
                'data' : row[label],
                'syntax': syntax,
                'similarity': similarity,
                'student': student_code,
                'solution': solution_code
            }
            row['details'].append(details)

            if row[label]['has_code'] == 'no':
                row['issues'].append(f"{label} does not have a code solution.")
            elif row[label]['syntax'] == 'error':
                row['issues'].append(f"{label} code has syntax error: {syntax['error']}. Fix errors for a better grade.")
            # elif float(row[label]['similarity']) < 0.5:
            #     row['issues'].append(f"{label} code not at least 50% similar to expected solution.")
        
        if output_issues:
            for issue in row['issues']:
                print(f"{CANCEL} {issue}")
            if len(row['issues']) == 0:    
                print(f"{OK} Completed the problem analysis.")
                print(f"{OK} Solution Cell has no syntax errors.")
                print(f"{OK} Completed your metacognition.")
        else:         
            return row

# import nbformat


# ##############################################
# # Cells

# def is_template_header_cell(cell):
#     header = cell['metadata'].get('cass', None)
#     return header == {'cell_type': "grading_header"}

# def is_code(cell):
#     return cell.get('cell_type','') == 'code'

# def is_markdown(cell):
#     return cell.get('cell_type','') == 'markdown'

# def get_code(cell):
#     if is_code(cell):
#         return "".join([line for line in cell["source"] if not line.strip().startswith("#") ] )
#     else:
#         return ""

# def get_code_cell_type(cell):
#     if is_code(cell):
#         return cell['metadata'].get('code_cell_type',None)
#     else:
#         return None

# def has_code(cell):
#     return len(get_code(cell)) > 0
    
# def was_executed(cell):
#     if is_code(cell):
#         return cell.get('execution_count',None) != None
#     else:
#         return False
    
# def has_solution(cell):
#     if is_code(cell):
#         return len(cell['metadata'].get('solution', [])) >0
#     else:
#         return False
    
# def get_solution(cell):
#     if has_solution(cell):
#         return "".join(cell['metadata']['solution'])
#     else:
#         return None

# def get_label(cell):
#     return cell['metadata'].get('label', None)
    
# def get_code_output_type(cell):
#     if was_executed(cell) and not len(cell.get('outputs',[]))==0:
#         return cell['outputs'][0]['output_type']
#     else:
#         return None
    
# def get_code_output(cell):
#     code_output_type = get_code_output_type(cell)
#     if code_output_type == 'stream':
#         return "".join(cell['outputs'][0]['text'])
#     elif code_output_type == 'execute_result':
#         return cell['outputs'][0]['data']
#     else:
#         return None

# ########################################
# # Notebooks




# def get_code_cells(notebook):
#     nb = nbformat(notebook)

# def get_run_code_cells(notebook):
#     pass

# def has_comfort_cell(notebook):
#     for cell in notebook['cells']:
#         if is_markdown(cell) and cell['metadata'].get('label',"") == "comfort_cell":
#             return True
#     return False

# def has_questions_cell(notebook):
#     for cell in notebook['cells']:
#         if is_markdown(cell) and cell['metadata'].get('label',"") == "questions_cell":
#             return True
#     return False

# def has_homework_questions_cell(notebook):
#     for cell in notebook['cells']:
#         if is_markdown(cell) and cell['metadata'].get('label',"") == "homework_questions_cell":
#             return True
#     return False

# def has_reflection_cell(notebook):
#     for cell in notebook['cells']:
#         if is_markdown(cell) and cell['metadata'].get('label',"") == "reflection_cell":
#             return True
#     return False

# def has_problem_analysis_cell(notebook):
#     for cell in notebook['cells']:
#         if is_markdown(cell) and cell['metadata'].get('label',"") == "problem_analysis_cell":
#             return True
#     return False

# def has_code_solution_cell(notebook):
#     for cell in notebook['cells']:
#         if is_code(cell) and cell['metadata'].get('label',"") == "code_solution_cell":
#             return True
#     return False

# def get_comfort_level(notebook):
#     extract = "None"
#     TOKEN = " ==--`"
#     for cell in notebook['cells']:
#         if is_markdown(cell) and cell['metadata'].get('label',"") == "comfort_cell":
#             text = "".join(cell['source'])
#             extract = text[text.find(TOKEN)+len(TOKEN):].strip()
#             try:
#                 return int(extract)
#             except ValueError:
#                 return "None"
#     return extract


# def get_questions(notebook):
#     extract = ""
#     TOKEN = " ==--`"
#     for cell in notebook['cells']:
#         if is_markdown(cell) and cell['metadata'].get('label',"") == "questions_cell":
#             text = "".join(cell['source'])
#             extract = text[text.find(TOKEN)+len(TOKEN):].strip()        
#             return extract
#     return extract


