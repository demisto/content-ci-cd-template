import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401


# import json
import urllib3
# import dateparser
import traceback
# from typing import Any, Dict, Tuple, List, Optional, Union, cast
from typing import Any, Dict

# Disable insecure warnings
urllib3.disable_warnings()


''' CONSTANTS '''


DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

''' CLIENT CLASS '''


class Client(BaseClient):
    """Client class to interact with the service API

    This Client implements API calls, and does not contain any Demisto logic.
    Should only do requests and return data.
    It inherits from BaseClient defined in CommonServer Python.
    Most calls use _http_request() that handles proxy, SSL verification, etc.
    For this MSSPortal implementation, no special attributes defined
    """

    def getCurrentUserIdentity(self) -> Dict[str, Any]:
        """Gets customer user's identity
        This methods will be used mainly to test API connectivity
        """

        return self._http_request('get', '/identities/current')

    def get_alert(self, id: str) -> Dict[str, Any]:
        """Gets a specific MSSPortal alert by id

        :type id: ``str``
        :param id: id of the alert to return

        :return: dict containing the alert as returned from the API
        :rtype: ``Dict[str, Any]``
        """

        return self._http_request('get', f'/alerts/{id}')

    def get_case(self, id: str) -> Dict[str, Any]:
        """Get a specific MSSPortal case by id

        :type id: ``str``
        :param id: id of the case to acknowledge

        :return: string from the API call
        :rtype: ``str``
        """

        return self._http_request('get', f'/cases/{id}')

    def find_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific MSSPortal case by id

        :return: string from the API call
        :rtype: ``str``
        """

        return self._http_request('get', '/tasks', json_data=data)

    def update_case(self, id: str, data: Dict[str, Any]) -> str:
        """Updates a specific MSSPortal case by id

        :type id: ``str``
        :param id: id of the case to update

        :return: string from the API call
        :rtype: ``str``
        """

        return self._http_request('put', f'/cases/{id}', json_data=data, resp_type='text')

    def acknowledge_case(self, id: str) -> str:
        """Acknowledge a specific MSSPortal case by id

        :type id: ``str``
        :param id: id of the case to acknowledge

        :return: string from the API call
        :rtype: ``str``
        """

        return self._http_request('put', f'/cases/{id}/acknowledgement', resp_type='text')

    def get_playbook(self, id: str) -> Dict[str, Any]:
        """Get a specific MSSPortal playbook by id

        :type id: ``str``
        :param id: id of the playbook

        :return: string from the API call
        :rtype: ``Dict[str, Any]``
        """

        return self._http_request('get', f'/playbooks/{id}')

    def find_playbook(self, searchParams: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific MSSPortal playbook by id

        :type data: ``Dict[str, Any]``
        :param data: search parameter values

        :return: string from the API call
        :rtype: ``Dict[str, Any]``
        """
        return self._http_request('get', '/playbooks', params=searchParams)

    def get_task(self, id: str) -> Dict[str, Any]:
        """Get a specific MSSPortal task by id

        :type id: ``str``
        :param id: id of the case to acknowledge

        :return: string from the API call
        :rtype: ``Dict[str, Any]``
        """

        return self._http_request('get', f'/tasks/{id}')

    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """create a MSSPortal task

        :type data: `Dict[str, Any]
        :param data: information to create task

        :return: string from the API call
        :rtype: ``Dict[str, Any]``
        """
        return self._http_request('post', '/tasks', json_data=data)

    def create_case(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a specific MSSPortal case

        :return: string from the API call
        :rtype: ``Dict[str, Any]``
        """
        return self._http_request('post', '/cases', json_data=data)

    def create_alert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gets a specific MSSPortal alert by id
        :type: dict containing the alert
        :param ``Dict[str, Any]``

        :return: dict containing the alert as returned from the API
        :rtype: ``Dict[str, Any]``
        """

        return self._http_request('post', '/alerts', json_data=data)

    def create_playbook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Gets a specific MSSPortal alert by id
        :type: dict containing the alert
        :param ``Dict[str, Any]``

        :return: dict containing the alert as returned from the API
        :rtype: ``Dict[str, Any]``
        """

        return self._http_request('post', '/playbooks', json_data=data)

    def resolve_case(self, id: str, data: Dict[str, Any]) -> str:
        """Resolve a MSSPortal case
        :type: dict containing the alert
        :param ``Dict[str, Any]``

        :return: dict containing the alert as returned from the API
        :rtype: ``str``
        """
        return self._http_request('put', f'/cases/{id}/resolution', json_data=data, resp_type='text')

    def confirm_incident(self, id: str) -> str:
        """confirms the case as a true incident

        :type id: ``str``
        :param id: id of the case to confirm as a true incident

        :return: string from the API call
        :rtype: ``str``
        """

        return self._http_request('put', f'/cases/{id}/incident', resp_type='text')

    def activate_playbook(self, caseId: str, playbookId: str, excludeTaskIds: str) -> str:
        """confirms the case as a true incident

        :type id: ``str``
        :param id: id of the case to confirm as a true incident

        :return: string from the API call
        :rtype: ``str``
        """
        data = []
        if excludeTaskIds:
            data = excludeTaskIds.replace(" ", "").split(",")

        return self._http_request('post', f'/cases/{caseId}/playbooks/{playbookId}', json_data=data, resp_type='text')


''' HELPER FUNCTIONS '''


''' COMMAND FUNCTIONS '''


def test_module(client: Client) -> str:
    """Tests API connectivity

    Returning 'ok' indicates that the integration works like it is supposed to.
    Connection to the service is successful.
    Raises exceptions if something goes wrong.

    :type client: ``Client``
    :param Client: MSSPortal client to use

    :type name: ``str``
    :param name: name to append to the 'Hello' string

    :return: 'ok' if test passed, anything else will fail the test.
    :rtype: ``str``
    """

    # INTEGRATION DEVELOPER TIP
    # Client class should raise the exceptions, but if the test fails
    # the exception text is printed to the Cortex XSOAR UI.
    # If you have some specific errors you want to capture (i.e. auth failure)
    # you should catch the exception here and return a string with a more
    # readable output (for example return 'Authentication Error, API Key
    # invalid').
    # Cortex XSOAR will print everything you return different than 'ok' as
    # an error
    try:
        client.getCurrentUserIdentity()
    except DemistoException as e:
        if 'Forbidden' in str(e):
            return 'Authorization Error: make sure API Key is correctly set'
        else:
            raise e
    return 'ok'


def get_alert_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-get-alert command: Returns a MSSPortal alert

    :type client: ``Client``
    :param Client: MSSPortal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['id']`` alert ID to return

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains an alert

    :rtype: ``CommandResults``
    """

    id = args.get('id', None)
    if not id:
        raise ValueError('id not specified')

    alert = client.get_alert(id)

    # tableToMarkdown() is defined is CommonServerPython.py and is used very
    # often to convert lists and dicts into a human readable format in markdown
    readable_output = tableToMarkdown(f'MSSPortal Alert {id}', alert)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='MSSPortal.Alert',
        outputs_key_field='id',
        outputs=alert
    )


