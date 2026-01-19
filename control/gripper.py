"""Gripper control for Poppy Ergo Jr.

This module is intentionally small and explicit:
- It connects to the robot (PoppyErgoJr) on Raspberry Pi (Poppy OS)
- It finds the motor responsible for the gripper (by name, e.g. 'm6')
- It exposes high-level actions: open() and close()

Safety notes:
- Do NOT run open()/close() before the robot is fully assembled and calibrated.
- Use `dry_run=True` to test the pipeline without moving any hardware.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

try:
    # Available on Raspberry Pi with Poppy OS
    from pypot.creatures import PoppyErgoJr
except Exception:  # pragma: no cover
    PoppyErgoJr = None  # Allows importing this file on a dev machine (Mac/Windows).


@dataclass
class GripperConfig:
    motor_name: str = "m6"  # will be confirmed later (list motors after connect)
    open_angle: float = 90.0
    close_angle: float = 10.0
    speed: int = 50
    # Optional safety clamp. Tune after calibration if needed.
    min_angle: float = -150.0
    max_angle: float = 150.0


class GripperController:
    """Small wrapper around a single Dynamixel motor used as a gripper."""

    def __init__(self, config: GripperConfig | None = None, *, dry_run: bool = False):
        self.config = config or GripperConfig()
        self.dry_run = dry_run

        self.poppy = None
        self.m = None

    # ----------------------------- connection helpers -----------------------------
    def connect(self):
        """Connect to the robot and bind the configured motor.

        Must be executed on Raspberry Pi with Poppy OS.
        """
        if PoppyErgoJr is None:
            raise RuntimeError(
                "Poppy libraries not available in this environment. "
                "Run on Raspberry Pi (Poppy OS) and open via poppy.local."
            )

        self.poppy = PoppyErgoJr(camera='dummy')
        self.m = getattr(self.poppy, self.config.motor_name, None)
        if self.m is None:
            raise RuntimeError(
                f"Motor '{self.config.motor_name}' not found. Available motors: {self.list_motor_names()}"
            )

    def is_connected(self) -> bool:
        return self.poppy is not None and self.m is not None

    def list_motor_names(self) -> List[str]:
        """Return a list of motor names (e.g. ['m1','m2',...])."""
        if self.poppy is None:
            # If not connected, we can't query the robot
            return []
        return [mot.name for mot in self.poppy.motors]

    # ----------------------------- motor config -----------------------------
    def set_compliant(self, compliant: bool):
        """Set compliant mode.

        compliant=True  -> motor is "soft" (doesn't hold position strongly)
        compliant=False -> motor holds target position
        """
        self._require_connected()
        if self.dry_run:
            print(f"[DRY_RUN] set_compliant({compliant})")
            return
        self.m.compliant = compliant

    # ----------------------------- actions -----------------------------
    def open(self):
        """Open the gripper (move motor to config.open_angle)."""
        self._move_to(self.config.open_angle, label="OPEN")

    def close(self):
        """Close the gripper (move motor to config.close_angle)."""
        self._move_to(self.config.close_angle, label="CLOSE")

    # ----------------------------- internals -----------------------------
    def _require_connected(self):
        if not self.is_connected():
            raise RuntimeError("GripperController is not connected. Call connect() first.")

    def _clamp(self, angle: float) -> float:
        return max(self.config.min_angle, min(self.config.max_angle, angle))

    def _move_to(self, angle: float, *, label: str):
        self._require_connected()
        target = self._clamp(angle)

        if self.dry_run:
            print(f"[DRY_RUN] {label}: moving motor {self.config.motor_name} to {target} deg (speed={self.config.speed})")
            return

        # NOTE: moving_speed and goal_position are the standard knobs in Poppy notebooks.
        self.m.moving_speed = self.config.speed
        self.m.goal_position = target