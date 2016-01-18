import time
import jsonpickle
from vk_user import Vk_user
from db import db
import re
from constants import action

"""
Bot client
"""

class Client:
    def __init__(self,
                 last_seen=time.time(),
                 next_action=action.NOTHING,
                 chat_id=None):

        self.last_seen = last_seen
        self.next_action = next_action
        self.chat_id = chat_id
        self.vk_user = Vk_user()
        self.vk_token = None
        self.last_used_server = None

    def db_key(self):
        return 'Client-' + str(self.chat_id)

    def persist(self):
        db.set(self.db_key(), self.to_json())
        db.dump()

    def seen_now(self):
        self.last_seen = time.time()

    def load_vk_user(self, vk_token):
        self.vk_token = vk_token
        if self.vk_user.should_fetch():
            user = Vk_user.fetch_current_user(vk_token)
            if user != None:
                self.vk_user = user

    def to_json(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_json(json_str):
        return jsonpickle.decode(json_str)

    @staticmethod
    def all_from_db():
        all = db.getall()
        clients = dict()
        for client_key in all:
            if not re.match('Client-.+', client_key):
                continue

            client_json = db.get(client_key)
            client = Client.from_json(client_json)
            if client.vk_user.should_fetch():
                client.load_vk_user(client.vk_token)

            clients[client.chat_id] = client

        print 'Restored clients from db: ' + str(clients)
        return clients
