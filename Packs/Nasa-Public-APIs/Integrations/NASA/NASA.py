import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401


class Client(BaseClient):
    def __init__(self, base_url: str, api_key: str):
        super().__init__(base_url=base_url)
        self.api_key = api_key

    def apod_request(self, data):
        data["api_key"] = self.api_key
        return self._http_request(method='GET', url_suffix='planetary/apod', params=data, ok_codes=(200,))

    def neo_feed_request(self, data):
        data["api_key"] = self.api_key
        return self._http_request(method='GET', url_suffix='neo/rest/v1/feed', params=data, ok_codes=(200,))


def test_module(client: Client) -> str:
    data = {}
    try:
        # Testing abod method
        abod_res = client.apod_request(data)
        test_abod_status = demisto.get(abod_res, "copyright")

        # Testing neo feed method
        neo_res = client.neo_feed_request(data)
        test_neo_status = demisto.get(neo_res, 'element_count')

        if test_abod_status and test_neo_status:
            return 'ok'
        else:
            return f'Test failed. Expected a for the image generated. Received {test_status}'

    except Exception as e:
        raise e


def create_abod_entry(response):

    title = demisto.get(response, "title")
    image = demisto.get(response, "url")
    details = demisto.get(response, "explanation")
    content = {"Title": title, "Image": image, "Details": details}
    md = f'{title}|\n|-----------------|\n|![]({image})|\n|{details}|\n'

    entry = {'Type': entryTypes['image'],
             'ContentsFormat': formats['markdown'],
             'Contents': content,
             'HumanReadable': md,
             'ReadableContentsFormat': formats['markdown']}

    return entry


def apod_get_image(client: Client, data):

    try:
        response = client.apod_request(data)
    except Exception as e:
        raise(f"Error running command. Encounted error {e}")

    if type(response) != list:
        output = create_abod_entry(response)
    else:
        output = []
        for items in response:
            entry = create_abod_entry(items)
            output.append(entry)

    return output


def get_neo_feed(client, data):

    try:
        response = client.neo_feed_request(data)
        count_of_elements = demisto.get(response, "element_count")
        main_output = demisto.get(response, "near_earth_objects")
        link = str(demisto.get(response, "links").get('self'))
        dates = re.search(r"(start_date=[0-9]{4}-[0-9]{2}-[0-9]{2})&(end_date=[0-9]{4}-[0-9]{2}-[0-9]{2})", link)
        start_date = dates.group(1).split('=')[1]
        end_date = dates.group(2).split('=')[1]

        content = {}
        md = f"## Total of {count_of_elements} Space Objects are approaching Earth between {start_date} to {end_date}\n|ID|Name|Minimum Diameter|Maximum Diameter|Close Approach Date|\n|-|-|-|-|-|\n"

        for dates, items in main_output.items():
            if items:
                for near_earth_obj in items:
                    obj_id = near_earth_obj.get('id')
                    obj_name = near_earth_obj.get('name').strip('()')
                    obj_min_diameter = near_earth_obj.get('estimated_diameter').get('feet').get('estimated_diameter_min')
                    obj_max_diameter = near_earth_obj.get('estimated_diameter').get('feet').get('estimated_diameter_max')
                    obj_close_aproach_date = near_earth_obj.get('close_approach_data')[0].get('close_approach_date_full')
                    content[obj_id] = {"id": obj_id, "name": obj_name, "min_dia": str(obj_min_diameter) + ' ft', "max_dia": str(obj_max_diameter) + ' ft',
                                       "close_date": obj_close_aproach_date}

        for items, ch_obj in content.items():
            md += f'|{ch_obj["id"]}|{ch_obj["name"]}|{ch_obj["min_dia"]}|{ch_obj["max_dia"]}|{ch_obj["close_date"]}|\n'

        entry = {'Type': entryTypes['note'], 'Contents': content, 'ContentsFormat': formats['json'],
                 'HumanReadable': md, 'ReadableContentsFormat': formats['markdown']}
    except Exception as e:
        return (f"An error occured during command execution. {str(e)}")
    return entry


def main():
    args = demisto.args()
    params = demisto.params()
    command = demisto.command()

    api_key = params.get('apikey')
    base_url = params.get('url')

    demisto.debug(f'Command being called is {command}')

    try:
        client = Client(base_url, api_key)

        if command == 'test-module':
            return_results(test_module(client))

        elif command == 'nasa-abod-get-Image':
            return_results(apod_get_image(client, args))
        elif command == 'nasa-neo-feed':
            return_results(get_neo_feed(client, args))
        else:
            raise NotImplementedError(f"command {command} is not implemented.")

    except Exception as e:
        demisto.error(traceback.format_exc())
        return_error("\n".join((f"Failed to execute {command} command.",
                                "Error:",
                                str(e))))


if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
