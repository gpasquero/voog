import numpy as np
from ..config import SAMPLE_RATE, NUM_OSCILLATORS, A4_FREQ
from ..dsp.oscillator import Oscillator
from ..dsp.envelope import ADSR
from ..dsp.filter import MoogFilter
from ..dsp.noise import NoiseGenerator
from ..dsp.lfo import LFO
from ..dsp.glide import Glide
from ..patch.patch import Patch


def midi_to_freq(note: int) -> float:
    return A4_FREQ * (2.0 ** ((note - 69) / 12.0))


class Voice:
    def __init__(self):
        self.oscillators = [Oscillator() for _ in range(NUM_OSCILLATORS)]
        self.noise = NoiseGenerator()
        self.moog_filter = MoogFilter()
        self.amp_env = ADSR()
        self.filter_env = ADSR()
        self.lfo = LFO()
        self.glide = Glide()

        self.note: int = -1
        self.velocity: float = 0.0
        self.active: bool = False
        self._base_freq: float = 0.0

        # Pre-allocated buffers
        self._mix_buf: np.ndarray | None = None

    def apply_patch(self, patch: Patch):
        for i, osc in enumerate(self.oscillators):
            if i < len(patch.oscillators):
                op = patch.oscillators[i]
                osc.waveform = op.waveform
                osc.octave = op.octave
                osc.semitone = op.semitone
                osc.detune = op.detune
                osc.level = op.level
                osc.pulse_width = op.pulse_width
        self.noise.noise_type = patch.noise.noise_type
        self.noise.level = patch.noise.level
        self.moog_filter.cutoff = patch.filter.cutoff
        self.moog_filter.resonance = patch.filter.resonance
        self.moog_filter.env_amount = patch.filter.env_amount
        self.moog_filter.key_tracking = patch.filter.key_tracking
        self.amp_env.attack = patch.amp_adsr.attack
        self.amp_env.decay = patch.amp_adsr.decay
        self.amp_env.sustain = patch.amp_adsr.sustain
        self.amp_env.release = patch.amp_adsr.release
        self.filter_env.attack = patch.filter_adsr.attack
        self.filter_env.decay = patch.filter_adsr.decay
        self.filter_env.sustain = patch.filter_adsr.sustain
        self.filter_env.release = patch.filter_adsr.release
        self.lfo.waveform = patch.lfo.waveform
        self.lfo.rate = patch.lfo.rate
        self.lfo.depth = patch.lfo.depth
        self.lfo.destination = patch.lfo.destination
        self.lfo.key_sync = patch.lfo.key_sync
        self.glide.time = patch.glide.time
        self.glide.mode = patch.glide.mode

    def note_on(self, note: int, velocity: int, legato: bool = False):
        self.note = note
        self.velocity = velocity / 127.0
        self._base_freq = midi_to_freq(note)
        self.active = True
        self.glide.set_target(self._base_freq, legato=legato)
        self.amp_env.gate_on()
        self.filter_env.gate_on()
        if self.lfo.key_sync:
            self.lfo.reset()
        if not legato:
            for osc in self.oscillators:
                osc.reset_phase()

    def note_off(self):
        self.amp_env.gate_off()
        self.filter_env.gate_off()

    def render(self, n_samples: int) -> np.ndarray:
        if not self.active:
            return np.zeros(n_samples, dtype=np.float64)

        # Amp envelope
        amp_env = self.amp_env.render(n_samples)
        if not self.amp_env.is_active() and np.max(amp_env) < 1e-5:
            self.active = False
            return np.zeros(n_samples, dtype=np.float64)

        # Filter envelope
        filt_env = self.filter_env.render(n_samples)

        # LFO
        lfo_out = self.lfo.render(n_samples)

        # Pitch modulation from LFO
        pitch_mod = None
        if self.lfo.destination == "pitch" and self.lfo.depth > 0:
            pitch_mod = lfo_out * 12.0  # LFO depth scales to semitones

        # Glide
        freq_buf = self.glide.render(n_samples)

        # Mix oscillators
        mix = np.zeros(n_samples, dtype=np.float64)
        for osc in self.oscillators:
            if osc.level > 0.0:
                # Use mean frequency for the buffer (glide is slow-moving)
                mean_freq = float(np.mean(freq_buf))
                mix += osc.render(mean_freq, n_samples, pitch_mod)

        # Add noise
        if self.noise.level > 0.0:
            mix += self.noise.render(n_samples)

        # Filter modulation
        # env_amount in semitones → convert to Hz offset
        base_cutoff = self.moog_filter.cutoff
        # Key tracking
        if self.moog_filter.key_tracking > 0:
            kt_offset = (self._base_freq - A4_FREQ) * self.moog_filter.key_tracking
            base_cutoff += kt_offset

        cutoff_mod = np.zeros(n_samples, dtype=np.float64)
        if self.moog_filter.env_amount != 0.0:
            # Convert envelope (0..1) to frequency offset
            env_freq = base_cutoff * (2.0 ** (filt_env * self.moog_filter.env_amount / 12.0) - 1.0)
            cutoff_mod += env_freq
        if self.lfo.destination == "filter" and self.lfo.depth > 0:
            lfo_freq = base_cutoff * (2.0 ** (lfo_out * 2.0 / 12.0) - 1.0)
            cutoff_mod += lfo_freq

        # Apply filter
        filtered = self.moog_filter.render(mix, cutoff_mod if np.any(cutoff_mod) else None)

        # Amp modulation from LFO
        if self.lfo.destination == "amp" and self.lfo.depth > 0:
            amp_lfo = 1.0 + lfo_out * 0.5  # Tremolo
            filtered *= amp_lfo

        # Apply amp envelope and velocity
        return filtered * amp_env * self.velocity

    def reset(self):
        self.note = -1
        self.velocity = 0.0
        self.active = False
        self.amp_env.reset()
        self.filter_env.reset()
        self.lfo.reset()
        self.glide.reset()
        self.moog_filter.reset()
        self.noise.reset()
        for osc in self.oscillators:
            osc.reset_phase()
