import numpy as np
from ..config import SAMPLE_RATE, CONTROL_RATE_DIVIDER

_TWO_PI = 2.0 * np.pi


class LFO:
    def __init__(self):
        self.waveform = "sine"    # sine, triangle, saw, square
        self.rate = 1.0           # Hz
        self.depth = 0.0          # 0..1
        self.destination = "filter"  # filter, pitch, amp
        self.key_sync = True
        self._phase = 0.0

    def render(self, n_samples: int) -> np.ndarray:
        """Return modulation signal (-1..+1) * depth at audio rate."""
        if self.depth <= 0.0:
            return np.zeros(n_samples, dtype=np.float64)

        # Generate at control rate, then interpolate
        n_blocks = n_samples // CONTROL_RATE_DIVIDER
        remainder = n_samples % CONTROL_RATE_DIVIDER
        total = n_blocks + (1 if remainder else 0)

        ctrl = np.empty(total, dtype=np.float64)
        phase_inc = self.rate * CONTROL_RATE_DIVIDER / SAMPLE_RATE

        for i in range(total):
            ctrl[i] = self._sample(self._phase)
            self._phase += phase_inc
            if self._phase >= 1.0:
                self._phase -= 1.0

        # Interpolate to audio rate
        out = np.empty(n_samples, dtype=np.float64)
        pos = 0
        for i in range(total):
            bs = CONTROL_RATE_DIVIDER if i < n_blocks else remainder
            if bs == 0:
                continue
            if i == 0:
                out[pos:pos + bs] = ctrl[i]
            else:
                out[pos:pos + bs] = np.linspace(ctrl[i - 1], ctrl[i], bs, endpoint=False)
            pos += bs

        return out * self.depth

    def _sample(self, phase: float) -> float:
        if self.waveform == "sine":
            return np.sin(_TWO_PI * phase)
        elif self.waveform == "triangle":
            return 4.0 * abs(phase - 0.5) - 1.0
        elif self.waveform == "saw":
            return 2.0 * phase - 1.0
        elif self.waveform == "square":
            return 1.0 if phase < 0.5 else -1.0
        return 0.0

    def reset(self):
        self._phase = 0.0
