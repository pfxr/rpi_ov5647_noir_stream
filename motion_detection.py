import cv2
import collections
import numpy as np
from dataclasses import dataclass

@dataclass
class states:
    INIITAL = 0
    CAPTURING = 1
    DETECTED = 2

class motion_detection:
    # Macros
    MIN_DETECTED_PIXELS = 120
    THRESHOLD = 80
    ASSIGN_VALUE = 255

    def __init__(self):
        self.notifications = list()
        self.previous_frame = np.array([])

    def register_notification(self, notification):
        self.notifications.append(notification)

    def detect_motion(self, frame):
        # Count nonzero pixels (indicating motion)
        motion_pixels = np.count_nonzero(frame)

        # Motion detected if enough pixels changed
        return motion_pixels > self.MIN_DETECTED_PIXELS

    def calculate_motion(self, frame):
        # Convert to gray scale
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Ignore the first frame
        if self.previous_frame.size == 0:
            self.previous_frame = frame_gray

        diff = cv2.absdiff(self.previous_frame, frame_gray)
        ret, motion_mask = cv2.threshold(diff, self.THRESHOLD, self.ASSIGN_VALUE, cv2.THRESH_BINARY)
        motion_detected = self.detect_motion(motion_mask)

        self.previous_frame = frame_gray

        return motion_detected, motion_mask