def update_case_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-update-case command: Returns a MSSPortal case

    :type client: ``Client``
    :param Client: MSSPortal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['id']`` alert ID to return

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains the result of case update

    :rtype: ``CommandResults``
    """

    id = args.get('id', None)
    if not id:
        raise ValueError('id not specified')

    json_data: Dict[str, Any] = {}

    status = args.get('status')
    if not status:
        json_data['status'] = status
    telusPrime = args.get('telusPrime')
    if not status:
        json_data['telusPrime'] = telusPrime
    description = args.get('description')
    if not status:
        json_data['description'] = description
    caseTitle = args.get('caseTitle')
    if not status:
        json_data['caseTitle'] = caseTitle
    priority = args.get('priority')
    if not priority:
        json_data['priority'] = priority
    resolutionNotes = args.get('resolutionNotes')
    if not resolutionNotes:
        json_data['resolutionNotes'] = resolutionNotes

    client.update_case(id, json_data)

    return CommandResults(
        readable_output=f'MSSPortal Case {id} updated'
    )


def acknowledge_case_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-acknowledge-case command: change case status from pending to investigate

    :type client: ``Client``
    :param Client: MSSPortal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['id']`` case ID to return

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains the result of the case acknowledgement

    :rtype: ``CommandResults``
    """

    id = args.get('id', None)
    if not id:
        raise ValueError('id not specified')

    client.acknowledge_case(id)

    return CommandResults(
        readable_output=f'MSSPortal Case {id} acknowledged'
    )


