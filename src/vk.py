import string
import requests
from collections import namedtuple

LongPollServer = namedtuple('LongPollServer', 'server key ts chat_id')

class Vk():
    def __init__(self, client_id):
        self._client_id = client_id

    @staticmethod
    def AUTH_URL(params):
        return string.Template(
                'https://oauth.vk.com/authorize'
                '?client_id=$client_id'
                '&display=page'
                '&scope=messages,offline'
                '&response_type=token'
                '&v=5.44').substitute(params)

    @staticmethod
    def API_URL(method):
        return 'https://api.vk.com/method/' + method

    @staticmethod
    def api(method, token, params=dict()):
        params = params.copy()
        params['access_token'] = token
        r = requests.get(Vk.API_URL(method), params=params)
        if r.status_code != requests.codes.ok:
            return None

        json = r.json()
        print('VK api response: ' + str(json))

        if 'response' in json:
            return json['response']

        return None

    def get_auth_url(self):
        params = { 'client_id':self._client_id }
        return Vk.AUTH_URL(params)

    @staticmethod
    def get_long_poll_server(token, chat_id):
        method = 'messages.getLongPollServer'
        server = Vk.api(method, token)
        if server == None:
            return None

        return LongPollServer(server['server'], server['key'],
                              server['ts'], chat_id)

    @staticmethod
    def poll(client, retry=True):
        server, key, ts, chat_id = client.next_server
        url = 'http://' + server
        params = {'key':key, 'ts':ts, 'wait': 25, 'act':'a_check', 'mode':2}
        r = requests.get(url, params=params)
        if r.status_code != requests.codes.ok:
            return None
            next_server = Vk.get_long_poll_server(token=client.vk_token,
                    chat_id=client.chat_id)
            if next_server == None:
                return None

            client.next_server = next_server
            if retry:
                return Vk.poll(client, retry=False)
            else:
                return None

        json = r.json()
        print("Poll results: " + str(json))
        if 'failed' in json:
            return None
            next_server = Vk.get_long_poll_server(token=client.vk_token,
                    chat_id=client.chat_id)
            if next_server == None:
                return None

            client.next_server = next_server
            if retry:
                return Vk.poll(client, retry=False)
            else:
                return None

        next_server = LongPollServer(server, key, json['ts'], chat_id)
        client.next_server = next_server
        return json['updates']

