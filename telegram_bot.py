import logging
import asyncio
from telegram import Update, Bot
from telegram.request import HTTPXRequest
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# All users that subscribe to notifications
user_chat_ids = set()

# Telegram Bot Token (replace with your actual token)
TOKEN = ""

# Initialize global bot variable
bot = None

# Unpuplated callbacks
start_video_calback = None
start_motion_detection_calback = None


def register_start_video_callback(func):
    global start_video_calback
    start_video_calback = func

def register_start_motion_detection_callback(func):
    global start_motion_detection_calback
    start_motion_detection_calback = func

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received message: {update.message.text}")
    await update.message.reply_text(update.message.text)

# Telegram Bot Handlers
async def start_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Add chat id to users
    user_chat_ids.add(update.message.chat.id)  # Save the chat_id of new users

    start_video_calback()

    await update.message.reply_text("Starting video, check http://192.168.1.110/video_feed")

async def start_motion_detection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Add chat id to users
    user_chat_ids.add(update.message.chat.id)  # Save the chat_id of new users

    start_motion_detection_calback()

    await update.message.reply_text("Starting motion detection")



# Function to send a message without a command
def send_message(message):
    for chat_id in user_chat_ids:
        try:
            asyncio.run(bot.send_message(chat_id=chat_id, text=message))
        except Exception as e:
            print(f"Failed to send message to {chat_id}: {e}")

def init(token):
    global bot

    application = Application.builder().token(token).build()
    bot = Bot(token)

    # Add handlers
    application.add_handler(CommandHandler("start_video", start_video))
    application.add_handler(CommandHandler("start_motion_detection", start_motion_detection))

    application.run_polling()

