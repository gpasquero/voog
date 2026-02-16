import numpy as np
from ..config import SAMPLE_RATE, WAVETABLE_SIZE

# Pre-computed wavetables (band-limited via additive synthesis)
_TABLES: dict[str, np.ndarray] = {}


def _build_tables():
    phase = np.linspace(0.0, 1.0, WAVETABLE_SIZE, endpoint=False, dtype=np.float64)
    # Sine
    _TABLES["sine"] = np.sin(2.0 * np.pi * phase)
    # Saw – additive (enough harmonics for audible range)
    saw = np.zeros(WAVETABLE_SIZE, dtype=np.float64)
    for k in range(1, 64):
        saw += ((-1.0) ** (k + 1)) * np.sin(2.0 * np.pi * k * phase) / k
    _TABLES["saw"] = saw * (2.0 / np.pi)
    # Square – odd harmonics
    sq = np.zeros(WAVETABLE_SIZE, dtype=np.float64)
    for k in range(1, 64, 2):
        sq += np.sin(2.0 * np.pi * k * phase) / k
    _TABLES["square"] = sq * (4.0 / np.pi)
    # Triangle – odd harmonics, alternating sign
    tri = np.zeros(WAVETABLE_SIZE, dtype=np.float64)
    for k in range(1, 64, 2):
        sign = (-1.0) ** ((k - 1) // 2)
        tri += sign * np.sin(2.0 * np.pi * k * phase) / (k * k)
    _TABLES["triangle"] = tri * (8.0 / (np.pi * np.pi))


_build_tables()

WAVEFORMS = list(_TABLES.keys())


class Oscillator:
    def __init__(self):
        self.waveform: str = "saw"
        self.octave: int = 0          # -2..+2
        self.semitone: int = 0        # -12..+12
        self.detune: float = 0.0      # cents
        self.level: float = 1.0
        self.pulse_width: float = 0.5  # for future PWM
        self.phase: float = 0.0       # 0..1 accumulator

    def render(self, freq: float, n_samples: int, pitch_mod: np.ndarray | None = None) -> np.ndarray:
        """Render n_samples at the given base frequency (Hz). Returns mono float64 array."""
        # Apply octave, semitone, detune
        f = freq * (2.0 ** self.octave) * (2.0 ** (self.semitone / 12.0)) * (2.0 ** (self.detune / 1200.0))
        if self.level <= 0.0:
            return np.zeros(n_samples, dtype=np.float64)

        table = _TABLES.get(self.waveform, _TABLES["saw"])
        ts = WAVETABLE_SIZE

        # Phase increment per sample
        if pitch_mod is not None:
            # pitch_mod in semitones
            freqs = f * (2.0 ** (pitch_mod / 12.0))
            increments = freqs / SAMPLE_RATE
        else:
            increments = np.full(n_samples, f / SAMPLE_RATE, dtype=np.float64)

        # Build phase ramp (vectorized)
        # phases[i] is the phase at sample i, before adding increments[i]
        cumulative = np.cumsum(increments)
        phases = (self.phase + cumulative - increments) % 1.0
        self.phase = float((self.phase + cumulative[-1]) % 1.0)

        # Wavetable lookup with linear interpolation
        idx_f = phases * ts
        idx_i = idx_f.astype(np.int32)
        frac = idx_f - idx_i
        idx_next = (idx_i + 1) % ts
        idx_i = idx_i % ts
        out = table[idx_i] * (1.0 - frac) + table[idx_next] * frac

        return out * self.level

    def reset_phase(self):
        self.phase = 0.0
