import numpy as np
from ..config import MAX_VOICES
from ..patch.patch import Patch
from .voice_allocator import VoiceAllocator


class Channel:
    """A multitimbral channel: owns a patch and a voice allocator."""

    def __init__(self, channel_id: int = 0):
        self.channel_id = channel_id
        self.patch = Patch()
        self.allocator = VoiceAllocator(MAX_VOICES)
        self.volume = 1.0
        self._apply_patch()

    def set_patch(self, patch: Patch):
        self.patch = patch
        self._apply_patch()

    def _apply_patch(self):
        for voice in self.allocator.voices:
            voice.apply_patch(self.patch)

    def note_on(self, note: int, velocity: int):
        v = self.allocator.note_on(note, velocity)
        v.apply_patch(self.patch)

    def note_off(self, note: int):
        self.allocator.note_off(note)

    def all_notes_off(self):
        self.allocator.all_notes_off()

    def set_param(self, param: str, value: float):
        """Set a patch parameter by dotted path, e.g. 'filter.cutoff'."""
        parts = param.split(".")
        obj = self.patch
        for part in parts[:-1]:
            if part.startswith("osc") and part[-1].isdigit():
                idx = int(part[-1]) - 1
                obj = obj.oscillators[idx]
            else:
                obj = getattr(obj, part)
        setattr(obj, parts[-1], value)
        # Re-apply to all voices
        self._apply_patch()

    def render(self, n_samples: int) -> np.ndarray:
        out = np.zeros(n_samples, dtype=np.float64)
        for voice in self.allocator.voices:
            if voice.active:
                out += voice.render(n_samples)
        return out * self.volume * self.patch.master_volume
