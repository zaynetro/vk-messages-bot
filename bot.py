from vk import Vk
from vk_user import Vk_user
from constants import action, message
from telegram import Updater
import logging
from client import Client
from telegram.dispatcher import run_async
from db import db

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

class Bot:
    def __init__(self, poller, token, vk_client_id):
        self.poller = poller
        self.updater = Updater(token=token)
        self.reg_actions()
        self.vk = Vk(vk_client_id)
        self.clients = Client.all_from_db()
        for _, client in self.clients.iteritems():
            self.add_poll_server(client)

    def run(self):
        self.poller.async_run(self.on_update)
        self.updater.start_polling()
        self.updater.idle()
        self.poller.stop()
        for _, client in self.clients.iteritems():
            db.set(client.DB_KEY(), client.to_json())
        db.dump()

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
        client = Client.create_now(action.ACCESS_TOKEN, chat_id)
        self.clients[chat_id] = client
        db.set(client.DB_KEY(), client.to_json())

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
            client.load_vk_user(update.message.text)
            name = client.vk_user.get_name()
            client.next_action = action.NOTHING
            self.add_poll_server(client)
            return self.send(bot, update, message.TOKEN_SAVED(name))

        return self.echo(bot, update)

    @run_async
    def add_poll_server(self, client):
        server = Vk.get_long_poll_server(client.vk_token, client.chat_id)
        self.poller.add(server)

    def echo(self, bot, update):
        self.send(bot, update, message.ECHO)

    def unknown(self, bot, update):
        self.send(bot, update, message.UNKNOWN)

    def on_update(self, updates, chat_id):
        print str('Updates' + str(updates))
        for update in updates:
            self.process_update(update, chat_id)

    def process_update(self, update, chat_id):
        if len(update) == 0:
            return

        if update[0] == 4:
            # When new message received
            self.receive_vk_message(update, chat_id)

    def receive_vk_message(self, update, chat_id):
        if not chat_id in self.clients:
            return

        client = self.clients[chat_id]
        from_id = update[3]
        text = update[6]
        user = Vk_user.fetch_user(client.vk_token, from_id)
        self.updater.bot.sendMessage(chat_id=chat_id,
                text=message.NEW_MESSAGE(user.get_name(), text))
