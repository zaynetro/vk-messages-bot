# Vk messages bot

Listens for your messages updates and forwards them to your telegram.

## Installations

1. Create *standalone* vk app
2. Register your bot with [@BotFather](http://telegram.me/botfather) telegram bot (see detailed instructions below)
3. Create `set_env.sh` file and populate with required values (see example in `set_env.example.sh`
4. Run bot with `./run.sh` (you can specify `reset-db` parameter, if you messed up the database. You can always just remove the database file)

## BotFather config

1. Create a new bot with `/newbot` command
2. Configure bot with commands (see `bot_info.md`)
  * `/setdescription`
  * `/setjoingroups` set to Disable
  * `/setcommands`
