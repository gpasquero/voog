import argparse
import sys
from .engine.audio_engine import AudioEngine
from .patch.default_patches import DEFAULT_PATCHES

# MIDI is optional — don't crash if mido/rtmidi aren't installed
try:
    from .midi.midi_input import MidiInput
    _MIDI_AVAILABLE = True
except ImportError:
    _MIDI_AVAILABLE = False


class _NullMidi:
    """Stub when MIDI libraries are not installed."""
    is_open = False
    port_name = None
    @staticmethod
    def list_ports(): return []
    def open(self, *a, **kw): pass
    def close(self): pass


def main():
    parser = argparse.ArgumentParser(
        prog="voog",
        description="VOOG — Virtual Moog polyphonic synthesizer",
    )
    parser.add_argument("--list-midi", action="store_true", help="List MIDI input ports and exit")
    parser.add_argument("--midi-port", type=str, default=None, help="MIDI port to connect to")
    parser.add_argument("--patch", type=str, default=None, help="Default patch name to load")
    parser.add_argument("--no-midi", action="store_true", help="Start without MIDI")
    parser.add_argument("--gui", action="store_true", help="Launch graphical interface")
    args = parser.parse_args()

    if args.list_midi:
        if not _MIDI_AVAILABLE:
            print("MIDI support not available (install mido and python-rtmidi).")
            sys.exit(0)
        ports = MidiInput.list_ports()
        if ports:
            print("Available MIDI input ports:")
            for i, p in enumerate(ports):
                print(f"  [{i}] {p}")
        else:
            print("No MIDI input ports found.")
        sys.exit(0)

    # Create engine
    engine = AudioEngine()

    # Create MIDI input (real or stub)
    if _MIDI_AVAILABLE:
        midi_input = MidiInput(engine.midi_queue)
    else:
        midi_input = _NullMidi()
        if not args.no_midi:
            print("MIDI support not available (install mido and python-rtmidi). Continuing without MIDI.")

    # Load initial patch
    if args.patch and args.patch in DEFAULT_PATCHES:
        patch = DEFAULT_PATCHES[args.patch].copy()
        engine.channels[0].set_patch(patch)
        print(f"Loaded patch: {patch.name}")
    else:
        print(f"Using default patch: {engine.channels[0].patch.name}")

    # Start audio
    try:
        engine.start()
        print(f"Audio engine started (44100 Hz, buffer {engine._stream.blocksize})")
    except Exception as e:
        print(f"Failed to start audio: {e}")
        sys.exit(1)

    # Connect MIDI
    if _MIDI_AVAILABLE and not args.no_midi:
        ports = MidiInput.list_ports()
        if ports:
            port = args.midi_port if args.midi_port else ports[0]
            try:
                midi_input.open(port)
                print(f"MIDI connected: {midi_input.port_name}")
            except Exception as e:
                print(f"MIDI not available: {e}")
        else:
            print("No MIDI ports found. Use 'midi open' in REPL when available.")

    if args.gui:
        try:
            from .gui.app import SynthGUI
        except ImportError as e:
            if "_tkinter" in str(e) or "tkinter" in str(e):
                print("Error: tkinter is not installed.")
                print("  On macOS with Homebrew:  brew install python-tk@3.13")
                print("  On Ubuntu/Debian:        sudo apt install python3-tk")
                print("  On Fedora:               sudo dnf install python3-tkinter")
            else:
                print(f"Error loading GUI: {e}")
            engine.stop()
            sys.exit(1)
        gui = SynthGUI(engine, midi_input)
        try:
            gui.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            midi_input.close()
            engine.stop()
    else:
        from .cli.repl import run_repl
        print("Type 'help' for commands, 'quit' to exit.\n")
        try:
            run_repl(engine, midi_input)
        except KeyboardInterrupt:
            pass
        finally:
            print("\nShutting down...")
            midi_input.close()
            engine.stop()
            print("Done.")


if __name__ == "__main__":
    main()
