# Server Logs Telegram Bot

**🔧 Telegram Bot for Monitoring Server Logs via SSH**

You can test the bot here: [@server_pyinsight_bot](https://t.me/server_pyinsight_bot)

This project provides a Telegram bot for reading server logs and basic resource usage via SSH. Server information is stored in an SQLite database.

## Requirements
- Python 3.10+
- [pip](https://pip.pypa.io/)

Install the Python dependencies using:

```bash
pip install python-telegram-bot paramiko
```

## Configuration
The bot expects the following configuration variables:

- `TELEGRAM_TOKEN` – your Telegram bot token
- `SSH_HOST` – default server address
- `SSH_PORT` – SSH port (default: 22)
- `SSH_USER` – SSH username
- `SSH_PASSWORD` – SSH password

Edit `commands/config.py` and update these values accordingly or export them as environment variables before running the bot.

## Initialize the Database
Create the SQLite database by running:

```bash
python test.py
```

This script calls `init_db()` from `commands.db` and creates `servers.db` in the project root.

## Running the Bot
After configuring the values and creating the database, start the bot with:

```bash
python main.py
```

The bot listens for commands such as `/addserver`, `/getlog`, `/cpu`, `/memory`, and more.
