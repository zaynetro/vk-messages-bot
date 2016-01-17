from vk import Vk

"""
Vk user
"""

class Vk_user():
    def __init__(self, uid, first_name, last_name, photo_200):
        self.uid = uid
        self.first_name = first_name
        self.last_name = last_name
        self.photo = photo_200

    def get_name(self):
        return self.first_name + ' ' + self.last_name

    @staticmethod
    def from_token(access_token):
        return Vk_user.fetch_current_user(access_token)

    @staticmethod
    def from_api(token, params):
        users = Vk.api('users.get', token, params)
        if users == None:
            return None

        if len(users) == 0:
            return None

        return Vk_user(**users[0])

    @staticmethod
    def fetch_current_user(token):
        params = {'fields':'photo_200'}
        return Vk_user.from_api(token, params)

    @staticmethod
    def fetch_user(token, user_id):
        params = {'user_ids':user_id, 'fields':'photo_200'}
        return Vk_user.from_api(token, params)

    @staticmethod
    def empty():
        return Vk_user(0, 'Unresolved', 'Name', '')
