import logging
from urllib.parse import urlparse, parse_qs, urljoin

from telegram import ParseMode, ReplyKeyboardHide, ReplyKeyboardMarkup
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async

from vk_messages_bot import db
from vk_messages_bot.client import Client
from vk_messages_bot.constants import action, message
from vk_messages_bot.poller import Poller
from vk_messages_bot.vk import Vk
from vk_messages_bot.vk_chat import Vk_chat
from vk_messages_bot.vk_user import Vk_user

logger = logging.getLogger(__name__)


class Bot:
    def __init__(self, tg_bot_token, vk_client_id):
        self.tg_bot_token = tg_bot_token
        self.poller = Poller()
        self.vk = Vk(vk_client_id)
        self.clients = Client.all_from_db()

        self.updater = Updater(token=tg_bot_token)
        dispatcher = self.updater.dispatcher

        start_command_handler = CommandHandler('start', self.start_command_callback)
        dispatcher.add_handler(start_command_handler)
        start_command_handler = CommandHandler('whoami', self.whoami_command_callback)
        dispatcher.add_handler(start_command_handler)
        start_command_handler = CommandHandler('pick', self.pick_command_callback)
        dispatcher.add_handler(start_command_handler)
        start_command_handler = CommandHandler('unpick', self.unpick_command_callback)
        dispatcher.add_handler(start_command_handler)
        start_command_handler = CommandHandler('details', self.details_command_callback)
        dispatcher.add_handler(start_command_handler)
        unknown_handler = MessageHandler(Filters.command, self.unknown_command_callback)
        dispatcher.add_handler(unknown_handler)
        message_handler = MessageHandler(Filters.text, self.message_callback)
        dispatcher.add_handler(message_handler)
        dispatcher.add_error_handler(self.error_callback)

        self.restore()

    def start(self, use_webhook=False, app_url=None, app_port=None):
        self.poller.async_run(self.on_update)

        if use_webhook:
            url_path = self.tg_bot_token.replace(":", "")
            self.updater.start_webhook(listen="0.0.0.0",
                                       port=app_port,
                                       url_path=url_path)
            self.updater.bot.set_webhook(urljoin(app_url, url_path))
        else:
            self.updater.start_polling()
        self.updater.idle()

        self.poller.stop()
        self.persist()
        db.close()

    def persist(self):
        for _, client in self.clients.items():
            client.persist()

    def restore(self):
        for _, client in self.clients.items():
            self.add_poll_server(client)


    def start_command_callback(self, bot, update):
        chat_id = update.message.chat_id
        auth_url = self.vk.get_auth_url()
        # Send first info messages
        bot.sendMessage(chat_id=chat_id,
                        text=message.WELCOME(auth_url),
                        reply_markup=ReplyKeyboardHide())
        bot.sendMessage(chat_id=chat_id, text=message.COPY_TOKEN)
        # Create new client
        client = Client(next_action=action.ACCESS_TOKEN,
                        chat_id=chat_id)
        self.clients[chat_id] = client
        client.persist()

    def whoami_command_callback(self, bot, update):
        chat_id = update.message.chat_id
        if not chat_id in self.clients:
            return

        client = self.clients[chat_id]
        bot.sendMessage(chat_id=chat_id,
                        text=message.WHOAMI(client.vk_user.get_name()),
                        reply_markup=Bot.keyboard(client.keyboard_markup()))

    def pick_command_callback(self, bot, update):
        chat_id = update.message.chat_id
        if not chat_id in self.clients:
            self.start_command_callback(bot, update)
            return

        client = self.clients[chat_id]
        client.seen_now()
        recepient = update.message.text[6:]
        client.expect_message_to(recepient)
        bot.sendMessage(chat_id=chat_id,
                        text=message.TYPE_MESSAGE(recepient),
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=Bot.keyboard(client.keyboard_markup()))

    def unpick_command_callback(self, bot, update):
        chat_id = update.message.chat_id
        if not chat_id in self.clients:
            self.start_command_callback(bot, update)
            return

        client = self.clients[chat_id]
        client.next_action = action.NOTHING
        client.persist()
        bot.sendMessage(chat_id=chat_id,
                        text=message.UNPICK(client.next_recepient.get_name()),
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=Bot.keyboard(client.keyboard_markup()))
        client.next_recepient = None

    def details_command_callback(self, bot, update):
        chat_id = update.message.chat_id
        if not chat_id in self.clients:
            self.start_command_callback(bot, update)
            return

        client = self.clients[chat_id]
        client.seen_now()
        user = client.next_recepient
        if user == None:
            bot.sendMessage(chat_id=chat_id,
                            text=message.FIRST_PICK_USER,
                            reply_markup=Bot.keyboard(client.keyboard_markup()))
            return

        if user.photo != None:
            bot.sendPhoto(chat_id=chat_id, photo=user.photo)

        bot.sendMessage(chat_id=chat_id,
                        text=message.USER_NAME(user.get_name()),
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=Bot.keyboard(client.keyboard_markup()))

        participants = user.participants()
        if participants != None:
            bot.sendMessage(chat_id=chat_id,
                            text=message.PARTICIPANTS(participants),
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=Bot.keyboard(client.keyboard_markup()))

    def unknown_command_callback(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=message.UNKNOWN)

    def error_callback(self, bot, update, error):
        try:
            raise error
        except Unauthorized:
            # remove update.message.chat_id from conversation list
            logger.debug('Update {} caused error {}'.format(update, error))
        except BadRequest:
            # handle malformed requests - read more below!
            logger.debug('Update {} caused error {}'.format(update, error))
        except TimedOut:
            # handle slow connection problems
            logger.debug('Update {} caused error {}'.format(update, error))
        except NetworkError:
            # handle other connection problems
            logger.debug('Update {} caused error {}'.format(update, error))
        except ChatMigrated as e:
            # the chat_id of a group has changed, use e.new_chat_id instead
            logger.debug('Update {} caused error {}'.format(update, error))
        except TelegramError:
            # handle all other telegram related errors
            logger.debug('Update {} caused error {}'.format(update, error))

    def message_callback(self, bot, update):
        chat_id = update.message.chat_id

        if not chat_id in self.clients:
            return self.start_command_callback(bot, update)

        client = self.clients[chat_id]
        client.seen_now()

        if client.next_action == action.ACCESS_TOKEN:
            return self.on_token_message(bot, update, client)
        elif client.next_action == action.MESSAGE:
            return self.on_typed_message(bot, update, client)

        self.echo(update.message.chat_id)

    def on_token_message(self, bot, update, client):
        parseresult = urlparse(update.message.text)
        if parseresult.scheme == 'https':
            parseparams = parse_qs(parseresult.fragment)
            access_token = parseparams.get('access_token')[0]
            client.load_vk_user(access_token)
        else:
            client.load_vk_user(update.message.text)
        name = client.vk_user.get_name()
        client.next_action = action.NOTHING
        self.add_poll_server(client)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=message.TOKEN_SAVED(name),
                        reply_markup=Bot.keyboard(client.keyboard_markup()))

    def on_typed_message(self, bot, update, client):
        client.send_message(update.message.text)

    @run_async
    def add_poll_server(self, client):
        if client.vk_token != None:
            self.poller.add(client)

    def echo(self, chat_id):
        self.updater.bot.sendMessage(chat_id=chat_id, text=message.ECHO)

    @staticmethod
    def keyboard(keyboard_markup):
        return ReplyKeyboardMarkup(
            keyboard_markup,
            selective=True,
            resize_keyboard=True)

    def on_update(self, updates, client):
        for update in updates:
            self.process_update(update, client)

    def process_update(self, update, client):
        if len(update) == 0:
            return

        if update[0] == 4:
            # When new message received
            self.receive_vk_message(update, client)

    def receive_vk_message(self, update, client):
        flags = update[2]
        from_id = update[3]
        text = update[6]
        attachments = update[7]

        if flags & 2 == 2:
            # Skip when message is outgoing
            return

        from_name = ''

        if from_id & 2000000000 == 2000000000:
            # Message came from chat
            chat_id = from_id - 2000000000
            chat = Vk_chat.fetch(client.vk_token, chat_id)
            from_name = chat.name_from(attachments['from'])
            client.add_interaction_with(chat)
        else:
            user = Vk_user.fetch_user(client.vk_token, from_id)
            from_name = user.get_name()
            client.add_interaction_with(user)

        self.updater.bot.sendMessage(chat_id=client.chat_id,
                                     text=message.NEW_MESSAGE(from_name, text),
                                     reply_markup=Bot.keyboard(client.keyboard_markup()),
                                     parse_mode=ParseMode.MARKDOWN)
        client.persist()
