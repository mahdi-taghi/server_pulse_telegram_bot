from dotenv import load_dotenv
import os

load_dotenv()  

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SSH_HOST = os.getenv("SSH_HOST", "")
SSH_PORT = int(os.getenv("SSH_PORT", "22"))
SSH_USER = os.getenv("SSH_USER", "")
SSH_PASSWORD = os.getenv("SSH_PASSWORD", "")
