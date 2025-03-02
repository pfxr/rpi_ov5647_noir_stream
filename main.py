import asyncio
import threading
import telegram_bot
from flask import Flask
from ir_camera import ir_camera
from http_server import http_server
import json


server = http_server()
cam = ir_camera()
cam.register_notification(telegram_bot.send_message)
cam.register_callback(server.receive_frame)

# Thread global variables
video_thread = None
server_thread = None

# Run Flask
def run_http_server():
    server_thread = threading.Thread(target=server.run, daemon=True).start()

def stop_http_server():
    server_thread.stop()

def run_video():
    video_thread = threading.Thread(target=cam.gen_frames, daemon=True).start()

def stop_video():
    video_thread.stop()

if __name__ == "__main__":
    run_http_server()

    with open('configs.json') as f:
        telegram_bot.register_start_video_callback(run_video)
        telegram_bot.register_start_motion_detection_callback(cam.start_motion_detection)

        d = json.load(f)
        telegram_bot.init(token=d["token"])  # Runs the bot in the main thread
