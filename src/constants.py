# Actions

def constant(f):
    def fset(self, value):
        raise TypeError

    def fget(self):
        return f()

    return property(fget, fset)

class _Action():
    @constant
    def NOTHING():
        return 'NOTHING'

    @constant
    def ACCESS_TOKEN():
        return 'ACCESS_TOKEN'

    @constant
    def RECEPIENT():
        return 'RECEPIENT'

    @constant
    def MESSAGE():
        return 'MESSAGE'

action = _Action()

class _Message():
    @staticmethod
    def WELCOME(link):
        return ('Yo, first we need to authorize vk app.\n'
                'First, generate access token by '
                'following the link: ' + link)

    @constant
    def COPY_TOKEN():
        return 'Now send generated access token from the url.'

    @staticmethod
    def TOKEN_SAVED(name):
        return ('Hey, ' + name + '! Your token was saved! '
                'Now you will start receiving messages.')

    @constant
    def ECHO():
        return 'I am just a machine.'

    @constant
    def UNKNOWN():
        return ('I have no clue about the command you specified. '
                'Where did you find it from?')

    @staticmethod
    def NEW_MESSAGE(sender, text):
        return sender + ': ' + text

    @staticmethod
    def WHOAMI(name):
        return 'You are ' + name

    @constant
    def TYPE_MESSAGE():
        return 'Type your message:'

message = _Message()
