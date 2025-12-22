# utils/debounce.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Debounce:
    stable_frames: int = 5

    _last_raw: Optional[str] = None
    _count: int = 0
    _applied: Optional[str] = None  # что уже реально отправили на гриппер

    def update(self, raw: str) -> Optional[str]:
        """raw: 'OPEN' | 'CLOSE' | 'UNKNOWN' -> returns confirmed 'OPEN'/'CLOSE' or None"""
        if raw not in ("OPEN", "CLOSE"):
            # UNKNOWN не ломает состояние, просто игнор
            return None

        if raw == self._last_raw:
            self._count += 1
        else:
            self._last_raw = raw
            self._count = 1

        if self._count >= self.stable_frames and raw != self._applied:
            self._applied = raw
            return raw

        return None