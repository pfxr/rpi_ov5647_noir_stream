
from flask import Flask, Response
import time

class http_server():
    def __init__(self):
        self.app = Flask(__name__)
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)

    def run(self):
        self.app.run(host="0.0.0.0", port=5000)

    def receive_frame(self, frame):
        self.frame = frame
        self.blocked = False # unblock wait_for_frame

    def wait_for_frame(self):
        while True:
            self.blocked = True

            while self.blocked:
                time.sleep(0.01)
                continue
                # When new image comes break this
                # maybe add a time.sleep here??

            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + self.frame + b'\r\n')

    def video_feed(self):
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(self.wait_for_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')
