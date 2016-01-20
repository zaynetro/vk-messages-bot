# VK Messages Telegram Bot

Listens for your messages updates and forwards them to your Telegram.

## Installation

1. Copy `set_env.example.sh` to `set_env.sh`
2. [Create](https://vk.com/editapp?act=create) *standalone* VK app with any name and copy its App ID from settings to `set_env.sh`
3. Create new Telegram bot with any name by sending `/newbot` command to [@BotFather](http://telegram.me/botfather) and copy token to access the HTTP API to `set_env.sh`
4. Configure bot with commands from [bot_info.md](bot_info.md)
5. Run bot with `./run.sh` (you can specify `reset_db` parameter, if you messed up the database. You can always just remove the database file)