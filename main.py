import asyncio
import threading
import telegram_bot
from flask import Flask
from ir_camera import ir_camera
import json

# Initialize main objects
app = Flask(__name__)
cam = ir_camera(app)
cam.register_notification(telegram_bot.send_message)


# Run Flask
def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    # Run Flask and Telegram Bot in parallel
    threading.Thread(target=run_flask, daemon=True).start()

    with open('configs.json') as f:
        d = json.load(f)
        telegram_bot.init(token=d["token"])  # Runs the bot in the main thread
