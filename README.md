# LeetCode Companion

Ever wanted to solve [LeetCode](https://leetcode.com/) problems with your favourite IDE? This project is for you!

## Quickstart
* Install [curl-impersonate](https://github.com/lwthiker/curl-impersonate). You can download the binaries from the [releases page](https://github.com/lwthiker/curl-impersonate/releases) and place them, for example, in `/usr/local/bin/`.

* Install the required dependencies:
```bash
sudo apt-get install python3 python3-pip
pip3 install -r requirements.txt
```

* Run the following command to prepare the problem:
```bash
python3 main.py prepare <problem_name>
```
where `<problem_name>` is the name of the problem you want to solve. For example, to prepare the problem [Merge Sorted Array](https://leetcode.com/problems/merge-sorted-array/), you would run:
```bash
python3 main.py prepare merge-sorted-array
```
You can find the problem name in the URL of the problem. For example, the URL of the problem [Merge Sorted Array](https://leetcode.com/problems/merge-sorted-array/) is `https://leetcode.com/problems/merge-sorted-array/`, so the problem name is `merge-sorted-array`.

Firstly, the script main.py will ask to login to your LeetCode account. Your browser is opened automatically to the login page of LeetCode. After logging in, press F12 to open the developer tools, go to the Application tab, click on "https://leetcode.com" under "Cookies" and copy the value of the `LEETCODE_SESSION` cookie. Paste this value into the terminal and press Enter.

A directory named `merge-sorted-array` will be created in the `problems` directory. Inside this folder, you will find the following files:
  1. `README.md`: The problem statement.
  2. `solution.py`: The solution template.
  3. `testcases.json`: The testcases for the problem.

* Open the `solution.py` file in your favourite IDE and start solving the problem! You can also debug your solution through the IDE.

* Run the following command to test your solution on the LeetCode server with the testcases provided by LeetCode:
```bash
python3 main.py run <problem_name>
```

* If you want to submit your solution, run the following command:
```bash
python3 main.py submit <problem_name>
```

## Limitations
* This project only supports Python 3. Maybe in the future, we will support other languages.
* The supported system is Linux. We have not tested this project on other systems.