def resolve_case_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-resolve-alert command: Returns a MSSPortal case

    :type client: ``Client``
    :param Client: MSSPortal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['id']`` case ID to return

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains an alert

    :rtype: ``CommandResults``
    """

    id = args.get('id', None)
    if not id:
        raise ValueError('id not specified')
    resolutionNotes = args.get('resolutionNotes', None)
    if not resolutionNotes:
        raise ValueError('resolutionNotes not specified')

    client.resolve_case(id, {"resolutionNotes": resolutionNotes})

    return CommandResults(
        readable_output=f'MSSPortal Case {id} resolved - {resolutionNotes}'
    )


def create_alert_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-get-alert command: Returns a MSSPortal alert

    :type client: ``Client``
    :param Client: MSSPortal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['alert_id']`` alert ID to return

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains an alert

    :rtype: ``CommandResults``
    """

    sourceId = args.get('sourceId')
    if not sourceId:
        raise ValueError('sourceId not specified')
    sourceCreatedAt = args.get('sourceCreatedAt')
    if not sourceCreatedAt:
        raise ValueError('sourceCreatedAt not specified')
    sourceModifiedAt = args.get('sourceModifiedAt')
    if not sourceModifiedAt:
        raise ValueError('sourceModifiedAt not specified')
    sourceAlertId = args.get('sourceAlertId')
    if not sourceAlertId:
        raise ValueError('sourceAlertId not specified')
    sourceRaw = args.get('sourceRaw', '{}')
    if not sourceRaw:
        raise ValueError('sourceRaw not specified')
    severity = args.get('severity')
    if not severity:
        raise ValueError('severity not specified')
    customerId = args.get('customerId',)
    if not customerId:
        raise ValueError('customerId not specified')
    investigationCaseId = args.get('investigationCaseId')
    name = args.get('name')
    if not name:
        raise ValueError('name not specified')

    json_data = {
        "sourceId": sourceId,
        "sourceCreatedAt": sourceCreatedAt,
        "sourceModifiedAt": sourceModifiedAt,
        "sourceAlertId": sourceAlertId,
        "sourceRaw": json.dumps(sourceRaw),
        "severity": severity,
        "customerId": customerId,
        "investigationCaseId": investigationCaseId,
        "name": name
    }

    caseDescription = args.get('caseDescription')
    if caseDescription:
        json_data['caseDescription'] = caseDescription
    caseTitle = args.get('caseTitle')
    if caseTitle:
        json_data['caseTitle'] = caseTitle
    detailHtml = args.get('detailHtml')
    if detailHtml:
        json_data['detailHtml'] = detailHtml

    alert = client.create_alert(json_data)

    # INTEGRATION DEVELOPER TIP
    # We want to convert the "created" time from timestamp(s) to ISO8601 as
    # Cortex XSOAR customers and integrations use this format by default

    # tableToMarkdown() is defined is CommonServerPython.py and is used very
    # often to convert lists and dicts into a human readable format in markdown

    readable_output = tableToMarkdown(f'MSSPortal Alert {alert["id"]}', alert)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='MSSPortal.Alert',
        outputs_key_field='id',
        outputs=alert
    )


