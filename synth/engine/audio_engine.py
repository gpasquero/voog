import collections
import numpy as np
import sounddevice as sd
from ..config import SAMPLE_RATE, BUFFER_SIZE, NUM_CHANNELS, MIDI_QUEUE_SIZE
from .channel import Channel


class AudioEngine:
    """Master audio engine: manages channels, processes MIDI queue, drives audio output."""

    def __init__(self):
        self.channels = [Channel(i) for i in range(NUM_CHANNELS)]
        self.midi_queue: collections.deque = collections.deque(maxlen=MIDI_QUEUE_SIZE)
        self._stream: sd.OutputStream | None = None
        self._running = False
        self._master_volume = 0.8
        self._peak_level = 0.0

    def start(self):
        self._running = True
        self._stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BUFFER_SIZE,
            channels=1,
            dtype="float32",
            callback=self._audio_callback,
            latency="low",
        )
        self._stream.start()

    def stop(self):
        self._running = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        for ch in self.channels:
            ch.all_notes_off()

    def _audio_callback(self, outdata, frames, time_info, status):
        """Called by sounddevice from the audio thread."""
        # Drain MIDI queue
        while self.midi_queue:
            try:
                msg = self.midi_queue.popleft()
            except IndexError:
                break
            self._process_midi(msg)

        # Render all channels
        out = np.zeros(frames, dtype=np.float64)
        for ch in self.channels:
            out += ch.render(frames)

        out *= self._master_volume

        # Soft clip to avoid harsh clipping
        out = np.tanh(out)

        # Measure peak level for VU meter
        self._peak_level = float(np.max(np.abs(out)))

        outdata[:, 0] = out.astype(np.float32)

    def _process_midi(self, msg):
        """Route a parsed MIDI message to the appropriate channel."""
        msg_type = msg.get("type")
        ch_idx = msg.get("channel", 0)
        if ch_idx >= NUM_CHANNELS:
            ch_idx = 0
        channel = self.channels[ch_idx]

        if msg_type == "note_on":
            if msg["velocity"] > 0:
                channel.note_on(msg["note"], msg["velocity"])
            else:
                channel.note_off(msg["note"])
        elif msg_type == "note_off":
            channel.note_off(msg["note"])
        elif msg_type == "control_change":
            self._process_cc(channel, msg["control"], msg["value"])
        elif msg_type == "pitchwheel":
            pass  # Could add pitch bend support

    def _process_cc(self, channel: Channel, cc: int, value: int):
        """Map CC messages to synth parameters."""
        from ..midi.cc_map import CC_MAP
        normalized = value / 127.0
        if cc in CC_MAP:
            param, min_val, max_val = CC_MAP[cc]
            scaled = min_val + normalized * (max_val - min_val)
            channel.set_param(param, scaled)
        elif cc == 120 or cc == 123:  # All Sound Off / All Notes Off
            channel.all_notes_off()

    @property
    def peak_level(self) -> float:
        return self._peak_level

    @property
    def master_volume(self) -> float:
        return self._master_volume

    @master_volume.setter
    def master_volume(self, value: float):
        self._master_volume = max(0.0, min(1.0, value))
