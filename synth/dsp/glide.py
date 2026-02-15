import numpy as np
from ..config import SAMPLE_RATE


class Glide:
    def __init__(self):
        self.time = 0.0         # seconds
        self.mode = "off"       # off, always, legato
        self._current_freq = 0.0
        self._target_freq = 0.0

    def set_target(self, freq: float, legato: bool = False):
        if self.mode == "off" or self._current_freq <= 0.0:
            self._current_freq = freq
            self._target_freq = freq
        elif self.mode == "always" or (self.mode == "legato" and legato):
            self._target_freq = freq
        else:
            self._current_freq = freq
            self._target_freq = freq

    def render(self, n_samples: int) -> np.ndarray:
        """Return per-sample frequency array."""
        if self.time <= 0.0 or self._current_freq == self._target_freq:
            self._current_freq = self._target_freq
            return np.full(n_samples, self._target_freq, dtype=np.float64)

        out = np.empty(n_samples, dtype=np.float64)
        # Exponential glide in log-frequency domain
        coeff = 1.0 - np.exp(-1.0 / (self.time * SAMPLE_RATE))
        for i in range(n_samples):
            self._current_freq += (self._target_freq - self._current_freq) * coeff
            out[i] = self._current_freq

        if abs(self._current_freq - self._target_freq) < 0.01:
            self._current_freq = self._target_freq

        return out

    def reset(self):
        self._current_freq = 0.0
        self._target_freq = 0.0
