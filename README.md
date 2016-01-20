# VK Messages Telegram Bot

Listens for your messages updates and forwards them to your Telegram.

## Installation

1. Copy `set_env.example.sh` to `set_env.sh`
2. [Create](https://vk.com/editapp?act=create) *standalone* VK app with any name and copy its App ID from settings to `set_env.sh`
3. Create new Telegram bot with any name by sending `/newbot` command to [@BotFather](http://telegram.me/botfather) and copy token to access the HTTP API to `set_env.sh`
4. Configure bot with commands from [bot_info.md](bot_info.md)
5. Run bot with `./run.sh` (you can specify `reset-db` parameter, if you messed up the database. You can always just remove the database file)

## Deploying to [Heroku](https://heroku.com/)

Install [Heroku Toolbelt](https://toolbelt.heroku.com/), then:

```
cd vk-messages-bot
heroku login
heroku create vk-messages-bot # create app
heroku buildpacks:set heroku/python # set python buildpack
git push heroku master # deploy app to heroku
heroku config:set VK_CLIENT_ID='<VK_APP_CLIENT_ID>' # set config vars
heroku config:set TELEGRAM_TOKEN='<TELEGRAM_TOKEN>'
heroku ps:scale worker=1 # start 1 worker dyno
heroku ps:stop worker # or stop worker dyno
```

https://devcenter.heroku.com/articles/dynos
https://devcenter.heroku.com/articles/config-vars