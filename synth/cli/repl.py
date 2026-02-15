import shlex
from ..engine.audio_engine import AudioEngine
from ..midi.midi_input import MidiInput
from ..patch.patch_manager import PatchManager


def _print_help():
    print("""
VOOG commands:
  patch list              - List available patches (defaults + saved)
  patch load <name>       - Load a default patch to channel 1
  patch save [filename]   - Save current channel 1 patch
  patch file <filename>   - Load a saved patch file

  ch <n> patch <name>     - Load patch to channel n (1-4)
  ch <n> set <param> <v>  - Set parameter on channel n
                            e.g.: ch 1 set filter.cutoff 2000
  ch <n> volume <v>       - Set channel volume (0-1)

  volume <v>              - Set master volume (0-1)
  voices                  - Show active voice count per channel
  panic                   - All notes off

  midi list               - List MIDI ports
  midi open [port]        - Open a MIDI port
  midi close              - Close MIDI port

  help                    - Show this help
  quit / exit             - Stop VOOG
""")


def run_repl(engine: AudioEngine, midi_input: MidiInput):
    pm = PatchManager()
    _print_help()

    while True:
        try:
            line = input("voog> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        try:
            parts = shlex.split(line)
        except ValueError:
            parts = line.split()

        cmd = parts[0].lower()

        try:
            if cmd in ("quit", "exit"):
                break
            elif cmd == "help":
                _print_help()
            elif cmd == "panic":
                for ch in engine.channels:
                    ch.all_notes_off()
                print("All notes off.")
            elif cmd == "voices":
                for i, ch in enumerate(engine.channels):
                    count = ch.allocator.active_voice_count()
                    print(f"  Channel {i+1}: {count} active voices [{ch.patch.name}]")
            elif cmd == "volume" and len(parts) >= 2:
                engine.master_volume = float(parts[1])
                print(f"Master volume: {engine.master_volume:.2f}")
            elif cmd == "patch":
                _handle_patch(parts[1:], engine, pm)
            elif cmd == "ch":
                _handle_channel(parts[1:], engine, pm)
            elif cmd == "midi":
                _handle_midi(parts[1:], midi_input)
            else:
                print(f"Unknown command: {cmd}. Type 'help' for commands.")
        except Exception as e:
            print(f"Error: {e}")


def _handle_patch(args: list[str], engine: AudioEngine, pm: PatchManager):
    if not args:
        print("Usage: patch list|load|save|file")
        return
    sub = args[0].lower()
    ch = engine.channels[0]

    if sub == "list":
        print("Default patches:")
        for name in pm.list_defaults():
            print(f"  {name}")
        saved = pm.list_saved()
        if saved:
            print("Saved patches:")
            for f in saved:
                print(f"  {f}")
    elif sub == "load" and len(args) >= 2:
        name = " ".join(args[1:])
        patch = pm.get_default(name)
        ch.set_patch(patch)
        print(f"Loaded '{patch.name}' on channel 1")
    elif sub == "save":
        filename = args[1] if len(args) >= 2 else None
        path = pm.save(ch.patch, filename)
        print(f"Saved to {path}")
    elif sub == "file" and len(args) >= 2:
        patch = pm.load(args[1])
        ch.set_patch(patch)
        print(f"Loaded '{patch.name}' from file")
    else:
        print("Usage: patch list|load <name>|save [file]|file <filename>")


def _handle_channel(args: list[str], engine: AudioEngine, pm: PatchManager):
    if len(args) < 2:
        print("Usage: ch <n> patch|set|volume ...")
        return
    ch_idx = int(args[0]) - 1
    if ch_idx < 0 or ch_idx >= len(engine.channels):
        print(f"Channel must be 1-{len(engine.channels)}")
        return
    ch = engine.channels[ch_idx]
    sub = args[1].lower()

    if sub == "patch" and len(args) >= 3:
        name = " ".join(args[2:])
        patch = pm.get_default(name)
        ch.set_patch(patch)
        print(f"Channel {ch_idx+1}: loaded '{patch.name}'")
    elif sub == "set" and len(args) >= 4:
        param = args[2]
        value = float(args[3])
        ch.set_param(param, value)
        print(f"Channel {ch_idx+1}: {param} = {value}")
    elif sub == "volume" and len(args) >= 3:
        ch.volume = float(args[2])
        print(f"Channel {ch_idx+1}: volume = {ch.volume:.2f}")
    else:
        print("Usage: ch <n> patch <name> | set <param> <value> | volume <v>")


def _handle_midi(args: list[str], midi_input: MidiInput):
    if not args:
        print("Usage: midi list|open|close")
        return
    sub = args[0].lower()

    if sub == "list":
        ports = MidiInput.list_ports()
        if ports:
            for i, p in enumerate(ports):
                print(f"  [{i}] {p}")
        else:
            print("  No MIDI ports found.")
    elif sub == "open":
        port = args[1] if len(args) >= 2 else None
        try:
            midi_input.open(port)
            print(f"Opened MIDI: {midi_input.port_name}")
        except Exception as e:
            print(f"Could not open MIDI: {e}")
    elif sub == "close":
        midi_input.close()
        print("MIDI closed.")
    else:
        print("Usage: midi list|open [port]|close")
