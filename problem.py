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
    code = get_problem_code(args, session, problem_name)
    func_name = re.findall(r'def (.*)\(', code)[0]
    testcases, params = get_problem_testcases(args, session, problem_name)
    target_dir = os.path.join(os.getcwd(), 'problems', problem_name)
    os.makedirs(target_dir, exist_ok=True)
    write_to_file(os.path.join(target_dir, 'README.md'), desc)
    params_strings = []
    for i, param in enumerate(params):
        ps = ', '.join([f'{k}={v}' for k, v in param.items()])
        params_strings.append(ps)
    code = f'''from typing import List, Tuple, Dict, Any

{code}

if __name__ == '__main__':
    s = Solution()
'''
    for i, ps in enumerate(params_strings):
        code += f'    s.{func_name}({ps})\n'
    write_to_file(os.path.join(target_dir, 'solution.py'), code)
    tmp = '[\n'
    for idx, pinfo in enumerate(params):
        tmp += f'    {json.dumps(pinfo)},\n' if idx < len(params) - 1 else f'    {json.dumps(pinfo)}\n'
    tmp += ']'
    write_to_file(os.path.join(target_dir, 'testcases.json'), tmp)
    
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
                            exampleTestcaseList
                            mysqlSchemas
                            dataSchemas
                        }
                    }'''
    }
    res = session.post(f'{base_url}/graphql/', json=data)
    html = res.json()['data']['question']['content']
    return html

def get_problem_testcases(args, session, problem_name):
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
    params_info = metadata['params']
    params = []
    for i, testcase in enumerate(testcases):
        params.append({})
        lines = testcase.split('\n')
        for p_idx, line in enumerate(lines):
            pname = params_info[p_idx]['name']
            ptype = params_info[p_idx]['type']
            pval = eval(line)
            params[-1][pname] = pval

    return testcases, params

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


def interpret_solution(args, session, problem_name):
    problem_id = get_problem_id(args, session, problem_name)
    module_name = f'problems.{problem_name}.solution'
    module = importlib.import_module(module_name)
    # get the solution code
    typed_code = inspect.getsource(module.Solution)
    # get the testcases
    testcases, params = get_problem_testcases(args, session, problem_name)
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
    while True:
        headers = {
            'Referer': f'{base_url}/problems/{problem_name}/',
            'X-Csrftoken': session.cookies['csrftoken']
        }
        res = session.get(f'{base_url}/submissions/detail/{interpret_id}/check/', headers=headers)
        if res.status_code != 200:
            raise Exception('Error in getting the submission result')
        state = res.json()['state']
        if state == 'PENDING':
            print('Waiting for result...')
            time.sleep(1)
        else:
            break
    if state == 'FAILURE':
        print('#### FAILURE ####')
        print(res.json())
    if state == 'SUCCESS':
        print('#### SUCCESS ####')
        print('You successfully solved the problem with the provided test cases')
        #print(res.json())
    
def submit_solution(args, session, problem_name):
    problem_id = get_problem_id(args, session, problem_name)
    module_name = f'problems.{problem_name}.solution'
    module = importlib.import_module(module_name)
    # get the solution code
    typed_code = inspect.getsource(module.Solution)
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
    while True:
        headers = {
            'Referer': f'{base_url}/problems/{problem_name}/',
            'X-Csrftoken': session.cookies['csrftoken']
        }
        res = session.get(f'{base_url}/submissions/detail/{submission_id}/check/', headers=headers)
        if res.status_code != 200:
            raise Exception('Error in getting the submission result')
        state = res.json()['state']
        if state == 'PENDING':
            print('Waiting for result...')
            time.sleep(1)
        else:
            break
    if state == 'FAILURE':
        print('#### FAILURE ####')
        print(res.json())
    if state == 'SUCCESS':
        print('#### SUCCESS ####')
        print('Congratulations! You solved the problem!')


    