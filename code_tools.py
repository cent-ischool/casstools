##################################################################
# Code Tools
import pycode_similar
from subprocess import Popen, PIPE
import base64


def obfuscate(code: str) -> str:
    return base64.b64encode(code.encode("utf-8")).decode("utf-8")


def deobfuscate(encoded_code: str) -> str:
    return base64.b64decode(encoded_code.encode("utf-8")).decode("utf-8")


def syntax_check(code: str) -> dict:
    from os import remove
    with open ("_tmp_.py", "w") as f:
        f.write(code)
    process = Popen(['python','-m','py_compile', '_tmp_.py'], stdout=PIPE, stderr=PIPE)
    out,err = process.communicate()
    out = out.decode("utf-8")
    err = err.decode("utf-8").replace('File "_tmp_.py",',"") 
    remove("_tmp_.py")
    return  { 'ok' : err == "", 
             'output' : out,
             'error' : err }

def code_similarity_check(ref_code: str, candidate_code: str, diff_method = pycode_similar.UnifiedDiff) -> dict:
    try:
        code = [ ref_code, candidate_code ]
        results = pycode_similar.detect(code ,diff_method=diff_method, keep_prints=True, module_level=True)
        out = results[0][1][0]
        return { 'similar_token_count' : out.plagiarism_count, 
                'total_tokens' : out.total_count,
                'pct_similar' : out.plagiarism_percent }
    except:
        return { 'similar_token_count' : 0, 
                'total_tokens' : 0,
                'pct_similar' : 0 }


def execute_code(code: str, redirected_input: str) -> dict:
    process = Popen(['python', '-c', code], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    out, err = process.communicate(input=redirected_input.encode())
    out = out.decode("utf-8")
    err = err.decode("utf-8")
    return  { 'ok' : err == "",
        'input' : redirected_input,
        'output' : out,
        'error' : err }

# code = '''
# num1 = int(input("Enter #1 :"))
# num2 = int(input("Enter #2 :"))
# total = num1 + num2
# print(f"The total is: {total}")
# '''

# result = execute_code(code, "45\n60\n")
# try:
#     assert result['output'].strip().endswith("105")
#     print("ok")
# except AssertionError:
#     print("not ok")
