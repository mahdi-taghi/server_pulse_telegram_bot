import paramiko
from telegram import Update
from telegram.ext import ContextTypes
import re
from .config import SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD
from .ratelimit import rate_limit

@rate_limit
async def get_cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USER,
            password=SSH_PASSWORD
        )
        _, stdout, _ = ssh.exec_command("top -bn1 | grep 'Cpu(s)'")
        cpu_line = stdout.read().decode()
        ssh.close()

        match = re.search(r'(\d+\.\d+)\s*id', cpu_line)
        if match:
            idle = float(match.group(1))
            used = 100 - idle
            await update.message.reply_text(f"CPU Usage: {used:.2f}%")
        else:
            await update.message.reply_text("Could not parse CPU usage.")
    except Exception as e:
        await update.message.reply_text(f"Exception: {e}")

