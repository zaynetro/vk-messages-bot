import re
import time

import jsonpickle

from vk_messages_bot import db
from vk_messages_bot.constants import action
from vk_messages_bot.vk_user import Vk_user

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
        self.next_server = None
        self.interacted_with = set()  # set of chats or users
        self.next_recepient = None

    def db_key(self):
        return 'Client-' + str(self.chat_id)

    def persist(self):
        self.seen_now()
        db.set(self.db_key(), self.to_json())
        db.sync()

    def seen_now(self):
        self.last_seen = time.time()

    def load_vk_user(self, vk_token):
        self.vk_token = vk_token
        if self.vk_user.should_fetch():
            user = Vk_user.fetch_current_user(vk_token)
            if user != None:
                self.vk_user = user

    def keyboard_markup(self):
        if self.next_action == action.MESSAGE:
            return self.picked_keyboard()

        return [['/pick ' + user.get_name()]
                for user in self.interacted_with
                if not user.should_fetch()]

    def picked_keyboard(self):
        return [['/unpick ' + self.next_recepient.get_name()],
                ['/details']]

    def expect_message_to(self, to_name):
        self.next_recepient = next((u for u in self.interacted_with
                                    if u.get_name() == to_name), None)
        if self.next_recepient != None:
            self.next_action = action.MESSAGE
        self.persist()

    def send_message(self, text):
        if self.next_recepient == None:
            return

        self.next_recepient.send_message(self.vk_token, text)

    def add_interaction_with(self, user):
        if user.empty():
            return

        self.interacted_with.add(user)

    def to_json(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_json(json_str):
        return jsonpickle.decode(json_str)

    @staticmethod
    def all_from_db():
        clients = dict()
        for client_key in db.dict():
            if not re.match('Client-.+', client_key):
                continue

            client_json = db.get(client_key)
            client = Client.from_json(client_json)
            if client.vk_user.should_fetch():
                client.load_vk_user(client.vk_token)

            clients[client.chat_id] = client

        print('Restored clients from db: ' + str(clients))
        return clients
