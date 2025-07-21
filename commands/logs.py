import paramiko
from telegram import Update
from telegram.ext import ContextTypes
from .db import get_full_servers_by_user
from .config import SSH_PORT
from .ratelimit import rate_limit

@rate_limit
async def get_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args:
            await update.message.reply_text("Please specify the server number. Example: /getlog 1")
            return

        server_index = int(args[0]) - 1
        user_id = update.effective_user.id
        servers = get_full_servers_by_user(user_id)

        if server_index < 0 or server_index >= len(servers):
            await update.message.reply_text("Invalid server number.")
            return

        server_name, ip, username, password = servers[server_index]

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=SSH_PORT, username=username, password=password)
        _, stdout, stderr = ssh.exec_command('tail -n 30 /var/log/syslog')
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()

        if output.strip():
            await update.message.reply_text(f"Logs from {server_name}:\n{output[:4000]}")
        elif error.strip():
            await update.message.reply_text(f"Error:\n{error[:4000]}")
        else:
            await update.message.reply_text("No output received from the command.")
    except Exception as e:
        await update.message.reply_text(f"Exception:\n{e}")
