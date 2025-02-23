import asyncio
import threading
import telegram_bot
from flask import Flask
from ir_camera import ir_camera

app = Flask(__name__)
cam = ir_camera(app, notification = telegram_bot.send_message)


# Run Flask
def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    # Run Flask and Telegram Bot in parallel
    threading.Thread(target=run_flask, daemon=True).start()
    telegram_bot.init()  # Runs the bot in the main thread
