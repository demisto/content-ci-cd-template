import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401
res = demisto.executeCommand("Print", {"value": "Samuel"})
return_results(res)
