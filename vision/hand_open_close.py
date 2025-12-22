# vision/hand_open_close.py
from typing import Literal, Optional
State = Literal["OPEN", "CLOSE", "UNKNOWN"]

def classify_hand_state(landmarks) -> State:
    """
    landmarks: точки руки из MediaPipe.
    Возвращает OPEN/CLOSE/UNKNOWN.
    Реализацию сделаем простой: считаем поднятые пальцы.
    """
    # TODO: реализовать “finger up” логику (я дам готовую формулу следующим шагом)
    return "UNKNOWN"