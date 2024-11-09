import webbrowser
from pathlib import Path
import os
import re

base_url = 'https://leetcode.com'

def write_to_file(file_path, content):
    if os.path.exists(file_path):
        res = input(f'File {file_path} already exists. Do you want to overwrite it? (yes/no) ')
        if res.lower() != 'yes':
            return
    with open(file_path, 'w') as f:
        f.write(content)

def check_login(args, session):
    verboseprint = print if args.verbose else lambda *a, **k: None
    sess_path = Path.home() / '.leetcode_session'
    if not os.path.exists(sess_path):
        print('Please, login to your LeetCode account.')
        print('Press F12 to open the developer console.')
        print('Go to the Application tab.')
        print('Expand "Cookies" on the left.')
        print('Click on the "https://leetcode.com" link.')
        print('Copy the LEETCODE_SESSION cookie and paste it here.')
        login_path = f'{base_url}/accounts/login/'
        webbrowser.open(login_path)
        leetcode_session = input('LEETCODE_SESSION: ')
        with open(sess_path, 'w') as f:
            f.write(leetcode_session)
    
    # check if the session token is valid
    with open(sess_path, 'r') as f:
        leetcode_session = f.read()
    session.cookies['LEETCODE_SESSION'] = leetcode_session
    response = session.get(f'{base_url}/profile/', impersonate="chrome")
    try:
        ret = re.findall(r'realName: \'(.*)\'', response.text)[0]
        target_path = Path.home() / '.leetcode_session'
        with open(target_path, 'w') as f:
            f.write(leetcode_session)
    except:
        print('Invalid LEETCODE_SESSION cookie. Please rerun the script.')
        os.remove(sess_path)
        exit(1)
    verboseprint(f'Welcome, {ret}!')

def get_user_api_token(args, session):
    data = {
        'operationName': 'getUserApiToken',
        'variables': {},
        'query': '''query getUserApiToken {
                        generateLeetcodeUserApiToken {
                            token
                        }
                    }'''
    }
    res = session.post(f'{base_url}/graphql/', json=data)
    api_token = res.json()['data']['generateLeetcodeUserApiToken']['token']
    return api_token
