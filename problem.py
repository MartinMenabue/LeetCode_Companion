from utils import base_url
import os
from markdownify import markdownify as md
import json
import re
import inspect
import importlib
import time
from utils import write_to_file


def prepare_problem(args, session, problem_name):
    desc = get_problem_description(args, session, problem_name)
    desc = md(desc)
    code_str = get_problem_code(args, session, problem_name)
    testcases, metadata = get_problem_testcases_and_metadata(args, session, problem_name)
    final_testcases_str = '[\n'
    if 'name' in metadata:
        func_name = metadata['name']
        params_info = metadata['params']
        testcases_str = '    s = Solution()\n'
        for i, testcase in enumerate(testcases):
            lines = testcase.split('\n')
            l = []
            final_testcases_str += '    {'
            for p_idx, line in enumerate(lines):
                pname = params_info[p_idx]['name']
                ptype = params_info[p_idx]['type']
                l.append(f'{pname}={line}')
                final_testcases_str += f'"{pname}": {line}'
                if p_idx < len(lines) - 1:
                    final_testcases_str += ', '
            final_testcases_str += '},\n' if i < len(testcases) - 1 else '}\n'
            testcases_str += f'    s.{func_name}({", ".join(l)})\n'
    elif 'classname' in metadata:
        classname = metadata['classname']
        constructor_params = metadata['constructor']['params']
        testcases_str = ''
        for i, testcase in enumerate(testcases):
            names = json.loads(testcase.split('\n')[0])
            values = json.loads(testcase.split('\n')[1])
            final_testcases_str += '    {\n'
            final_testcases_str += f'        "names": {json.dumps(names)},\n        "values": {json.dumps(values)}\n'
            final_testcases_str += '    },\n' if i < len(testcases) - 1 else '    }\n'

            constructor_args = values[0]
            if constructor_args:
                constructor_args = ', '.join([str(v) for v in constructor_args])
            else:
                constructor_args = ''
            testcases_str += f'    obj = {classname}({constructor_args})\n'
            for idx, (name, value) in enumerate(zip(names[1:], values[1:])):
                if value:
                    value = ', '.join([str(v) for v in value])
                else:
                    value = ''
                testcases_str += f'    obj.{name}({value})\n'
    else:
        raise Exception(f'Could not prepare problem {problem_name}')

    final_testcases_str += ']'

    code = 'from typing import List, Tuple, Dict, Any'
    code += '\n\n'
    code += f'{code_str}\n\n'
    code += '''if __name__ == '__main__':\n'''
    code += f'{testcases_str}\n'

    target_dir = os.path.join(os.getcwd(), 'problems', problem_name)
    os.makedirs(target_dir, exist_ok=True)
    write_to_file(os.path.join(target_dir, 'README.md'), desc)
    write_to_file(os.path.join(target_dir, 'solution.py'), code)
    write_to_file(os.path.join(target_dir, 'testcases.json'), final_testcases_str)
    
    print(f'Problem {problem_name} prepared in {target_dir}')

def get_problem_description(args, session, problem_name):
    data = {
        'operationName': 'questionContent',
        'variables': {
            'titleSlug': problem_name
        },
        'query': '''query questionContent($titleSlug: String!) {
                        question(titleSlug: $titleSlug) {
                            content
                            mysqlSchemas
                            dataSchemas
                        }
                    }'''
    }
    res = session.post(f'{base_url}/graphql/', json=data)
    html = res.json()['data']['question']['content']
    return html

def get_problem_testcases_and_metadata(args, session, problem_name):
    data = {
        'operationName': 'questionTestcases',
        'variables': {
            'titleSlug': problem_name
        },
        'query': '''query questionTestcases($titleSlug: String!) {
                        question(titleSlug: $titleSlug) {
                            exampleTestcaseList
                            metaData
                        }
                    }'''
    }
    res = session.post(f'{base_url}/graphql/', json=data)
    testcases = res.json()['data']['question']['exampleTestcaseList']
    metadata = json.loads(res.json()['data']['question']['metaData'])
    return testcases, metadata

def get_problem_code(args, session, problem_name):
    data = {
        'operationName': 'questionEditorData',
        'variables': {
            'titleSlug': problem_name
        },
        'query': '''query questionEditorData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                codeSnippets {
                lang
                langSlug
                code
                }
                envInfo
                enableRunCode
                hasFrontendPreview
                frontendPreviews
            }
        }'''
    }
    res = session.post(f'{base_url}/graphql/', json=data)
    codes = res.json()['data']['question']['codeSnippets']
    # get python code
    code = ''
    for c in codes:
        if c['lang'] == 'Python3':
            code = c['code']
            break
    return code

def get_problem_hints(args, session, problem_name):
    data = {
        'operationName': 'questionHints',
        'variables': {
            'titleSlug': problem_name
        },
        'query': '''query questionHints($titleSlug: String!) {
                        question(titleSlug: $titleSlug) {
                            hints
                        }
                    }'''
    }
    res = session.post(f'{base_url}/graphql/', json=data)
    hints = res.json()['data']['question']['hints']
    return hints

def get_problem_id(args, session, problem_name):
    data = {
        'operationName': 'questionId',
        'variables': {
            'titleSlug': problem_name
        },
        'query': '''query questionId($titleSlug: String!) {
                        question(titleSlug: $titleSlug) {
                            questionId
                        }
                    }'''
    }
    res = session.post(f'{base_url}/graphql/', json=data)
    id = res.json()['data']['question']['questionId']
    return id

