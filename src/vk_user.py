from vk import Vk
from db import db
import time
import jsonpickle

"""
Vk user
"""

class Vk_user():
    def __init__(self,
                 uid=None,
                 first_name='Unresolved',
                 last_name='Name',
                 photo_400_orig=None,
                 created_at=time.time()):

        self.uid = uid
        self.first_name = first_name
        self.last_name = last_name
        self.photo = photo_400_orig
        self.created_at = created_at

    def __hash__(self):
        return self.uid

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def db_key(self):
        return Vk_user.DB_KEY(self.uid)

    @staticmethod
    def DB_KEY(uid):
        return 'VK-USER-' + str(uid)

    def should_fetch(self):
        return self.uid == None or self.outdated()

    def get_name(self):
        return self.first_name + ' ' + self.last_name

    def send_message(self, token, message):
        params = {'user_id': self.uid, 'message':message}
        message_id = Vk.api('messages.send', token, params)

    def outdated(self):
        one_week = 60*24*7
        return self.created_at < time.time() - one_week

    def to_json(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_json(json_str):
        return jsonpickle.decode(json_str)

    @staticmethod
    def from_api(token, params):
        users = Vk.api('users.get', token, params)
        if users == None:
            return Vk_user()

        if len(users) == 0:
            return Vk_user()

        user = Vk_user(**users[0])
        db.set(user.db_key(), user.to_json())
        return user

    @staticmethod
    def fetch_current_user(token):
        params = {'fields':'photo_400_orig'}
        return Vk_user.from_api(token, params)

    @staticmethod
    def fetch_user(token, user_id):
        user_json = db.get(Vk_user.DB_KEY(user_id))
        if user_json != None:
            user = Vk_user.from_json(user_json)
            if not user.outdated:
                return user

        params = {'user_ids':user_id, 'fields':'photo_400_orig'}
        return Vk_user.from_api(token, params)
