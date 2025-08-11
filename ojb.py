import os
import random
from datetime import date, time
import pytz
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables.")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-app.onrender.com
if not WEBHOOK_URL:
    raise ValueError("No WEBHOOK_URL found in environment variables.")

PORT = int(os.getenv("PORT", "8443"))

PASSWORD = "iloveyiyi"
PARTNER_CHAT_IDS = [1224169124]  # multiple IDs supported
ASKING_HELP = 1
SINGAPORE_TZ = pytz.timezone("Asia/Singapore")

# --- Keyboard Menus ---
MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["tell me a joke", "want jovie..."],
        ["love note pws", "daily check-in"],
        ["gimme hug", "how many days left?"],
        ["main menu"]
    ],
    one_time_keyboard=False,
    resize_keyboard=True
)

JOVIE_MENU = ReplyKeyboardMarkup(
    [
        ["am sad...", "am happi!"],
        ["angry?", "did we argue?"],
        ["main menu"]
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Please enter the password to continue:")
    return 0

async def verify_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == PASSWORD:
        return await show_main_menu(update)
    await update.message.reply_text("Wrong password. Try again.")
    return 0

async def show_main_menu(update: Update):
    await update.message.reply_text(
        "✅ Welcome to Jovie's main menu!\n\n"
        "Use /cancel to end the conversation if needed.\n\n"
        "What does babie want to do?",
        reply_markup=MAIN_MENU
    )
    return ASKING_HELP

async def reply_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.lower()

    if "i love you" in user_msg:
        await update.message.reply_text(random.choice([
            "i love you too!!", "I LOVE YOU I LOVE YOU I LOVE YOU",
            "but i love you the most idc", "i lub babie too",
            "i love you!", "i love you more", "you're babie... but i love you too!",
            "ilyt!"
        ]), reply_markup=MAIN_MENU)

    elif "i miss you" in user_msg:
        await update.message.reply_text(random.choice([
            "i miss you too hmph", "i miss you more",
            "i miss you the mostestestestest", "i miss yu most",
            "idc i win because i miss you more"
        ]), reply_markup=MAIN_MENU)

    elif "main menu" in user_msg:
        return await show_main_menu(update)

    elif "joke" in user_msg:
        await update.message.reply_text(random.choice([
            "Why did the Python programmer go hungry? Because his food was in bytes!",
            "Why do Java developers wear glasses? Because they don't C#!",
            "Why was the function so good at basketball? Because it had a lot of callbacks."
        ]), reply_markup=MAIN_MENU)

    elif "want jovie" in user_msg:
        await update.message.reply_text("aww baby... how are you feeling?", reply_markup=JOVIE_MENU)

    elif "sad" in user_msg:
        await update.message.reply_text("It's okay to feel sad. You're not alone. 🤗")
        await update.message.reply_text("Sending cuddles...")
        await update.message.reply_text("You’re very loved, okay? ❤️", reply_markup=MAIN_MENU)

    elif "happy" in user_msg:
        await update.message.reply_text(
            "That's wonderful! Keep smiling and spread the joy 😄\n"
            "<a href='http://www.youtube.com'>Click here</a>",
            parse_mode="HTML",
            reply_markup=MAIN_MENU
        )

    elif "love note" in user_msg:
        await update.message.reply_text(random.choice([
            "You're the best part of my day 💖",
            "Even when we're apart, you're always on my mind 💭",
            "You're more than special — you're my everything ✨"
        ]), reply_markup=MAIN_MENU)

    elif "daily check-in" in user_msg:
        await update.message.reply_text("Have you eaten? 🥢")
        await update.message.reply_text("Drank enough water? 💧")
        await update.message.reply_text("Rested your eyes lately? 👀", reply_markup=MAIN_MENU)

    elif "gimme hug" in user_msg:
        await update.message.reply_text(random.choice([
            "BIGGG HUGGG 🤗", "Wrapping you up in the softest squishiest hug 🧸",
            "*squeezes you tightly* 😚"
        ]), reply_markup=MAIN_MENU)

    elif "how many days left" in user_msg:
        next_meeting = date(2025, 9, 5)
        days_left = (next_meeting - date.today()).days
        await update.message.reply_text(
            f"There are {days_left} days left until we see each other again! 💕",
            reply_markup=MAIN_MENU
        )

    else:
        await update.message.reply_text(random.choice([
            "what... am too siwwy to understand message... can you choose button pwease",
            "aaa zenzenwakanai what is baby saying... pwease select button to continue",
            "sowwy but bot don't understand... can choose button... meanwhile baby will learn how to code better"
        ]), reply_markup=MAIN_MENU)

    return ASKING_HELP

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "baibao! use /start to activate me again!",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def send_good_morning(context: ContextTypes.DEFAULT_TYPE):
    for chat_id in PARTNER_CHAT_IDS:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text="🌞 Good morning my love! Hope you have a beautiful day 💛"
            )
        except Exception as e:
            print(f"Failed to send morning message to {chat_id}: {e}")

# --- Main ---
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_password)],
            ASKING_HELP: [MessageHandler(filters.TEXT & ~filters.COMMAND, reply_help)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)

    # Schedule daily morning message job
    app.job_queue.run_daily(
        send_good_morning,
        time=time(hour=7, minute=0, tzinfo=SINGAPORE_TZ),
        name="morning_message"
    )

    url_path = BOT_TOKEN  # secure path for webhook
    webhook_url = f"{WEBHOOK_URL}/{url_path}"

    # Start webhook
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=url_path,
        webhook_url=webhook_url,
    )
    print(f"Bot is running with webhook at {webhook_url}")

    # Block until the bot is stopped
    await app.idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


#await asyncio.sleep(1) for bot to wait between messages