def find_task_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-find-task command: Returns a MSSPortal task

     Args:
        client(Client): MSSPortal client to use
        task_id: task id
        name: name of the alert
        description: description of task
        caseId: case id
        accountable: Telus or customer
        phase: phase of task example: INVESTIGATE
        priority: priority of task (HIGH, MEDIUM, LOW)
        status: status of the task example: PENDING
        telusPrime: TELUS member accountable for task
        createdAt_from:
        createdAt_to: The creation time of the alert
        dueDate: due date of task
        customerId:
        caseTitle:
        searchText:
        resolvedAt_to:
        resolvedBy:
        sort:
        offset:
        limit:limit


    Returns:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains an alert


    Context Outputs:
        id (int): Alert ID.
        status(str): status of case example: PENDING


    """

    task_id = args.get('id')
    name = args.get('name')
    description = args.get('description')
    case_id = args.get('caseId')
    accountable = args.get('accountable')
    phase = args.get('phase')
    priority = args.get('priority')
    status = args.get('status')
    telusPrime = args.get('telusPrime')
    createdAt_from = args.get('createdAt_from')
    createdAt_to = args.get('createdAt_to')
    dueDate = args.get('dueDate')
    customerId = args.get('customerId')
    caseTitle = args.get('caseTitle')
    searchText = args.get('searchText')
    resolvedAt_to = args.get('resolvedAt_to')
    resolvedBy = args.get('resolvedBy')
    sort = args.get('sort')
    offset = args.get('offset')
    limit = args.get('limit')

    json_data = {
        "id": task_id,
        "name": name,
        'description': description,
        "caseId": case_id,
        "accountable": accountable,
        "phase": phase,
        "priority": priority,
        "status": status,
        "telusPrime": telusPrime,
        "createdAt_from": createdAt_from,
        "createdAt_to": createdAt_to,
        "dueDate": dueDate,
        "customerId": customerId,
        "caseTitle": caseTitle,
        "searchText": searchText,
        "resolvedAt_to": resolvedAt_to,
        "resolvedBy": resolvedBy,
        "sort": sort,
        "offset": offset,
        "limit": limit
    }

    tasks = client.find_task(json_data)

    readable_output = tableToMarkdown('MSSPortal Task founded', tasks)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='MSSPortal.Task',
        outputs_key_field='id',
        outputs=tasks
    )


def get_case_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-get-case command: Returns a MSSPortal case

    Args:
        client(Client): MSSPortal client to use
        id: Case ID to return

    Returns:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains an alert


    Context Outputs:
        id (int): Alert ID.
        status(str): status of case example: PENDING
        telusPrime(str): The Telus user accountable for the case
        description(str): The description of the case
        caseTitle(str): The caseTitle of the case
        priority(str): The priority of the case
        resolutionNotes(str): resolution notes
        customerId(int): The identifiant of the related customer
        caseSource(str): Indicate if is a Cortex case or created manually
        alertName(str): Description for Cortex created cases and Alert Name for manually created cases
        id(int): The identifiant of the case
        createdAt(date): the creation time of the case
        createdBy(str): The case creator
        updatedAt(date): The last modification time of the case
        updatedBy(str): The last case updator
        serviceComponent(str): The component of service for the case ex SOC
        incident(boolean) Indicates if the case has an incident (TRUE OR FALSE)
        incidentTime(date): The incident time of the case
        incidentBy(str): The user who set the case as incident
        nbTelusPendingTasks(int): Number of pending tasks accountable for TELUS
        nbTelusUnreadTaskComments(int): Number of task comments unread by TELUS
        nbCustomerClosedTasks(int): Number of closed tasks accountable for Customer
        nbCustomerTasks(int): Number of tasks accountable for Customer
        resolvedAt(date): Resolution time of the task
        resolvedBy(str):User who resolved the task
        sourceCreatedAt(date): The creation time from the source (optional)
        firstAcknowledgmentAt(date): The time of the first acknowledgement (optional)
        firstAssignmentAt(date): The time of the first assignment (optional)
        firstResolutionAt(date): The first resolution time
        firstCustomerTaskCreatedAt(date): The time the first customer task was created (optional)
        firstTelusTaskResolvedAt(date): The time the first TELUS task was resolved (optional)
        firstCustomerIncidentTaskCreatedAt(date): The time the first customer task was created (optional)
        firstTelusIncidentTaskResolvedAt(date): The time the first TELUS task was resolved after promoting as incident (optional)
    """

    id = args.get('id', None)
    if not id:
        raise ValueError('id not specified')

    case = client.get_case(id)

    # tableToMarkdown() is defined is CommonServerPython.py and is used very
    # often to convert lists and dicts into a human readable format in markdown
    readable_output = tableToMarkdown(f'MSSPortal Case {id}', case)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='MSSPortal.Case',
        outputs_key_field='id',
        outputs=case
    )


