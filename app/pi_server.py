# pi_server.py
import cv2
from flask import Flask, Response, request, jsonify
from pypot.creatures import PoppyErgoJr

app = Flask(__name__)

# --- Camera ---
cap = cv2.VideoCapture(0)

# --- Robot ---
poppy = PoppyErgoJr()
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
    print("Pi server running on http://poppy.local:5000")
    app.run(host="0.0.0.0", port=5000)