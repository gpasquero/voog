from ..config import NUM_CHANNELS


class MidiRouter:
    """Routes MIDI channels to synth channels.

    By default MIDI channel N maps to synth channel N (mod NUM_CHANNELS).
    Custom mappings can be set.
    """

    def __init__(self):
        # midi_channel → synth_channel
        self._mapping: dict[int, int] = {}

    def route(self, midi_channel: int) -> int:
        if midi_channel in self._mapping:
            return self._mapping[midi_channel]
        return midi_channel % NUM_CHANNELS

    def set_mapping(self, midi_channel: int, synth_channel: int):
        self._mapping[midi_channel] = synth_channel % NUM_CHANNELS

    def clear_mappings(self):
        self._mapping.clear()
