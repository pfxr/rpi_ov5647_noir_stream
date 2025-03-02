from picamera2 import Picamera2, Preview
from flask import Flask, Response
import numpy as np
import cv2
import logging
from motion_detection import motion_detection

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

class ir_camera:
    MAX_FRAMES = 30
    def __init__(self):
        self.video_callbacks = list()
        self.notifications = list()

        # Initialize motion detection framework
        self.motion_detection = motion_detection()

        # Disable motion detection by default
        self.enable_motion_detection = False

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

    def register_notification(self, notification):
        self.notifications.append(notification)

    def register_callback(self, callback):
        self.video_callbacks.append(callback)

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

    def start_motion_detection(self):
        self.enable_motion_detection = True

    def stop_motion_detection(self):
        self.enable_motion_detection = False

    def gen_frames(self):
        """Generate video frames."""
        while True:
            # Capture frame-by-frame
                frame = self.picam2.capture_array()
                #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Flip verticaly and horizontaly
                frame = cv2.flip(frame, -1)

                # Process the frame (e.g., convert to JPEG)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()

                if self.enable_motion_detection == True:
                    motion_detected, motion_mask = self.motion_detection.calculate_motion(frame)

                    # Process motion mask
                    ret, buffer = cv2.imencode('.jpg', motion_mask)
                    motion_mask = buffer.tobytes()

                    merged_frame = self.merge_frames(frame_bytes, motion_mask)

                    if motion_detected:
                        logger.info("Motion Detected")

                        for notification in self.notifications:
                            notification("Motion Detected\n See at: http://192.168.1.110:5000/video_feed")
                else:
                    merged_frame = frame_bytes

                # Yield the frame
                for callback in self.video_callbacks:
                    callback(merged_frame)

