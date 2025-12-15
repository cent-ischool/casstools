import json
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

def render_table(table_data):
    """Render table data as styled HTML table.
    
    Accepts:
    - dict with 'headers' and 'rows': {'headers': ['A', 'B'], 'rows': [[1, 2], [3, 4]]}
    - list of dicts (records): [{'A': 1, 'B': 2}, {'A': 3, 'B': 4}]
    - pandas DataFrame
    """
    style = """<style>
        .quiz-table { border-collapse: collapse; margin: 10px 0; font-size: 14px; }
        .quiz-table th, .quiz-table td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
        .quiz-table th { background: #4a4a4a; color: white; }
        .quiz-table tr:nth-child(even) { background: #f9f9f9; }
        .quiz-table tr:hover { background: #f1f1f1; }
    </style>"""
    
    # Handle pandas DataFrame
    if hasattr(table_data, 'to_html'):
        return style + table_data.to_html(classes='quiz-table', index=True)
    
    # Handle list of dicts (records format)
    if isinstance(table_data, list) and len(table_data) > 0 and isinstance(table_data[0], dict):
        headers = list(table_data[0].keys())
        rows = [[row.get(h, '') for h in headers] for row in table_data]
    # Handle dict with headers and rows
    elif isinstance(table_data, dict):
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
    else:
        return "<p>Invalid table format</p>"
    
    html = style + "<table class='quiz-table'><thead><tr>"
    html += "".join(f"<th>{h}</th>" for h in headers)
    html += "</tr></thead><tbody>"
    for row in rows:
        html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    html += "</tbody></table>"
    return html


def display_question(question: dict, index: int = 0):
    """Display an interactive quiz question using ipywidgets.
    
    Question dict can include:
    - question: str - the question text
    - code: str - optional code block
    - table: dict/list/DataFrame - optional data table
    - type: 'multiple_choice', 'many_choice', or 'numeric'
    - answers: list of answer options
    """
    
    q_type = question.get('type', 'multiple_choice')
    q_text = question.get('question', '')
    q_code = question.get('code', '')
    q_table = question.get('table', None)
    answers = question.get('answers', [])
    
    # Build question HTML with optional code block and table
    q_html = f"<h4 style='margin-bottom: 10px;'>{q_text}</h4>"
    
    if q_code:
        q_html += f"""<pre style='background: #f4f4f4; padding: 10px; border-radius: 5px; 
                       border-left: 3px solid #2196F3; font-family: monospace; 
                       font-size: 14px; overflow-x: auto; margin: 10px 0;'><code>{q_code}</code></pre>"""
    
    if q_table is not None:
        q_html += render_table(q_table)
    
    question_html = widgets.HTML(q_html)
    
    # Feedback output area
    feedback_out = widgets.Output()
    
    # Store response
    response_store = widgets.HTML(value='', layout=widgets.Layout(display='none'))

    display(HTML(f"<h3>Question {index+1}"))
    
    if q_type in ['multiple_choice', 'many_choice']:
        options = [a.get('answer', '') for a in answers]
        answer_widget = widgets.RadioButtons(
            options=options,
            value=None,
            description='',
            disabled=False,
            layout=widgets.Layout(width='auto')
        )
        
        def on_answer_change(change):
            selected = change['new']
            if selected is None:
                return
            with feedback_out:
                clear_output(wait=True)
                for a in answers:
                    if a.get('answer') == selected:
                        correct = a.get('correct', False)
                        feedback = a.get('feedback', '')
                        color = '#009113' if correct else '#c80202'
                        icon = '✓' if correct else '✗'
                        display(HTML(f"<p style='color:{color};font-weight:bold;'>{icon} {feedback}</p>"))
                        response_store.value = f'{{"answer": "{selected}", "correct": {str(correct).lower()}}}'
                        break
        
        answer_widget.observe(on_answer_change, names='value')
        display(widgets.VBox([question_html, answer_widget, feedback_out, response_store]))
        
    elif q_type == 'numeric':
        answer_widget = widgets.Text(
            placeholder='Enter your answer',
            description='Answer:',
            layout=widgets.Layout(width='200px')
        )
        submit_btn = widgets.Button(description='Submit', button_style='primary')
        
        def on_submit(btn):
            try:
                user_val = float(eval(answer_widget.value))
            except:
                with feedback_out:
                    clear_output(wait=True)
                    display(HTML("<p style='color:#c80202;'>Invalid input. Enter a number or fraction.</p>"))
                return
            
            with feedback_out:
                clear_output(wait=True)
                correct = False
                feedback = ''
                
                for a in answers:
                    a_type = a.get('type', 'value')
                    if a_type == 'value':
                        precision = question.get('precision', 2)
                        if round(user_val, precision) == round(a.get('value', 0), precision):
                            correct = a.get('correct', True)
                            feedback = a.get('feedback', '')
                            break
                    elif a_type == 'range':
                        r = a.get('range', [0, 0])
                        if r[0] <= user_val < r[1]:
                            correct = a.get('correct', False)
                            feedback = a.get('feedback', '')
                            break
                    elif a_type == 'default':
                        feedback = a.get('feedback', '')
                
                color = '#009113' if correct else '#c80202'
                icon = '✓' if correct else '✗'
                display(HTML(f"<p style='color:{color};font-weight:bold;'>{icon} {feedback}</p>"))
                response_store.value = f'{{"answer": "{answer_widget.value}", "correct": {str(correct).lower()}}}'
        
        submit_btn.on_click(on_submit)
        display(widgets.VBox([question_html, widgets.HBox([answer_widget, submit_btn]), feedback_out, response_store]))
    
    else:
        display(HTML(f"<p>Unknown question type: {q_type}</p>"))

def render_quiz(filename: str):
    with open (filename, "r") as f:
        questions = json.load(f)
    title = filename.replace(".json","").replace("-"," ").title()        
    display(HTML(f"<h2>{title}"))
    for i, q in enumerate(questions):
        display_question(q, i)