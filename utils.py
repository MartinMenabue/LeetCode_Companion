import webbrowser
from pathlib import Path
import os
import jwt

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
    else:
        with open(sess_path, 'r') as f:
            leetcode_session = f.read()
    
    while True:
        try:
            ret = jwt.decode(leetcode_session, algorithms=["HS256"], options={"verify_signature": False})
            username = ret['username']
            session.cookies['LEETCODE_SESSION'] = leetcode_session
            ret = get_user_real_name(args, session)
            if ret is not None:
                break
            else:
                raise Exception
        except:
            print('Invalid LEETCODE_SESSION cookie. Please provide a correct one.')
            if os.path.exists(sess_path):
                os.remove(sess_path)
            leetcode_session = input('LEETCODE_SESSION: ')

    with open(sess_path, 'w') as f:
        f.write(leetcode_session)
    verboseprint(f'Welcome, {username}!')

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

def get_user_real_name(args, session):
    data = {
        'operationName': 'userRealName',
        'variables': {},
        'query': '''query userRealName {
                        user {
                            profile {
                            realName
                            __typename
                            }
                            __typename
                        }
                    }'''
    }
    res = session.post(f'{base_url}/graphql/', json=data)
    try:
        real_name = res.json()['data']['user']['profile']['realName']
    except:
        return None
    return real_name
