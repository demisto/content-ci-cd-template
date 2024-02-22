import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401


def main():
    res = demisto.executeCommand('URLDecode', {'value': 'https://www.paloaltonetworks.com/'})
    return_results(res)
    return_results(CommandResults(readable_output='hello there'))


if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
