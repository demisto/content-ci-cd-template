import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401

def hello_user(user):
    return "Hello {}".format(user)

def main():
    args = demisto.args()
    user = args.get("user")
    return_results(hello_user(user))
    
if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()