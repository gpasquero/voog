import threading
import collections
import os
import mido

# Use pygame backend if rtmidi is not available
try:
    import rtmidi  # noqa: F401
except ImportError:
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    os.environ.setdefault("MIDO_BACKEND", "mido.backends.pygame")
    mido.set_backend("mido.backends.pygame")


class MidiInput:
    """Listens on a MIDI port and pushes messages to a shared deque."""

    def __init__(self, queue: collections.deque):
        self._queue = queue
        self._port: mido.ports.BaseInput | None = None
        self._thread: threading.Thread | None = None
        self._running = False

    @staticmethod
    def list_ports() -> list[str]:
        try:
            return mido.get_input_names()
        except Exception:
            return []

    def open(self, port_name: str | None = None):
        if port_name is None:
            ports = self.list_ports()
            if not ports:
                raise RuntimeError("No MIDI input ports available")
            port_name = ports[0]
        self._port = mido.open_input(port_name)
        self._running = True
        self._thread = threading.Thread(target=self._listener, daemon=True)
        self._thread.start()

    def close(self):
        self._running = False
        if self._port is not None:
            self._port.close()
            self._port = None
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _listener(self):
        while self._running and self._port is not None:
            try:
                for msg in self._port.iter_pending():
                    parsed = self._parse(msg)
                    if parsed:
                        self._queue.append(parsed)
                import time
                time.sleep(0.001)  # ~1ms poll
            except Exception:
                if not self._running:
                    break

    @staticmethod
    def _parse(msg: mido.Message) -> dict | None:
        if msg.type == "note_on":
            return {"type": "note_on", "channel": msg.channel,
                    "note": msg.note, "velocity": msg.velocity}
        elif msg.type == "note_off":
            return {"type": "note_off", "channel": msg.channel,
                    "note": msg.note, "velocity": msg.velocity}
        elif msg.type == "control_change":
            return {"type": "control_change", "channel": msg.channel,
                    "control": msg.control, "value": msg.value}
        elif msg.type == "pitchwheel":
            return {"type": "pitchwheel", "channel": msg.channel,
                    "pitch": msg.pitch}
        return None

    @property
    def is_open(self) -> bool:
        return self._port is not None and self._running

    @property
    def port_name(self) -> str | None:
        return self._port.name if self._port else None
