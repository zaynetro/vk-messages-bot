import time
import jsonpickle
from vk_user import Vk_user
from db import db
import re

"""
Bot client
"""

class Client:
    def __init__(self, last_seen, next_action, chat_id):
        self.last_seen = last_seen
        self.next_action = next_action
        self.chat_id = chat_id
        self.vk_user = None
        self.vk_token = None

    def DB_KEY(self):
        return 'Client-' + str(self.chat_id)

    def seen_now(self):
        self.last_seen = time.time()

    def load_vk_user(self, vk_token):
        self.vk_token = vk_token
        if self.vk_user == None:
            user = Vk_user.fetch_current_user(vk_token)
            if user == None:
                user = Vk_user.empty()
            self.vk_user = user

    def to_json(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_json(json_str):
        return jsonpickle.decode(json_str)

    @staticmethod
    def create_now(next_action, chat_id):
        return Client(time.time(), next_action, chat_id)

    @staticmethod
    def all_from_db():
        all = db.getall()
        clients = dict()
        for client_key in all:
            if not re.match('Client-.+', client_key):
                continue

            client_json = db.get(client_key)
            client = Client.from_json(client_json)
            clients[client.chat_id] = client

        print 'Restored clients from db: ' + str(clients)
        return clients
