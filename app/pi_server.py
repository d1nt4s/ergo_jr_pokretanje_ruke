# pi_server.py
import cv2
import threading
import time
import signal
import sys
from flask import Flask, Response, request, jsonify
from pypot.creatures import PoppyErgoJr

app = Flask(__name__)

# ---------------- Camera (OPEN ONCE + background thread) ----------------
CAMERA_INDEX = 0
JPEG_QUALITY = 80

cap = None
last_frame = None
frame_lock = threading.Lock()
running = True


def camera_loop():
    global last_frame, running
    while running:
        ret, frame = cap.read()
        if ret:
            with frame_lock:
                last_frame = frame
        else:
            time.sleep(0.02)


def start_camera():
    global cap
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index={CAMERA_INDEX}")
    # smaller internal buffer to reduce lag
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass

    t = threading.Thread(target=camera_loop, daemon=True)
    t.start()


# ---------------- Robot ----------------
poppy = PoppyErgoJr(camera="dummy")

# Wake up: stiff motors + neutral pose
for m in poppy.motors:
    m.compliant = False
    m.moving_speed = 30

neutral = {"m1": 0, "m2": 0, "m3": 0, "m4": 0, "m5": 0, "m6": 30}
for name, angle in neutral.items():
    getattr(poppy, name).goal_position = angle

gripper = poppy.m6
gripper.compliant = False
gripper.moving_speed = 40

print("Robot awake: motors stiff + neutral pose set")


def go_to_rest():
    print("Going to rest: motors compliant (with settle delay)")
    # IMPORTANT: give it a moment before/after setting compliant
    try:
        for m in poppy.motors:
            m.compliant = True
    except Exception as e:
        print("Rest error:", e)

    time.sleep(2.0)

    # debug print
    try:
        for m in poppy.motors:
            print("REST:", m.name, "compliant=", m.compliant)
    except Exception:
        pass


def shutdown():
    global running
    running = False
    try:
        go_to_rest()
    finally:
        try:
            if cap is not None:
                cap.release()
        except Exception:
            pass


def handle_exit(sig, frame):
    print("\nStopping server safely...")
    shutdown()
    sys.exit(0)


signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


# ---------------- Routes ----------------
@app.route("/frame", methods=["GET"])
def frame():
    with frame_lock:
        frame = last_frame

    if frame is None:
        return ("no frame yet", 503)

    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
    if not ok:
        return ("encode failed", 500)

    return Response(buf.tobytes(), mimetype="image/jpeg")


@app.route("/command", methods=["POST"])
def command():
    data = request.get_json(silent=True) or {}
    cmd = data.get("cmd")

    if cmd == "OPEN":
        gripper.goal_position = 30
    elif cmd == "CLOSE":
        gripper.goal_position = 90
    elif cmd == "REST":
        go_to_rest()
    elif cmd == "WAKE":
        # re-wake
        for m in poppy.motors:
            m.compliant = False
            m.moving_speed = 30
        for name, angle in neutral.items():
            getattr(poppy, name).goal_position = angle

    return jsonify({"status": "ok", "cmd": cmd})


if __name__ == "__main__":
    try:
        start_camera()
        print("Pi server running on http://10.99.99.1:5000")
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=True)
    finally:
        shutdown()