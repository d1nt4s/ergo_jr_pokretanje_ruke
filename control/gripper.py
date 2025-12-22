# control/gripper.py
from typing import Optional

try:
    from pypot.creatures import PoppyErgoJr
except Exception:
    PoppyErgoJr = None  # чтобы файл хотя бы импортировался локально

class GripperController:
    def __init__(self, gripper_motor_name: str = "m6"):
        self.gripper_motor_name = gripper_motor_name
        self.poppy = None
        self.m = None

        # Эти углы вы потом подберёте после сборки (безопасно, маленькими шагами!)
        self.open_angle = 30.0
        self.close_angle = 90.0
        self.speed = 50

    def connect(self):
        if PoppyErgoJr is None:
            raise RuntimeError("Poppy libraries not available in this environment. Run on Raspberry Pi (Poppy OS).")

        self.poppy = PoppyErgoJr()
        # Можно вернуть в rest posture, но ДВИЖЕНИЯ — только когда робот собран и откалиброван!
        # self.poppy.rest_posture.start()

        self.m = getattr(self.poppy, self.gripper_motor_name, None)
        if self.m is None:
            names = [mot.name for mot in self.poppy.motors]
            raise RuntimeError(f"Motor {self.gripper_motor_name} not found. Available: {names}")

    def set_compliant(self, compliant: bool):
        if self.m is None:
            raise RuntimeError("Not connected")
        self.m.compliant = compliant

    def open(self):
        if self.m is None:
            raise RuntimeError("Not connected")
        self.m.moving_speed = self.speed
        self.m.goal_position = self.open_angle

    def close(self):
        if self.m is None:
            raise RuntimeError("Not connected")
        self.m.moving_speed = self.speed
        self.m.goal_position = self.close_angle