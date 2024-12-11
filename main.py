import argparse
from curl_cffi import requests
from utils import base_url, check_login
from problem import prepare_problem, interpret_solution, submit_solution

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LeetCode Companion')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print debug information')
    subparsers = parser.add_subparsers(help='commands', dest='command', required=True)
    prepare_parser = subparsers.add_parser('prepare', help='Prepare a problem')
    prepare_parser.add_argument('problem_name', type=str, help='Problem name')
    run_parser = subparsers.add_parser('run', help='Run the solution of a problem with the provided test cases')
    run_parser.add_argument('problem_name', type=str, help='Problem name')
    submit_parser = subparsers.add_parser('submit', help='Submit the solution of a problem')
    submit_parser.add_argument('problem_name', type=str, help='Problem name')
    args = parser.parse_args()
    s = requests.Session()
    res = check_login(args, s)
    if args.command == 'prepare':
        pname = args.problem_name
        print(f'Preparing problem {pname}')
        problem_info = prepare_problem(args, s, pname)
    elif args.command == 'run':
        pname = args.problem_name
        print(f'Running problem {pname} with the provided test cases')
        problem_info = interpret_solution(args, s, pname)
    elif args.command == 'submit':
        pname = args.problem_name
        print(f'Submitting problem {pname}')
        submit_solution(args, s, pname)
    else:
        raise ValueError('Invalid command')


    
    




    

