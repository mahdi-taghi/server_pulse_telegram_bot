from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from commands.cpu import get_cpu
from commands.logs import get_logs
from commands.config import TELEGRAM_TOKEN
from commands.memory import get_memory


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running.\nUse /cpu or /getlog or /memory.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cpu", get_cpu))
    app.add_handler(CommandHandler("getlog", get_logs))  
    app.add_handler(CommandHandler("memory", get_memory))

    app.run_polling()

if __name__ == "__main__":
    main()
