# vision/hand_open_close.py
import cv2

class HandOpenCloseDetector:
    def __init__(self):
        # Подбирается очень просто (см. ниже)
        self.open_threshold = 80   # светло
        self.close_threshold = 40  # темно

    def infer(self, frame_bgr):
        # Переводим в серый
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        # Средняя яркость кадра
        mean_val = gray.mean()

        # Для отладки можно печатать
        # print("MEAN:", mean_val)

        if mean_val > self.open_threshold:
            return "OPEN"
        elif mean_val < self.close_threshold:
            return "CLOSE"
        else:
            return "UNKNOWN"