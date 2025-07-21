import paramiko
from telegram import Update
from telegram.ext import ContextTypes
from .config import SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD
from .ratelimit import rate_limit

@rate_limit
async def get_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USER,
            password=SSH_PASSWORD
        )
        _, stdout, _ = ssh.exec_command("free -m | grep Mem")
        mem_line = stdout.read().decode()
        ssh.close()

        parts = mem_line.split()
        total = int(parts[1])
        used = int(parts[2])
        usage_percent = (used / total) * 100

        await update.message.reply_text(
            f"Memory Usage:\nUsed: {used} MB\nTotal: {total} MB\nPercent: {usage_percent:.2f}%"
        )
    except Exception as e:
        await update.message.reply_text(f"Exception: {e}")

