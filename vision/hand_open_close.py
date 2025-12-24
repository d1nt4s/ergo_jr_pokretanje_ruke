# vision/hand_open_close.py
import cv2

class HandOpenCloseDetector:
    def __init__(self):
        self.open_threshold = 9000
        self.close_threshold = 4000

    def infer(self, frame_bgr):
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)

        _, thresh = cv2.threshold(
            blur, 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return "UNKNOWN"

        hand_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(hand_contour)

        if area > self.open_threshold:
            return "OPEN"
        elif area < self.close_threshold:
            return "CLOSE"
        else:
            return "UNKNOWN"