from picamera2 import Picamera2, Preview
from flask import Flask, Response
import numpy as np
import cv2


class ir_camera:
    MAX_FRAMES = 30
    THRESHOLD = 80
    ASSIGN_VALUE = 255

    def __init__(self, app):
        self.app = app
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)

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

        self.picam2 = Picamera2(tuning=tuning)

        # Configure resolution and output data format
        self.picam2.configure(self.picam2.create_video_configuration(main={"format": "RGB888", "size": (800, 600)}))

        # Start picam2
        self.picam2.start()

        # Target for 30 FPS (probably not going to get it)
        self.picam2.set_controls({"FrameRate": self.MAX_FRAMES})

#    @app.route('/video_feed')
    def video_feed(self):
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(self.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def detect_motion(self, frame):
        # Count nonzero pixels (indicating motion)
        motion_pixels = np.count_nonzero(frame)

        # Motion detected if enough pixels changed
        return motion_pixels > 120

    def merge_frames(self, frame1, frame2):
        # Decode both frames (assuming they are JPEG images)
        img1 = cv2.imdecode(np.frombuffer(frame1, np.uint8), cv2.IMREAD_COLOR)
        img2 = cv2.imdecode(np.frombuffer(frame2, np.uint8), cv2.IMREAD_COLOR)

        # Ensure both images have the same dimensions
        height = max(img1.shape[0], img2.shape[0])
        width = img1.shape[1] + img2.shape[1]

        # Create a blank canvas
        merged_img = np.zeros((height, width, 3), dtype=np.uint8)

        # Place both images side by side
        merged_img[:img1.shape[0], :img1.shape[1]] = img1
        merged_img[:img2.shape[0], img1.shape[1]:] = img2

        # Encode the merged image back to JPEG
        _, merged_frame = cv2.imencode('.jpg', merged_img)
        return merged_frame.tobytes()

    def gen_frames(self):
        """Generate video frames."""
        while True:
            for t in range(self.MAX_FRAMES):
                # Capture frame-by-frame
                frame = self.picam2.capture_array()
                #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Flip verticaly and horizontaly
                frame = cv2.flip(frame, -1)

                # Convert to gray scale
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

                # Ignore the first frame
                if t == 0:
                    background = frame_gray
                    continue

                # Use remaining frames to detect motion
                else:
                    diff = cv2.absdiff(background, frame_gray)
                    ret, motion_mask = cv2.threshold(diff, self.THRESHOLD, self.ASSIGN_VALUE, cv2.THRESH_BINARY)
                    motion_detected = self.detect_motion(motion_mask)

                    if motion_detected:
                        print("Motion Detected")

                # Process the frame (e.g., convert to JPEG)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

                # Process motion mask
                ret, buffer = cv2.imencode('.jpg', motion_mask)
                motion_mask = buffer.tobytes()

                merged_frame = self.merge_frames(frame, motion_mask)
                # Yield the frame
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + merged_frame + b'\r\n')


