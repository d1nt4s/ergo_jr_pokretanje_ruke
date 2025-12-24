# vision/hand_open_close.py
import cv2
import mediapipe as mp
from typing import Literal

State = Literal["OPEN", "CLOSE", "UNKNOWN"]

class HandOpenCloseDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )

    def infer(self, frame_bgr) -> State:
        # MediaPipe работает в RGB
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        result = self.hands.process(frame_rgb)

        if not result.multi_hand_landmarks:
            return "UNKNOWN"

        landmarks = result.multi_hand_landmarks[0].landmark

        fingers_up = self._count_fingers_up(landmarks)

        if fingers_up >= 4:
            return "OPEN"
        elif fingers_up <= 1:
            return "CLOSE"
        else:
            return "UNKNOWN"

    def _count_fingers_up(self, lm) -> int:
        """
        Очень простая логика:
        палец считается поднятым, если tip выше pip по y
        """
        tips = [8, 12, 16, 20]   # index, middle, ring, pinky
        pips = [6, 10, 14, 18]

        count = 0
        for tip, pip in zip(tips, pips):
            if lm[tip].y < lm[pip].y:
                count += 1

        # большой палец (упрощённо)
        if abs(lm[4].x - lm[3].x) > 0.04:
            count += 1

        return count