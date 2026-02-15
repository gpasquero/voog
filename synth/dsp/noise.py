import numpy as np


class NoiseGenerator:
    def __init__(self):
        self.noise_type = "white"  # white | pink
        self.level = 0.0
        # Pink noise state (Paul Kellet's approximation)
        self._b0 = 0.0
        self._b1 = 0.0
        self._b2 = 0.0
        self._b3 = 0.0
        self._b4 = 0.0
        self._b5 = 0.0
        self._b6 = 0.0

    def render(self, n_samples: int) -> np.ndarray:
        if self.level <= 0.0:
            return np.zeros(n_samples, dtype=np.float64)

        white = np.random.uniform(-1.0, 1.0, n_samples)

        if self.noise_type == "pink":
            out = np.empty(n_samples, dtype=np.float64)
            b0, b1, b2, b3, b4, b5, b6 = (
                self._b0, self._b1, self._b2, self._b3, self._b4, self._b5, self._b6,
            )
            for i in range(n_samples):
                w = white[i]
                b0 = 0.99886 * b0 + w * 0.0555179
                b1 = 0.99332 * b1 + w * 0.0750759
                b2 = 0.96900 * b2 + w * 0.1538520
                b3 = 0.86650 * b3 + w * 0.3104856
                b4 = 0.55000 * b4 + w * 0.5329522
                b5 = -0.7616 * b5 - w * 0.0168980
                out[i] = b0 + b1 + b2 + b3 + b4 + b5 + b6 + w * 0.5362
                b6 = w * 0.115926
            self._b0, self._b1, self._b2, self._b3 = b0, b1, b2, b3
            self._b4, self._b5, self._b6 = b4, b5, b6
            out *= 0.11  # Normalize
            return out * self.level
        else:
            return white * self.level

    def reset(self):
        self._b0 = self._b1 = self._b2 = self._b3 = 0.0
        self._b4 = self._b5 = self._b6 = 0.0
