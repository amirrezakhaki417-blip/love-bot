import os
import random
import time
from datetime import datetime

import pytz
from telegram.ext import Updater, CommandHandler

# ================== CONFIG ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

TIMEZONE = pytz.timezone("Asia/Tehran")

# ================== MESSAGES ==================

START_MESSAGE = (
    "سلاممم 🫠❤️\n\n"
    "من اینجام که\n"
    "سرِ وقت،\n"
    "یادت بندازم چقدر دوستت دارم ⏰🫀\n\n"
    "لازم نیست کاری بکنی…\n"
    "فقط باش 🤍"
)

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

# ================== USERS STORAGE ==================

USERS_FILE = "users.txt"

def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r") as f:
        return set(int(x.strip()) for x in f if x.strip())

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

def send_to_all(bot, text):
    for uid in load_users():
        try:
            bot.send_message(chat_id=uid, text=text)
        except Exception:
            pass

# ================== TIME LOGIC ==================

def is_quiet_hours(now):
    return 2 <= now.hour < 7

def should_send_round(now):
    return now.hour == now.minute

# ================== SCHEDULER LOOP ==================

def scheduler_loop(bot):
    last_sent = set()

    while True:
        now = datetime.now(TIMEZONE)
        key = now.strftime("%Y-%m-%d %H:%M")

        if key in last_sent:
            time.sleep(5)
            continue

        if is_quiet_hours(now):
            time.sleep(30)
            continue

        if now.hour == 8 and now.minute == 0:
            send_to_all(bot, MORNING_MESSAGE)
            last_sent.add(key)

        elif now.hour == 23 and now.minute == 30:
            send_to_all(bot, NIGHT_MESSAGE)
            last_sent.add(key)

        elif should_send_round(now):
            send_to_all(bot, random.choice(ROUND_MESSAGES))
            last_sent.add(key)

        time.sleep(20)

# ================== COMMANDS ==================

def start(update, context):
    user_id = update.effective_user.id
    save_user(user_id)
    update.message.reply_text(START_MESSAGE)

# ================== MAIN ==================

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()

    # Start scheduler loop
    scheduler_loop(updater.bot)

    updater.idle()

if __name__ == "__main__":
    main()
