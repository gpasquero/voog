"""Play a short demo sequence through the speakers to test audio output."""
import time
import numpy as np
from synth.engine.audio_engine import AudioEngine
from synth.patch.default_patches import DEFAULT_PATCHES


def play_note(engine, channel, note, velocity, duration):
    engine.midi_queue.append({
        "type": "note_on", "channel": channel, "note": note, "velocity": velocity,
    })
    time.sleep(duration)
    engine.midi_queue.append({
        "type": "note_off", "channel": channel, "note": note, "velocity": 0,
    })


def main():
    engine = AudioEngine()

    # Load Bass Moog on channel 0
    engine.channels[0].set_patch(DEFAULT_PATCHES["Bass Moog"].copy())
    # Load Lead Saw on channel 1
    engine.channels[1].set_patch(DEFAULT_PATCHES["Lead Saw"].copy())
    # Load Pad Strings on channel 2
    engine.channels[2].set_patch(DEFAULT_PATCHES["Pad Strings"].copy())

    engine.start()
    print("Audio engine running. Playing demo...")
    time.sleep(0.3)

    # --- Bass line ---
    print(">> Bass Moog (channel 1)")
    for note in [36, 36, 39, 41, 36, 36, 43, 41]:
        play_note(engine, 0, note, 100, 0.3)
        time.sleep(0.05)

    time.sleep(0.3)

    # --- Lead melody ---
    print(">> Lead Saw (channel 2)")
    melody = [(60, 0.4), (64, 0.4), (67, 0.4), (72, 0.8),
              (71, 0.2), (67, 0.2), (64, 0.4), (60, 0.8)]
    for note, dur in melody:
        play_note(engine, 1, note, 90, dur)
        time.sleep(0.05)

    time.sleep(0.3)

    # --- Pad chord ---
    print(">> Pad Strings chord (channel 3)")
    chord = [60, 64, 67, 72]
    for n in chord:
        engine.midi_queue.append({
            "type": "note_on", "channel": 2, "note": n, "velocity": 80,
        })
    time.sleep(3.0)
    for n in chord:
        engine.midi_queue.append({
            "type": "note_off", "channel": 2, "note": n, "velocity": 0,
        })
    time.sleep(2.0)  # Let the release tail ring out

    print("Demo complete.")
    engine.stop()


if __name__ == "__main__":
    main()