def find_playbook_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-find-playbook command: Returns MSSPortal playbook
    """

    searchParams = {}

    playbookId = args.get('playbookId')
    if playbookId:
        searchParams['playbookId'] = playbookId
    createdAt_from = args.get('createdAt_from')
    if createdAt_from:
        searchParams['createdAt_from'] = createdAt_from
    createdAt_to = args.get('createdAt_to')
    if createdAt_to:
        searchParams['createdAt_to'] = createdAt_to
    updatedAt_from = args.get('updatedAt_from')
    if updatedAt_from:
        searchParams['updatedAt_from'] = updatedAt_from
    updatedAt_to = args.get('updatedAt_to')
    if updatedAt_to:
        searchParams['updatedAt_to'] = updatedAt_to
    searchText = args.get('searchText')
    if searchText:
        searchParams['searchText'] = searchText
    sort = args.get('sort')
    if sort:
        searchParams['sort'] = sort
    offset = args.get('offset')
    if offset:
        searchParams['offset'] = offset
    limit = args.get('limit')
    if limit:
        searchParams['limit'] = limit

    playbooks = client.find_playbook(searchParams)

    readable_output = tableToMarkdown('MSSPortal Playbooks found', playbooks)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='MSSPortal.Playbook',
        outputs_key_field='id',
        outputs=playbooks
    )


def get_playbook_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-get-playbook command: Returns a MSSPortal playbook

    Args:
        client(Client): MSSPortal client to use
        id:  playbook ID to return

    Returns:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains an alert


    Context Outputs:
        id(int): Playbook id
        createdAt(date): The creation time
        createdBy(str): The principal who created
        updatedAt(date): The last modification time
        updatedBy(str): The principal who last modifed
        name(str): The name of the playbook
        description(str): The description of the playbook
        playbookTasks(unknown): undefined
    """

    id = args.get('id', None)
    if not id:
        raise ValueError('id not specified')

    playbook = client.get_playbook(id)

    # tableToMarkdown() is defined is CommonServerPython.py and is used very
    # often to convert lists and dicts into a human readable format in markdown
    readable_output = tableToMarkdown(f'MSSPortal Playbook {id}', playbook)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='MSSPortal.Playbook',
        outputs_key_field='id',
        outputs=playbook
    )