def get_submission_details(args, session, submission_id):
    data = {
        'operationName': 'submissionDetails',
        'variables': {
            'submissionId': submission_id
        },
        'query': '''\n    query submissionDetails($submissionId: Int!) {\n  submissionDetails(submissionId: $submissionId) {\n    runtime\n    runtimeDisplay\n    runtimePercentile\n    runtimeDistribution\n    memory\n    memoryDisplay\n    memoryPercentile\n    memoryDistribution\n    code\n    timestamp\n    statusCode\n    user {\n      username\n      profile {\n        realName\n        userAvatar\n      }\n    }\n    lang {\n      name\n      verboseName\n    }\n    question {\n      questionId\n      titleSlug\n      hasFrontendPreview\n    }\n    notes\n    flagType\n    topicTags {\n      tagId\n      slug\n      name\n    }\n    runtimeError\n    compileError\n    lastTestcase\n    codeOutput\n    expectedOutput\n    totalCorrect\n    totalTestcases\n    fullCodeOutput\n    testDescriptions\n    testBodies\n    testInfo\n    stdOutput\n  }\n}\n    '''
    }
    res = session.post(f'{base_url}/graphql/', json=data)
    details = res.json()['data']['submissionDetails']
    return details

def handle_result(args, session, problem_name, submission_id, submit=True):
    while True:
        headers = {
            'Referer': f'{base_url}/problems/{problem_name}/',
            'X-Csrftoken': session.cookies['csrftoken']
        }
        res = session.get(f'{base_url}/submissions/detail/{submission_id}/check/', headers=headers)
        if res.status_code != 200:
            raise Exception('Error in getting the submission result')
        state = res.json()['state']
        if state == 'PENDING' or state == 'STARTED':
            print('Waiting for result...')
            time.sleep(1)
        else:
            break
    if state == 'FAILURE':
        print('#### FAILURE ####')
        print(res.json())
    if state == 'SUCCESS':
        status_msg = res.json()['status_msg']
        if status_msg.lower() == 'wrong answer':
            print('#### WRONG ANSWER ####')
            print('Your solution is incorrect')
            total_correct = res.json()['total_correct']
            total_testcases = res.json()['total_testcases']
            print(f'You solved {total_correct} out of {total_testcases} test cases')
            last_testcase = res.json()['last_testcase']
            code_output = res.json()['code_output']
            std_output = res.json()['std_output'].strip()
            expected_output = res.json()['expected_output']
            print(f'Last testcase input: {last_testcase}')
            if std_output:
                print(f'Stdout: {std_output}')
            print(f'Expected output: {expected_output}')
            print(f'Your output: {code_output}')
        elif status_msg.lower() == 'accepted':
            print('#### CORRECT ANSWER ####')
            if submit:
                print('Congratulations! You solved the problem!')
            else:
                print('Your solution passed all the provided test cases. You can now submit the solution')
        elif status_msg.lower() == 'runtime error':
            print('#### RUNTIME ERROR ####')
            print('Your solution encountered a runtime error')
            runtime_error = res.json()['runtime_error']
            print(f'Error: {runtime_error}')
        else:
            print('Unexpected status message')
    else:
        print('Something went wrong, please try again')

def get_typed_code(args, session, problem_name, metadata):
    if 'classname' in metadata:
        classname = metadata['classname']
    elif 'name' in metadata:
        classname = 'Solution'
    else:
        raise Exception('Could not find the class name')
    module_name = f'problems.{problem_name}.solution'
    module = importlib.import_module(module_name)
    # get the solution code
    typed_code = inspect.getsource(getattr(module, classname))
    return typed_code

def interpret_solution(args, session, problem_name):
    problem_id = get_problem_id(args, session, problem_name)
    testcases, metadata = get_problem_testcases_and_metadata(args, session, problem_name)
    typed_code = get_typed_code(args, session, problem_name, metadata)
    testcases = '\n'.join(testcases)
    data = {
        'typed_code': typed_code,
        'data_input': testcases,
        'lang': 'python3',
        'question_id': problem_id, 
    }
    headers = {
        'Referer': f'{base_url}/problems/{problem_name}/description',
        'X-Csrftoken': session.cookies['csrftoken']
    }
    res = session.post(f'{base_url}/problems/{problem_name}/interpret_solution/', json=data, headers=headers)
    if res.status_code != 200:
        raise Exception('Error in submitting the solution')
    print('Solution submitted successfully')
    interpret_id = res.json()['interpret_id']
    test_case = res.json()['test_case']
    handle_result(args, session, problem_name, interpret_id, submit=False)
    
def submit_solution(args, session, problem_name):
    problem_id = get_problem_id(args, session, problem_name)
    testcases, metadata = get_problem_testcases_and_metadata(args, session, problem_name)
    typed_code = get_typed_code(args, session, problem_name, metadata)
    data = {
        'typed_code': typed_code,
        'lang': 'python3',
        'question_id': problem_id, 
    }
    headers = {
        'Referer': f'{base_url}/problems/{problem_name}/description',
        'X-Csrftoken': session.cookies['csrftoken']
    }
    res = session.post(f'{base_url}/problems/{problem_name}/submit/', json=data, headers=headers)
    if res.status_code != 200:
        raise Exception('Error in submitting the solution')
    print('Solution submitted successfully')
    submission_id = res.json()['submission_id']
    handle_result(args, session, problem_name, submission_id)


    