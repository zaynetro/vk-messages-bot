from vk import Vk
from vk_user import Vk_user
from constants import action, message
from telegram import Updater
import logging
from client import Client
from telegram.dispatcher import run_async
from db import db
from poller import Poller

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

class Bot:
    def __init__(self, token, vk_client_id):
        self.poller = Poller()
        self.updater = Updater(token=token)
        self.vk = Vk(vk_client_id)
        self.clients = Client.all_from_db()

        self.reg_actions()
        self.restore()

    def run(self):
        self.poller.async_run(self.on_update)
        self.updater.start_polling()
        self.updater.idle()
        self.poller.stop()
        self.persist()

    def persist(self):
        for _, client in self.clients.iteritems():
            client.persist()

    def restore(self):
        for _, client in self.clients.iteritems():
            self.add_poll_server(client)

    def reg_actions(self):
        dispatcher = self.updater.dispatcher
        dispatcher.addTelegramCommandHandler('start', self.start)
        dispatcher.addTelegramCommandHandler('whoami', self.whoami)
        dispatcher.addErrorHandler(self.error)
        dispatcher.addUnknownTelegramCommandHandler(self.unknown)
        dispatcher.addTelegramMessageHandler(self.on_message)

    def send(self, bot, update, text):
        bot.sendMessage(chat_id=update.message.chat_id, text=text)

    def start(self, bot, update):
        chat_id = update.message.chat_id
        auth_url = self.vk.get_auth_url()
        # Send first info messages
        self.send(bot, update, message.WELCOME(auth_url))
        self.send(bot, update, message.COPY_TOKEN)
        # Create new client
        client = Client(next_action=action.ACCESS_TOKEN,
                        chat_id=chat_id)
        self.clients[chat_id] = client
        client.persist()

    def whoami(self, bot, update):
        chat_id = update.message.chat_id
        if not chat_id in self.clients:
            return

        client = self.clients[chat_id]
        self.send(bot, update, message.WHOAMI(client.vk_user.get_name()))

    def error(self, bot, update, error):
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def on_message(self, bot, update):
        chat_id = update.message.chat_id

        if not chat_id in self.clients:
            return self.start(bot, update)

        client = self.clients[chat_id]
        client.seen_now()

        if client.next_action == action.ACCESS_TOKEN:
            return self.on_token_message(bot, update, client)

        self.echo(bot, update)

    def on_token_message(self, bot, update, client):
        client.load_vk_user(update.message.text)
        name = client.vk_user.get_name()
        client.next_action = action.NOTHING
        self.add_poll_server(client)
        self.send(bot, update, message.TOKEN_SAVED(name))

    @run_async
    def add_poll_server(self, client):
        if client.last_used_server != None:
            self.poller.add(client.last_used_server)
        else:
            server = Vk.get_long_poll_server(token=client.vk_token,
                                             chat_id=client.chat_id)
            self.poller.add(server)

    def echo(self, bot, update):
        self.send(bot, update, message.ECHO)

    def unknown(self, bot, update):
        self.send(bot, update, message.UNKNOWN)

    def on_update(self, updates, server):
        print str('Updates' + str(updates))
        for update in updates:
            self.process_update(update, server)

    def process_update(self, update, server):
        if len(update) == 0:
            return

        if update[0] == 4:
            # When new message received
            self.receive_vk_message(update, server)

    def receive_vk_message(self, update, server):
        chat_id = server.chat_id
        if not chat_id in self.clients:
            return

        client = self.clients[chat_id]
        client.last_used_server = server
        from_id = update[3]
        text = update[6]
        user = Vk_user.fetch_user(client.vk_token, from_id)
        self.updater.bot.sendMessage(chat_id=chat_id,
                text=message.NEW_MESSAGE(user.get_name(), text))
