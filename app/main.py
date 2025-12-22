# app/main.py
import time
from utils.debounce import Debounce
from control.gripper import GripperController

def main():
    # 1) подключаем гриппер (на Pi)
    gripper = GripperController(gripper_motor_name="m6")
    gripper.connect()

    # 2) фильтр от дребезга
    deb = Debounce(stable_frames=5)

    # 3) главный цикл (пока вместо vision пусть будет “ручная подмена”)
    while True:
        # TODO: заменить на реальный state из vision
        raw = "UNKNOWN"

        confirmed = deb.update(raw)
        if confirmed == "OPEN":
            gripper.open()
        elif confirmed == "CLOSE":
            gripper.close()

        time.sleep(0.02)

if __name__ == "__main__":
    main()