from collections import defaultdict
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

# Maximum requests allowed per user within the window
REQUEST_LIMIT = 20
# Time window in seconds
WINDOW_SECONDS = 60

# Dictionary to track timestamps of requests per user
_request_log: defaultdict[int, list[datetime]] = defaultdict(list)


def rate_limit(func):
    """Decorator to enforce per-user rate limiting."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if user:
            now = datetime.utcnow()
            timestamps = [t for t in _request_log[user.id] if now - t < timedelta(seconds=WINDOW_SECONDS)]
            _request_log[user.id] = timestamps
            if len(timestamps) >= REQUEST_LIMIT:
                if update.message:
                    await update.message.reply_text("Too many requests. Please try again later.")
                elif update.callback_query:
                    await update.callback_query.answer("Too many requests. Try again later.", show_alert=True)
                return
            timestamps.append(now)
        return await func(update, context, *args, **kwargs)
    return wrapper