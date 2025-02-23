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

#trequest = HTTPXRequest(connection_pool_size=20)
#bot = Bot(token=TOKEN, request=trequest)
bot = None


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received message: {update.message.text}")
    await update.message.reply_text(update.message.text)

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Add chat id to users
    user_chat_ids.add(update.message.chat.id)  # Save the chat_id of new users

    await update.message.reply_text("Registered, you'll start receiving notifications")

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello, {update.effective_user.first_name}!")

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
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("hello", hello))
    application.run_polling()

