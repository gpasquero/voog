import numpy as np
from ..config import SAMPLE_RATE, CONTROL_RATE_DIVIDER

# Minimum time to avoid division by zero
_MIN_TIME = 0.001


class ADSR:
    def __init__(self, attack=0.01, decay=0.1, sustain=0.7, release=0.3):
        self.attack = attack    # seconds
        self.decay = decay      # seconds
        self.sustain = sustain   # 0..1
        self.release = release   # seconds
        self._state = "idle"     # idle, attack, decay, sustain, release
        self._level = 0.0
        self._samples_in_state = 0

    def gate_on(self):
        self._state = "attack"
        self._samples_in_state = 0

    def gate_off(self):
        if self._state != "idle":
            self._state = "release"
            self._samples_in_state = 0

    def is_active(self) -> bool:
        return self._state != "idle"

    def render(self, n_samples: int) -> np.ndarray:
        """Render envelope at control rate, then interpolate to audio rate."""
        n_blocks = n_samples // CONTROL_RATE_DIVIDER
        remainder = n_samples % CONTROL_RATE_DIVIDER
        total_blocks = n_blocks + (1 if remainder else 0)

        control_values = np.empty(total_blocks, dtype=np.float64)

        for i in range(total_blocks):
            block_size = CONTROL_RATE_DIVIDER if i < n_blocks else remainder
            self._advance(block_size)
            control_values[i] = self._level

        # Interpolate control values to audio rate
        if total_blocks <= 1:
            return np.full(n_samples, self._level, dtype=np.float64)

        # Each control value represents a block of CONTROL_RATE_DIVIDER samples
        out = np.empty(n_samples, dtype=np.float64)
        pos = 0
        for i in range(total_blocks):
            block_size = CONTROL_RATE_DIVIDER if i < n_blocks else remainder
            if block_size == 0:
                continue
            if i == 0:
                out[pos:pos + block_size] = control_values[i]
            else:
                prev = control_values[i - 1]
                cur = control_values[i]
                # Linear ramp without np.linspace overhead
                t = np.arange(block_size, dtype=np.float64) / block_size
                out[pos:pos + block_size] = prev + (cur - prev) * t
            pos += block_size
        return out

    def _advance(self, n_samples: int):
        self._samples_in_state += n_samples
        if self._state == "attack":
            rate = max(self.attack, _MIN_TIME) * SAMPLE_RATE
            self._level += n_samples / rate
            if self._level >= 1.0:
                self._level = 1.0
                self._state = "decay"
                self._samples_in_state = 0
        elif self._state == "decay":
            rate = max(self.decay, _MIN_TIME) * SAMPLE_RATE
            self._level -= (1.0 - self.sustain) * n_samples / rate
            if self._level <= self.sustain:
                self._level = self.sustain
                self._state = "sustain"
                self._samples_in_state = 0
        elif self._state == "sustain":
            self._level = self.sustain
        elif self._state == "release":
            rate = max(self.release, _MIN_TIME) * SAMPLE_RATE
            self._level -= self._level * n_samples / rate
            if self._level < 1e-5:
                self._level = 0.0
                self._state = "idle"
                self._samples_in_state = 0

    def reset(self):
        self._state = "idle"
        self._level = 0.0
        self._samples_in_state = 0
