# atcoder-grader
A tool to automate downloading test cases from AtCoder (Dropbox)and testing your python program locally


## Why this tool?
I am always a fan of allowing third-party libraries such as numpy and networkx in Competitive Programming. I strongly believe that using additional libraries with strengthen one's ability not only in general problem solving but in software engineering as well. But you know what, the community does not seem to appreciate this idea. Hence there is no judge around with support for this fantastic idea. That's why I created this tool, which at least allows me to do that locally.

## Usage
Installing whatever libraries of your choice in your local environment (with venv for now). 

Putting the pygrader script in the same directory.

Run it in the following syntax
```bash
>>>  python pygrader.py --program=program.py --contest=arc090 --problem=D --token=<Your Dropbox Access Token>
```
It will automatically download (to /tmp) and test your program.py.
