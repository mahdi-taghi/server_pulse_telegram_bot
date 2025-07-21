import paramiko
from telegram import Update
from telegram.ext import ContextTypes
from .config import SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD

async def get_disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USER,
            password=SSH_PASSWORD
        )
        _, stdout, _ = ssh.exec_command("df -h / | tail -n 1")
        disk_line = stdout.read().decode()
        ssh.close()

        parts = disk_line.split()
        total = parts[1]
        used = parts[2]
        percent = parts[4]

        await update.message.reply_text(
            f"Disk Usage:\nUsed: {used}B\nTotal: {total}B\nPercent: {percent}"
        )
    except Exception as e:
        await update.message.reply_text(f"Exception: {e}")