import paramiko
from telegram import Update
from telegram.ext import ContextTypes
import re

def parse_args(text):
    """Extract key=value pairs from message"""
    return dict(re.findall(r'(\w+)=([^\s]+)', text))

async def get_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = parse_args(update.message.text)

        ip = args.get("ip")
        user = args.get("user")
        password = args.get("password")
        log_path = args.get("log", "/var/log/syslog")

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=ip,
            port=22,
            username=user,
            password=password
        )

        stdin, stdout, stderr = ssh.exec_command(f'tail -n 30 {log_path}')
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()

        if output.strip():
            await update.message.reply_text(f"Logs:\n{output[:4000]}")
        elif error.strip():
            await update.message.reply_text(f"Error:\n{error[:4000]}")
        else:
            await update.message.reply_text("No output received from the command.")

    except Exception as e:
        await update.message.reply_text(f"Exception:\n{e}")
