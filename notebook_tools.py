import nbformat








##############################################
# Cells

def is_template_header_cell(cell):
    header = cell['metadata'].get('cass', None)
    return header == {'cell_type': "grading_header"}

def is_code(cell):
    return cell.get('cell_type','') == 'code'

def is_markdown(cell):
    return cell.get('cell_type','') == 'markdown'

def get_code(cell):
    if is_code(cell):
        return "".join([line for line in cell["source"] if not line.strip().startswith("#") ] )
    else:
        return ""

def get_code_cell_type(cell):
    if is_code(cell):
        return cell['metadata'].get('code_cell_type',None)
    else:
        return None

def has_code(cell):
    return len(get_code(cell)) > 0
    
def was_executed(cell):
    if is_code(cell):
        return cell.get('execution_count',None) != None
    else:
        return False
    
def has_solution(cell):
    if is_code(cell):
        return len(cell['metadata'].get('solution', [])) >0
    else:
        return False
    
def get_solution(cell):
    if has_solution(cell):
        return "".join(cell['metadata']['solution'])
    else:
        return None

def get_label(cell):
    return cell['metadata'].get('label', None)
    
def get_code_output_type(cell):
    if was_executed(cell) and not len(cell.get('outputs',[]))==0:
        return cell['outputs'][0]['output_type']
    else:
        return None
    
def get_code_output(cell):
    code_output_type = get_code_output_type(cell)
    if code_output_type  == 'stream':
        return "".join(cell['outputs'][0]['text'])
    elif code_output_type == 'execute_result':
        return cell['outputs'][0]['data']
    else:
        return None
    
########################################
# Notebooks




def get_code_cells(notebook):
    nb = nbformat(notebook)

def get_run_code_cells(notebook):
    pass

def has_comfort_cell(notebook):
    for cell in notebook['cells']:
        if is_markdown(cell) and cell['metadata'].get('label',"") == "comfort_cell":
            return True
    return False

def has_questions_cell(notebook):
    for cell in notebook['cells']:
        if is_markdown(cell) and cell['metadata'].get('label',"") == "questions_cell":
            return True
    return False

def has_homework_questions_cell(notebook):
    for cell in notebook['cells']:
        if is_markdown(cell) and cell['metadata'].get('label',"") == "homework_questions_cell":
            return True
    return False

def has_reflection_cell(notebook):
    for cell in notebook['cells']:
        if is_markdown(cell) and cell['metadata'].get('label',"") == "reflection_cell":
            return True
    return False

def has_problem_analysis_cell(notebook):
    for cell in notebook['cells']:
        if is_markdown(cell) and cell['metadata'].get('label',"") == "problem_analysis_cell":
            return True
    return False

def has_code_solution_cell(notebook):
    for cell in notebook['cells']:
        if is_code(cell) and cell['metadata'].get('label',"") == "code_solution_cell":
            return True
    return False

def get_comfort_level(notebook):
    extract = "None"
    TOKEN = " ==--`"
    for cell in notebook['cells']:
        if is_markdown(cell) and cell['metadata'].get('label',"") == "comfort_cell":
            text = "".join(cell['source'])
            extract = text[text.find(TOKEN)+len(TOKEN):].strip()
            try:
                return int(extract)
            except ValueError:
                return "None"
    return extract


def get_questions(notebook):
    extract = ""
    TOKEN = " ==--`"
    for cell in notebook['cells']:
        if is_markdown(cell) and cell['metadata'].get('label',"") == "questions_cell":
            text = "".join(cell['source'])
            extract = text[text.find(TOKEN)+len(TOKEN):].strip()        
            return extract
    return extract


