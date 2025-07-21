from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    ConversationHandler, MessageHandler, CallbackQueryHandler, filters
)
from commands.server import (
    start_add_server, get_server_name, get_ip, get_username, get_password,
    cancel, list_servers, start_get_log, handle_get_log,
    start_delete_server, handle_delete_server,
    start_get_cpu, handle_get_cpu,
    start_get_memory, handle_get_memory,
    start_get_disk, handle_get_disk,
    start_set_default, handle_set_default,
    SELECT_LOG, SELECT_DELETE, SELECT_CPU, SELECT_MEMORY, SELECT_DISK,
    SELECT_DEFAULT, SERVER_NAME, IP, USERNAME, PASSWORD
)
from commands.config import TELEGRAM_TOKEN


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🖥️ Manage Servers", callback_data="manage_servers"),
            InlineKeyboardButton("📊 Monitor Servers", callback_data="monitor_servers")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤖 Bot is running.\nPlease choose an option:",
        reply_markup=reply_markup
    )


async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "manage_servers":
        keyboard = [
            ["addserver", "deleteserver"],
            ["defaultserver", "myservers"],
            ["start"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.message.reply_text("🛠 Server Management Options:", reply_markup=reply_markup)

    elif query.data == "monitor_servers":
        keyboard = [
            ["getlog", "cpu", "memory", "disk"],
            ["start"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.message.reply_text("📈 Monitoring Options:", reply_markup=reply_markup)


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("addserver", start_add_server),
            MessageHandler(filters.TEXT & filters.Regex("^addserver$"), start_add_server)
        ],
        states={
            SERVER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_server_name)],
            IP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ip)],
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    getlog_conv = ConversationHandler(
        entry_points=[
            CommandHandler("getlog", start_get_log),
            MessageHandler(filters.TEXT & filters.Regex("^getlog$"), start_get_log)
        ],
        states={
            SELECT_LOG: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_get_log)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    delete_conv = ConversationHandler(
        entry_points=[
            CommandHandler("deleteserver", start_delete_server),
            MessageHandler(filters.TEXT & filters.Regex("^deleteserver$"), start_delete_server)
        ],
        states={
            SELECT_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_server)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    cpu_conv = ConversationHandler(
        entry_points=[
            CommandHandler("cpu", start_get_cpu),
            MessageHandler(filters.TEXT & filters.Regex("^cpu$"), start_get_cpu)
        ],
        states={
            SELECT_CPU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_get_cpu)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    memory_conv = ConversationHandler(
        entry_points=[
            CommandHandler("memory", start_get_memory),
            MessageHandler(filters.TEXT & filters.Regex("^memory$"), start_get_memory)
        ],
        states={
            SELECT_MEMORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_get_memory)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    disk_conv = ConversationHandler(
        entry_points=[
            CommandHandler("disk", start_get_disk),
            MessageHandler(filters.TEXT & filters.Regex("^disk$"), start_get_disk)
        ],
        states={
            SELECT_DISK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_get_disk)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    default_conv = ConversationHandler(
        entry_points=[
            CommandHandler("defaultserver", start_set_default),
            MessageHandler(filters.TEXT & filters.Regex("^defaultserver$"), start_set_default),
        ],
        states={
            SELECT_DEFAULT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_set_default)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^start$"), start))
    app.add_handler(CallbackQueryHandler(handle_inline_buttons))
    app.add_handler(CommandHandler("myservers", list_servers))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^myservers$"), list_servers))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^cancel$"), cancel))
    app.add_handler(conv_handler)
    app.add_handler(getlog_conv)
    app.add_handler(delete_conv)
    app.add_handler(cpu_conv)
    app.add_handler(memory_conv)
    app.add_handler(disk_conv)
    app.add_handler(default_conv)

    app.run_polling()


if __name__ == "__main__":
    main()
