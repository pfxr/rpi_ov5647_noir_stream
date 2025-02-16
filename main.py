import io
import threading
import time
from telegram_bot import telegram_bot
import numpy as np
from flask import Flask, Response
from ir_camera import ir_camera

app = Flask(__name__)
cam = ir_camera(app)
app.run(host = '0.0.0.0', port = 5000, threaded=True)
