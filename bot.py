import os
import random
import time
from datetime import datetime
from flask import Flask
import threading

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ================== CONFIG ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in Environment Variables")

# ================== KEEP ALIVE (Render) ==================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running ✅"

def run_web():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================== MESSAGES ==================

MORNING_MESSAGE = "صبح ات بخیرر جون دلمم🥹🫠🐣👧🏻🫀💋😘"

NIGHT_MESSAGE = (
    "خیلییی دوستت دارمم ، شب ات بخیر خوشگلمم🙃🌒💋😘\n"
    "خوب بخوابی💙🌊"
)

ROUND_MESSAGES = [
    "خیلی دوستت دارمم زندگیم❤️🍒",
    "همیشه تو دلمی قشنگم 🫀✨",
    "یه عالمه دوستت دارم 😘💞",
    "با تو همه چی قشنگ‌تره 💖🌸",
    "فقط مال منی ها 😌❤️",
    "بودنت آرامشه 🫶🌊",
]

# ================== TIME LOGIC ==================

def is_quiet_hours(now: datetime) -> bool:
    # Quiet hours: 02:00 – 06:59
    return 2 <= now.hour < 7

def should_send_round(now: datetime) -> bool:
    # Hour == Minute (e.g. 11:11, 22:22)
    return now.hour == now.minute

# ================== BOT TASK ==================

async def scheduled_messages(app):
    last_sent = set()

    while True:
        now = datetime.now()  # TZ is handled by Environment Variable

        key = now.strftime("%Y-%m-%d %H:%M")

        if key in last_sent:
            time.sleep(5)
            continue

        # Quiet hours
        if is_quiet_hours(now):
            time.sleep(30)
            continue

        # 08:00 Morning
        if now.hour == 8 and now.minute == 0:
            await send_to_all(app, MORNING_MESSAGE)
            last_sent.add(key)

        # 23:30 Night
        elif now.hour == 23 and now.minute == 30:
            await send_to_all(app, NIGHT_MESSAGE)
            last_sent.add(key)

        # Round time
        elif should_send_round(now):
            msg = random.choice(ROUND_MESSAGES)
            await send_to_all(app, msg)
            last_sent.add(key)

        time.sleep(20)

# ================== USERS STORAGE ==================

USERS_FILE = "users.txt"

def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r") as f:
        return set(int(x.strip()) for x in f if x.strip())

def save_user(user_id: int):
    users = load_users()
    if user_id not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

async def send_to_all(app, text: str):
    users = load_users()
    for uid in users:
        try:
            await app.bot.send_message(chat_id=uid, text=text)
        except Exception:
            pass

# ================== COMMANDS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    await update.message.reply_text("سلام 😌\nخوش اومدی 💖")

# ================== MAIN ==================

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    # Background scheduler
    application.job_queue.run_once(
        lambda ctx: ctx.application.create_task(
            scheduled_messages(ctx.application)
        ),
        when=1,
    )

    # Run Flask in another thread (keep alive)
    threading.Thread(target=run_web, daemon=True).start()

    application.run_polling()

if __name__ == "__main__":
    main()