def create_playbook_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-create-playbook command: Returns a MSSPortal playbook

    Args:
        client(Client): MSSPortal client to use
        name: playbook name
        description: playbook description

    Returns:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains an alert

    Context Outputs:
        id(int): Playbook id
        createdAt(date): The creation time
        createdBy(str): The principal who created
        updatedAt(date): The last modification time
        updatedBy(str): The principal who last modified
        name(str): The name of the playbook
        description(str): The description of the playbook
        playbookTasks(unknown): undefined
    """
    name = args.get('name')
    description = args.get('description')

    json_data: Dict[str, Any] = {}

    json_data['name'] = name
    json_data['description'] = description

    playbook = client.create_playbook(json_data)

    readable_output = tableToMarkdown('MSSPortal Playbook', playbook)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='MSSPortal.Playbook',
        outputs_key_field='id',
        outputs=playbook
    )


def get_task_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-get-task command: Returns a MSSPortal task

    Args:
        client(Client): MSSPortal client to use
        id:  Task Id


    Returns:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains an alert
    Context Outputs:
        id(int): Playbook id
        name(str): name of the task
        description(str):description of the task
        caseId(int): case no.
        customerId(int): undefined
        accountable(string): who is accountable TELUS or customer
        status(str): status of task
        acknowledged(boolean): undefined
        priority(string): priority of task
        phase(str): undefined
        telusPrime(str): The Telus user accountable for the case
        dueDate(date): due date of case
        createdAt(date): time of creation
        createdBy(date): who created the task
        updatedAt(date): last updated
        updatedBy(date): undefined
        acknowledgedAt(string): undefined
        acknowledgedBy(string): undefined
        caseTitle(string): undefined
        abouttoExpireThresholdInDays(unknown)
        playbookName(str): name of playbook
        comments(undefined): undefined
        unreadCommentsByCustomer(int): no. of unread comments by customer
        unreadCommentsByTelus(int): no. of unread comments by TELUS
        modifiedbyTelus(boolean): notify customer when TELUS updates task (true or false)
        resolvedAt(date):  Resolution time of the task
        resolvedBy(str): undefined
    """

    id = args.get('id', None)
    if not id:
        raise ValueError('id not specified')
    task = client.get_task(id)

    # INTEGRATION DEVELOPER TIP
    # We want to convert the "created" time from timestamp(s) to ISO8601 as
    # Cortex XSOAR customers and integrations use this format by default

    # tableToMarkdown() is defined is CommonServerPython.py and is used very
    # often to convert lists and dicts into a human readable format in markdown

    readable_output = tableToMarkdown(f'MSSPortal Task {id}', task)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='MSSPortal.Task',
        outputs_key_field='id',
        outputs=task
    )


