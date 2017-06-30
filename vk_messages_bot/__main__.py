#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from vk_messages_bot.bot import Bot
from vk_messages_bot.db import db


def main():
    tg_bot_token = os.environ['TG_BOT_TOKEN']
    vk_client_id = os.environ['VK_CLIENT_ID']
    use_webhook = bool(int(os.getenv('USE_WEBHOOK', '0')))
    app_port = int(os.getenv('PORT', '5000'))
    app_url = os.getenv('APP_URL', '')

    args = sys.argv[1:]
    if len(args) > 0:
        if '--reset-db' in args:
            print('Resetting database')
            db.clear()
            db.sync()

    bot = Bot(tg_bot_token, vk_client_id)
    bot.run(use_webhook, app_url, app_port)


if __name__ == '__main__':
    main()
