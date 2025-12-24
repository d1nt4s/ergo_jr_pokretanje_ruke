# app/main.py
import time
import cv2

from utils.debounce import Debounce
from vision.hand_open_close import HandOpenCloseDetector
from control.gripper import GripperController

CAMERA_INDEX = 0  # у вас рабочий индекс

def main():
    # 1) Камера
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError("Не удалось открыть камеру")

    # 2) Vision
    detector = HandOpenCloseDetector()

    # 3) Debounce
    deb = Debounce(stable_frames=5)

    # 4) Гриппер
    gripper = GripperController(gripper_motor_name="m6")
    gripper.connect()
    
    poppy.rest_posture.start()

    poppy.m1.compliant = False
    poppy.m2.compliant = False
    poppy.m3.compliant = False
    poppy.m4.compliant = False
    poppy.m5.compliant = False
    poppy.m6.compliant = False

    print("Система запущена. Покажи ладонь или кулак.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        raw_state = detector.infer(frame)
        confirmed = deb.update(raw_state)

        if confirmed == "OPEN":
            print("CONFIRMED: OPEN")
            gripper.open()

        elif confirmed == "CLOSE":
            print("CONFIRMED: CLOSE")
            gripper.close()

        time.sleep(0.02)

if __name__ == "__main__":
    main()