def create_task_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-create-task command: Returns a MSSPortal task

    Args:
        client(Client): MSSPortal client to use
        id:  Task Id
        name: Task name
        description: Task description
        caseId: Id of the case
        accountable: Telus user accountable for task example: TELUS
        telusPrime: The Telus user accountable for the case example: https://mssportal.telus.com/api/users/1
        priority: The priority of the task ex HIGH, MEDIUM, LOW
        phase: The phase of the task ex Investigate
        status: The status of the task ex pending
        dueDate: The due date of the task
        aboutToExpireThresholdInDays: The threshold in days to notify when task will expire
        modifiedByTelus: Should the customer be notified when TELUS modifies a task (ex false or true)

    Returns:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains an alert

    Context Outputs:
        id(int): Playbook id
        name(str): name of the task
        description(str): description of the task
        caseId(int): case no.
        customerId(int): undefined
        accountable(string): who is accountable TELUS or customer
        status(str): status of task
        acknowledged(boolean): undefined
        priority(string): priority of task
        phase(str): undefined
        telusPrime(str): The Telus user accountable for the case
        dueDate(date): due date of case
        createdAt(date): time of creation
        createdBy(date): who created the task
        updatedAt(date): last updated
        updatedBy(date): undefined
        acknowledgedAt(string): undefined
        acknowledgedBy(string): undefined
        caseTitle(string): undefined
        abouttoExpireThresholdInDays()
        playbookName(str): name of playbook
        comments(undefined): undefined
        unreadCommentsByCustomer(int): no. of unread comments by customer
        unreadCommentsByTelus(int): no. of unread comments by TELUS
        modifiedbyTelus(boolean): notify customer when TELUS updates task (true or false)
        resolvedAt(date):  Resolution time of the task
        resolvedBy(str): undefined


    """
    json_data = {}

    name = args.get('name')
    if name:
        json_data['name'] = name
    description = args.get('description')
    if description:
        json_data['description'] = description
    caseId = args.get('caseId')
    if caseId:
        json_data['caseId'] = caseId
    accountable = args.get('accountable')
    if accountable:
        json_data['accountable'] = accountable
    telusPrime = args.get("telusPrime")
    if telusPrime:
        json_data['telusPrime'] = telusPrime
    status = args.get("status")
    if status:
        json_data['status'] = status
    phase = args.get("phase")
    if description:
        json_data['phase'] = phase
    dueDate = args.get('dueDate')
    if dueDate:
        json_data['dueDate'] = dueDate
    aboutToExpireThresholdInDays = args.get('aboutToExpireThresholdInDays')
    if aboutToExpireThresholdInDays:
        json_data['aboutToExpireThresholdInDays'] = aboutToExpireThresholdInDays
    modifiedByTelus = args.get('modifiedByTelus')
    if modifiedByTelus:
        json_data['modifiedByTelus'] = modifiedByTelus

    task = client.create_task(json_data)

    readable_output = tableToMarkdown(f'MSSPortal Task {task["id"]}', task)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='MSSPortal.Task',
        outputs_key_field='id',
        outputs=task
    )


def create_case_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-get-alert command: Returns a MSSPortal alert

    Args:
        client(Client): MSSPortal client to use
        status: customer ID to return
        telusPrime: Telus user accountable for case
        description: description of case
        caseTitle: Title of case
        priority: Priority of case (HIGH, MEDIUM, LOW)
        resolutionNotes: resolution notes of the case
        customerId
        caseSource
        alertName
        serviceComponent


    Returns:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains an alert

    Context Outputs:
        status(str): status of case
        telusPrime(str): telus user accountable for case
        description(str): description of case
        caseTitle(str): title of case
        priority(str): severity of case (HIGH, MEIDUM, LOW )
        resolutionNotes(str): resolution notes
        customerId(unknown): undefined
        caseSource(unknown): undefined
        alertName(str): undefined
        id(int): id of case
        createdAt(date): date of creation
        createdBy(str): who created the case
        updatedAt(date): modification date
        updatedBy(str): undefined
        serviceComponent(unknown): undefined
        incident(boolean): true incident (true or false)
        incidentTime(date): undefined
        nbTelusPendingTasks(int): no. of pending tasks for TELUS
        nbTelusUnreadTaskComments(int): no. of unread tasks
        nbCustomerClosedTasks(int): closed customer tasks
        nbCustomerTasks(Int): tasks customer responsible for
        resolvedAt(date): undefined
        resolvedBy(str): undefined
        sourceCreatedAt(date): undefined
        firstAcknowledgmentAt(date): undefined
        firstAssignmentAt(date): undefined
        firstResolutionAt(unknown): undefined
        firstCustomerTaskCreatedAt(unknown): undefined
        firstTelusTaskResolvedAt(unknown): undefined
        firstCustomerIncidentTaskCreatedAt(unknown): undefined
        firstTelusIncidentTaskResolvedAt(unknown): undefined
    """

    description = args.get('description', None)
    if not description:
        raise ValueError('description not specified')
    caseTitle = args.get('caseTitle', None)
    if not description:
        raise ValueError('caseTitle not specified')
    priority = args.get('priority', None)
    if not description:
        raise ValueError('priority not specified')
    customerId = args.get('customerId', None)
    if not description:
        raise ValueError('customerId not specified')
    caseSource = args.get('caseSource', None)
    if not description:
        raise ValueError('caseSource not specified')
    serviceComponent = args.get('serviceComponent', None)
    if not description:
        raise ValueError('serviceComponent not specified')

    json_data = {
        'description': description,
        'caseTitle': caseTitle,
        'priority': priority,
        'customerId': customerId,
        'caseSource': caseSource,
        'serviceComponent': serviceComponent
    }

    status = args.get('status')
    if status:
        json_data['status'] = status
    telusPrime = args.get('telusPrime')
    if status:
        json_data['telusPrime'] = telusPrime
    resolutionNotes = args.get('resolutionNotes')
    if resolutionNotes:
        json_data['resolutionNotes'] = resolutionNotes
    alertName = args.get('alertName')
    if alertName:
        json_data['alertName'] = alertName

    case = client.create_case(json_data)

    # INTEGRATION DEVELOPER TIP
    # We want to convert the "created" time from timestamp(s) to ISO8601 as
    # Cortex XSOAR customers and integrations use this format by default

    # tableToMarkdown() is defined is CommonServerPython.py and is used very
    # often to convert lists and dicts into a human readable format in markdown

    readable_output = tableToMarkdown(f'MSSPortal Case {case["id"]}', case)

    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='MSSPortal.Case',
        outputs_key_field='id',
        outputs=case
    )


