from ..config import MAX_VOICES
from .voice import Voice


class VoiceAllocator:
    """Polyphonic voice allocator with voice stealing (oldest-note strategy)."""

    def __init__(self, max_voices: int = MAX_VOICES):
        self.max_voices = max_voices
        self.voices = [Voice() for _ in range(max_voices)]
        self._age_counter = 0
        self._voice_ages: list[int] = [0] * max_voices
        self._held_notes: list[int] = []  # for legato detection

    def note_on(self, note: int, velocity: int) -> Voice:
        legato = len(self._held_notes) > 0
        self._held_notes.append(note)

        # 1. Re-use voice already playing this note
        for i, v in enumerate(self.voices):
            if v.note == note and v.active:
                v.note_on(note, velocity, legato=legato)
                self._age_counter += 1
                self._voice_ages[i] = self._age_counter
                return v

        # 2. Find a free voice
        for i, v in enumerate(self.voices):
            if not v.active:
                v.note_on(note, velocity, legato=legato)
                self._age_counter += 1
                self._voice_ages[i] = self._age_counter
                return v

        # 3. Voice stealing – steal the oldest active voice
        oldest_idx = 0
        oldest_age = self._voice_ages[0]
        for i in range(1, self.max_voices):
            if self._voice_ages[i] < oldest_age:
                oldest_age = self._voice_ages[i]
                oldest_idx = i
        v = self.voices[oldest_idx]
        v.reset()
        v.note_on(note, velocity, legato=legato)
        self._age_counter += 1
        self._voice_ages[oldest_idx] = self._age_counter
        return v

    def note_off(self, note: int):
        if note in self._held_notes:
            self._held_notes.remove(note)
        for v in self.voices:
            if v.note == note and v.active:
                v.note_off()

    def all_notes_off(self):
        self._held_notes.clear()
        for v in self.voices:
            if v.active:
                v.note_off()

    def active_voice_count(self) -> int:
        return sum(1 for v in self.voices if v.active)
