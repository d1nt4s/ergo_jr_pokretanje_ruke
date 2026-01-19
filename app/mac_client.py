# mac_client.py
import cv2
import requests
import mediapipe as mp
import numpy as np
import time

PI_URL = "http://10.99.99.1:5000"

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.6, min_tracking_confidence=0.6)

def get_frame():
    try:
        r = requests.get(f"{PI_URL}/frame", timeout=3)
        if r.status_code != 200:
            return None
        img = np.frombuffer(r.content, dtype=np.uint8)
        frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
        return frame
    except requests.RequestException:
        return None

def send(cmd):
    try:
        requests.post(f"{PI_URL}/command", json={"cmd": cmd}, timeout=2)
    except requests.RequestException:
        pass

def detect_open_close(frame_bgr):
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    res = hands.process(rgb)

    if not res.multi_hand_landmarks:
        return None, frame_bgr

    lm = res.multi_hand_landmarks[0].landmark

    # count fingers (simple)
    fingers = 0
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    for t, p in zip(tips, pips):
        if lm[t].y < lm[p].y:
            fingers += 1

    # draw landmarks for debugging
    mp.solutions.drawing_utils.draw_landmarks(
        frame_bgr,
        res.multi_hand_landmarks[0],
        mp_hands.HAND_CONNECTIONS
    )

    if fingers >= 4:
        return "OPEN", frame_bgr
    elif fingers <= 1:
        return "CLOSE", frame_bgr
    else:
        return None, frame_bgr

# --- Debounce / anti-spam ---
last_sent = None
stable_state = None
stable_count = 0
NEED_STABLE_FRAMES = 5   # must be same state 5 frames in a row
SEND_COOLDOWN = 0.6      # seconds between sends
last_send_time = 0.0

while True:
    frame = get_frame()
    if frame is None:
        print("No frame... retry")
        time.sleep(0.1)
        continue

    state, vis = detect_open_close(frame)

    # show video so you see it's live
    cv2.putText(vis, f"state={state}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Pi Camera (via server)", vis)

    # quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    # debounce logic
    if state is None:
        stable_state = None
        stable_count = 0
        continue

    if state == stable_state:
        stable_count += 1
    else:
        stable_state = state
        stable_count = 1

    # send only if stable enough + cooldown + changed
    now = time.time()
    if stable_count >= NEED_STABLE_FRAMES:
        if stable_state != last_sent and (now - last_send_time) > SEND_COOLDOWN:
            print("SEND:", stable_state)
            send(stable_state)
            last_sent = stable_state
            last_send_time = now

cv2.destroyAllWindows()