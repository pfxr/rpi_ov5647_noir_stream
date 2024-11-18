import io
import time
from picamera2 import Picamera2, Preview
from flask import Flask, Response
import cv2

# Here we load up the tuning for the HQ cam and alter the default exposure profile.
# For more information on what can be changed, see chapter 5 in
# https://datasheets.raspberrypi.com/camera/raspberry-pi-camera-guide.pdf

# Set tunning for ov5647_noir
tuning = Picamera2.load_tuning_file("ov5647_noir.json")
algo = Picamera2.find_tuning_algo(tuning, "rpi.agc")
if "channels" in algo:
    algo["channels"][0]["exposure_modes"]["normal"] = {"shutter": [100, 66666], "gain": [1.0, 8.0]}
else:
    algo["exposure_modes"]["normal"] = {"shutter": [100, 66666], "gain": [1.0, 8.0]}

picam2 = Picamera2(tuning=tuning)

# Configure resolution and output data format
picam2.configure(picam2.create_video_configuration(main={"format": "RGB888", "size": (800, 600)}))

# Start picam2
picam2.start()

# Target for 30 FPS (probably not going to get it)
picam2.set_controls({"FrameRate": 30})
time.sleep(2)

app = Flask(__name__)

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    """Generate video frames."""
    while True:
        # Capture frame-by-frame
        frame = picam2.capture_array()
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Flip verticaly and horizontaly
        frame = cv2.flip(frame, -1)

        # Process the frame (e.g., convert to JPEG)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Start our server in port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