def confirm_incident_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-confirm-incident command: confirms the case as a true incident

    :type client: ``Client``
    :param Client: MSSPortal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['id']`` case ID to return

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains the result of the case acknowledgement

    :rtype: ``CommandResults``
    """

    id = args.get('id', None)
    if not id:
        raise ValueError('id not specified')

    client.confirm_incident(id)

    return CommandResults(
        readable_output=f'MSSPortal Case {id} confirmed as a true incident'
    )


def activate_playbook_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """mssportal-activate-playbook command: activate the playbook in the case

    :type client: ``Client``
    :param Client: MSSPortal client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['caseId']`` case ID to in which the playbook will be activated
        ``args['playbookId']`` playbook ID to activate in the case

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains the result of the case acknowledgement

    :rtype: ``CommandResults``
    """

    caseId = args.get('caseId', None)
    if not caseId:
        raise ValueError('caseId not specified')
    playbookId = args.get('playbookId', None)
    if not playbookId:
        raise ValueError('playbookId not specified')
    excludeTaskIds = args.get('excludeTaskIds', None)

    client.activate_playbook(caseId, playbookId, excludeTaskIds)

    return CommandResults(
        readable_output=f'MSSPortal playbook {playbookId} was activated in the case {playbookId}'
    )


''' MAIN FUNCTION '''


def main() -> None:
    """main function, parses params and runs command functions

    :return:
    :rtype:
    """

    api_key = demisto.params().get('api_key')

    # get the service API url
    base_url = urljoin(demisto.params()['url'], '/api/v1')

    # if your Client class inherits from BaseClient, SSL verification is
    # handled out of the box by it, just pass ``verify_certificate`` to
    # the Client constructor
    verify_certificate = not demisto.params().get('insecure', True)

    # if your Client class inherits from BaseClient, system proxy is handled
    # out of the box by it, just pass ``proxy`` to the Client constructor
    proxy = demisto.params().get('proxy', False)

    # INTEGRATION DEVELOPER TIP
    # You can use functions such as ``demisto.debug()``, ``demisto.info()``,
    # etc. to print information in the XSOAR server log. You can set the log
    # level on the server configuration
    # See: https://xsoar.pan.dev/docs/integrations/code-conventions#logging

    demisto.debug(f'Command being called is {demisto.command()}')
    try:
        headers = {
            'X-Lestrade-Key-ID': 'xsoar',
            'X-Lestrade-Key': api_key
        }
        client = Client(
            base_url=base_url,
            verify=verify_certificate,
            headers=headers,
            proxy=proxy)

        if demisto.command() == 'test-module':
            # This is the call made when pressing the integration Test button.
            result = test_module(client)
            return_results(result)

        elif demisto.command() == 'mssportal-get-alert':
            return_results(get_alert_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-create-alert':
            return_results(create_alert_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-get-case':
            return_results(get_case_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-update-case':
            return_results(update_case_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-acknowledge-case':
            return_results(acknowledge_case_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-confirm-incident':
            return_results(confirm_incident_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-create-case':
            return_results(create_case_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-resolve-case':
            return_results(resolve_case_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-get-playbook':
            return_results(get_playbook_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-find-playbook':
            return_results(find_playbook_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-create-playbook':
            return_results(create_playbook_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-activate-playbook':
            return_results(activate_playbook_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-get-task':
            return_results(get_task_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-create-task':
            return_results(create_task_command(client, demisto.args()))
        elif demisto.command() == 'mssportal-find-tasks':
            return_results(find_task_command(client, demisto.args()))

    # Log exceptions and return errors
    except Exception as e:
        demisto.error(traceback.format_exc())  # print the traceback
        return_error(f'Failed to execute {demisto.command()} command.\nError:\n{str(e)}')


''' ENTRY POINT '''

if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
