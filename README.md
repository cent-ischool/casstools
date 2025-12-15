# casstools

Client tools for CASS (Course Assignment Submission System)

The client works with the server. The CASS server is a REST API. It validates who is permitted to submit what and keeps track of those submissions. 

### Checking notebooks

Notebook checkers uses metadata int the assignment cells to check student code against the solutions. It also looks for missing work / blank cells.


### Check homework

```
from casstools.notebook_tools import NotebookFile
NotebookFile().check_homework()
```

Example output:
```
❌ Problem Analysis 1.1 Program Outputs cell is blank. Thoughtful completion of this section factors into your grade.
❌ Problem Analysis 1.2 Program Inputs cell is blank. Thoughtful completion of this section factors into your grade.
❌ Problem Analysis 1.3 The Plan (Algorithm) cell is blank. Thoughtful completion of this section factors into your grade.
❌ Metacognition 3.1 cell is blank. Thoughtful completion of this section factors into your grade.
❌ Metacognition 3.2 cell is blank. Thoughtful completion of this section factors into your grade.
❌ Metacognition 3.3 cell is blank. Thoughtful completion of this section factors into your grade.
❌ Metacognition 3.4 cell is blank. Thoughtful completion of this section factors into your grade.
❌ Metacognition 3.5 Comfort level is blank.
❌ 2.1 failed automated test with inputs: '2 4 10 3' Expected output should contain '120'. Actual output was '416 3 can 832'
❌ 2.1 failed automated test with inputs: '2 4 10 3' Expected output should contain '360'. Actual output was '416 3 can 832'
❌ 2.1 failed automated test with inputs: '2 4 10 3' Expected output should contain '1 can'. Actual output was '416 3 can 832'
```

#### Check Lab

```
from casstools.notebook_tools import NotebookFile
NotebookFile().check_lab()
```

Example output:

```
❌ Not all code cells were executed.
❌ Comfort level is blank.
❌ Questions cell is blank. You should have a question or comment.
❌ 1.1 you code does not have a code solution.
❌ 1.2 you code has syntax error:    line 3
    say = input "What say you? ")
                                ^
SyntaxError: unmatched ')'

❌ 1.3 you code does not have a code solution.
❌ 1.4 you code does not have a code solution.
```


### Submitting

Submitting Assignments will use the CASS server API to verify the current juptyerhub user is permitted to submit and that the assignment is registered with the API (you just can't submit anything.

#### Submit Homework / Lab

```
from casstools.assignment import Assignment
Assignment().submit()
```

Example Output:

```
✅ TIMESTAMP  : 2024-02-04 13:14
✅ COURSE     : ist256
✅ TERM       : spring2024
✅ USER       : mafudge@syr.edu
✅ STUDENT    : True
✅ PATH       : ist256/spring2024/lessons/02-Variables/HW-Variables.ipynb
✅ ASSIGNMENT : HW-Variables.ipynb
✅ POINTS     : 3
✅ DUE DATE   : 2024-02-02 23:59
✅ LATE       : True
✅ STATUS     : New Submission

❓ Assignment is late. Submit? [y/n] ❓  n
👎 Submission Cancelled
```

### Self Check Quizzes

The CASS system can also generate self-check quizzes from JSON files. The quizzes are designed to provide instant feedback and advice on incorrect questions.

```
from interact_quiz import render_quiz
render_quiz("L02-self-check.json")
```

Example Output:

```
Question 1
Which of these is the ratio of a circle's circumference to its diameter?
π (pi)
22/7
3 😊
τ (tau)
✓ Correct!
```


To create questions, there is a JSON schema `interact_quiz_question_schema.json` this can be used with generative AI to create questions in the proper JSON format.


