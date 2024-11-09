import argparse
from curl_cffi import requests
from utils import base_url, check_login
from problem import prepare_problem, interpret_solution, submit_solution

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LeetCode Companion')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print debug information')
    parser.add_argument('command', type=str, choices=['prepare', 'run', 'submit'], help='Command to execute')
    args1, other1 = parser.parse_known_args()
    s = requests.Session()
    verboseprint = print if args1.verbose else lambda *a, **k: None
    res = check_login(args1, s)
    if args1.command == 'prepare':
        parser = argparse.ArgumentParser(description='Prepare a problem')
        parser.add_argument('problem_name', type=str, help='Problem name')
        args2 = parser.parse_args(other1)
        for arg in vars(args2):
            setattr(args1, arg, getattr(args2, arg))
        args = args1
        pname = args.problem_name
        verboseprint(f'Preparing problem {pname}')
        problem_info = prepare_problem(args, s, pname)
    
    if args1.command == 'run':
        parser = argparse.ArgumentParser(description='Run the solution of a problem with the provided test cases')
        parser.add_argument('problem_name', type=str, help='Problem name')
        args2 = parser.parse_args(other1)
        for arg in vars(args2):
            setattr(args1, arg, getattr(args2, arg))
        args = args1
        pname = args.problem_name
        verboseprint(f'Running problem {pname} with the provided test cases')
        problem_info = interpret_solution(args, s, pname)

    if args1.command == 'submit':
        parser = argparse.ArgumentParser(description='Submit the solution of a problem')
        parser.add_argument('problem_name', type=str, help='Problem name')
        args2 = parser.parse_args(other1)
        for arg in vars(args2):
            setattr(args1, arg, getattr(args2, arg))
        args = args1
        pname = args.problem_name
        verboseprint(f'Submitting problem {pname}')
        submit_solution(args, s, pname)


    
    




    

