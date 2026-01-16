# pi_server.py
import cv2
from flask import Flask, Response, request, jsonify
from pypot.creatures import PoppyErgoJr
import signal
import sys
import time

app = Flask(__name__)

# --- Camera ---
cap = cv2.VideoCapture(0)

# --- Robot ---
poppy = PoppyErgoJr(camera='dummy')

# Wake up: make motors stiff and move to neutral pose
for m in poppy.motors:
    m.compliant = False
    m.moving_speed = 30

neutral = {
    "m1": 0,
    "m2": 0,
    "m3": 0,
    "m4": 0,
    "m5": 0,
    "m6": 30,  # gripper slightly open
}

for name, angle in neutral.items():
    getattr(poppy, name).goal_position = angle

print("Robot awake: motors stiff + neutral pose set")

def go_to_rest():
    print("Going to rest: motors compliant (with settle delay)")

    # 1) (опционально) чуть разгрузить позой, чтобы лучше “отпустило”
    try:
        # Если не хочешь двигать — закомментируй этот блок
        poppy.moving_speed = 20  # иногда есть, иногда нет — не критично
    except Exception:
        pass

    try:
        # Мягкая “разгрузочная” поза (можешь подправить углы)
        # Важно: делаем только если моторы были stiff
        for m in poppy.motors:
            m.compliant = False
            m.moving_speed = 20

        # Поза без сильного напряжения (пример)
        if hasattr(poppy, "m2"): poppy.m2.goal_position = -30
        if hasattr(poppy, "m3"): poppy.m3.goal_position =  30
        if hasattr(poppy, "m4"): poppy.m4.goal_position =  20
        time.sleep(1.0)
    except Exception as e:
        print("Rest pre-pose skipped:", e)

    # 2) Главный шаг: отпустить моторы
    for m in poppy.motors:
        try:
            m.compliant = True
        except Exception as e:
            print("SET ERROR", m.name, e)

    # 3) КЛЮЧ: дать физике “догнать” режим
    time.sleep(2.0)

    # 4) Контроль (полезно для уверенности)
    try:
        for m in poppy.motors:
            print("REST:", m.name, "compliant=", m.compliant)
    except Exception:
        pass


def handle_exit(sig, frame):
    print("\nCtrl+C detected, shutting down safely...")
    try:
        go_to_rest()
    finally:
        try:
            cap.release()
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

gripper = poppy.m6
gripper.compliant = False
gripper.moving_speed = 40

def get_frame():
    ret, frame = cap.read()
    if not ret:
        return None
    _, jpeg = cv2.imencode(".jpg", frame)
    return jpeg.tobytes()

@app.route("/frame")
def frame():
    img = get_frame()
    return Response(img, mimetype="image/jpeg")

@app.route("/command", methods=["POST"])
def command():
    cmd = request.json.get("cmd")
    if cmd == "OPEN":
        gripper.goal_position = 30
    elif cmd == "CLOSE":
        gripper.goal_position = 90
    return jsonify({"status": "ok", "cmd": cmd})

if __name__ == "__main__":
    try:
        print("Pi server running on http://poppy.local:5000")
        app.run(host="0.0.0.0", port=5000)
    finally:
        # если вдруг вылетели не через Ctrl+C
        try:
            go_to_rest()
        except Exception:
            pass
        try:
            cap.release()
        except Exception:
            pass
