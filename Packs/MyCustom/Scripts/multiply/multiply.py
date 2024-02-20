import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401, F403


''' COMMAND FUNCTION '''

def multiply(args: dict):
    value = args["value"]
    multiply = args["multiply"]
    return value * multiply


''' MAIN FUNCTION '''


def main():
    try:
        args = demisto.args()
        return_results(multiply(args))
    except Exception as ex:
        return_error(f'Failed to execute BaseScript. Error: {str(ex)}')


''' ENTRY POINT '''


if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()

