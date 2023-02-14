from CiCDTest import *
import demistomock as demisto
from CommonServerPython import *


def test_hello_user():
    assert hello_user("Daniel") == "Hello Daniel"


def test_good_bye_user():
    assert good_bye_user("John") == "Good Bye John"


def test_main(mocker):
    mocker.patch.object(demisto, "args", return_value={'user': 'Samuel'})
    return_result_mocker = mocker.patch("CiCDTest.return_results")
    main()
    return_result_mocker.assert_called_with("Hello Samuel")
