from CiCDTestScript import main, hello_user
import demistomock as demisto


def test_main(mocker):
    mocker.patch.object(demisto, 'args', return_value={"user": "Daniel"})
    return_mocker = mocker.patch("CiCDTestScript.return_results")
    main()
    return_mocker.assert_called_with("Hello Daniel")


def test_hello_user():
    assert hello_user('Daniel') == 'Hello Daniel'