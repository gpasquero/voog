# VOOG

**Virtual Analog Synthesizer** — a Moog-style polyphonic synthesizer built in Python with a tkinter GUI inspired by the Subsequent 37.

![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue)

```
┌─────────────────────────────────────────────────────────────────┐
│  VOOG   VIRTUAL ANALOG SYNTHESIZER                              │
├─────────────────────────────────────────────────────────────────┤
│  OSC 1        OSC 2        OSC 3        NOISE                   │
│  (Oct)(Semi)  (Oct)(Semi)  (Oct)(Semi)  (Lvl)                   │
│  (Det)(Lvl)   (Det)(Lvl)   (Det)(Lvl)                           │
├─────────────────────────────────────────────────────────────────┤
│  FILTER       FILTER ENV   AMP ENV      LFO                     │
│  (Cut)(Res)   (A)(D)       (A)(D)       (Rate)(Depth)           │
│  (Env)(Key)   (S)(R)       (S)(R)                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─┬█┬─┬█┬─┬─┬█┬─┬█┬─┬█┬─┬─┬█┬─┬█┬─┬─┬█┬─┬█┬─┬█┬─┐         │
│  │ │█│ │█│ │ │█│ │█│ │█│ │ │█│ │█│ │ │█│ │█│ │█│ │ │         │
│  └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **3 oscillators** with sine, saw, square, and triangle waveforms
- **Moog ladder filter** (24dB/oct) with resonance and envelope modulation
- **Dual ADSR envelopes** for amplitude and filter
- **LFO** with 4 waveforms and 3 modulation destinations (filter, pitch, amp)
- **Glide/portamento** with off, always, and legato modes
- **Noise generator** (white/pink)
- **4 multitimbral channels**, 8-voice polyphony each
- **19 built-in presets** from deep sub basses to screaming leads
- **Rotary knob GUI** with Subsequent 37-inspired dark theme
- **Virtual keyboard** — mouse click/drag + QWERTY PC keyboard input
- **MIDI input** support (optional, graceful fallback)
- **Patch save/load** system (`~/.synth_patches/`)

## Installation

Requires **Python 3.13+** with tkinter.

```bash
# Clone
git clone https://github.com/gpasquero/voog.git
cd voog

# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install numpy sounddevice

# Optional: MIDI support
pip install mido python-rtmidi

# macOS only: install tkinter if needed
brew install python-tk@3.13
```

## Usage

### GUI mode

```bash
source .venv/bin/activate
python -m synth --gui
```

### CLI REPL mode

```bash
python -m synth
```

### Command-line options

```
--gui          Launch graphical interface
--patch NAME   Load a preset by name (e.g. "Bass Voog")
--midi-port P  Connect to a specific MIDI port
--no-midi      Start without MIDI input
--list-midi    List available MIDI ports and exit
```

## Playing notes

### QWERTY keyboard mapping

```
 W E   T Y U   O P        ← black keys (sharps)
A S D F G H J K L          ← white keys
C D E F G A B C D
```

Hold a key to sustain — key repeat is filtered so notes don't re-trigger.

### Mouse

Click and drag on the virtual keyboard. Drag across keys to glide between notes.

### MIDI

Connect any MIDI controller. MIDI CC messages are mapped to synth parameters (cutoff, resonance, envelopes, LFO, etc.).

## Rotary knobs

All synth parameters use rotary knob controls:

- **Drag vertically** on any knob to change its value (up = increase)
- **Scroll wheel** for fine adjustment
- The amber arc shows the current value position

## Presets

| Preset | Description |
|---|---|
| Init | Default starting patch |
| Bass Voog | Fat detuned saw bass with filter envelope |
| Lead Saw | Aggressive dual-saw lead with legato glide |
| Pad Strings | Warm evolving pad with slow filter LFO |
| Sub Thunder | Deep sub bass with square wave foundation |
| Acid Squelch | High-resonance filter sweep, 303-style |
| Funky Pluck | Snappy percussive hit, fast decay |
| Screaming Lead | Bright resonant lead with vibrato and glide |
| Warm Brass | Square/saw mix with medium attack |
| Dark Drone | Detuned low saws with slow LFO sweep |
| Perc Hit | Noise burst with ultra-short envelope |
| Vintage Keys | Triangle/square electric piano tone |
| Wobble Bass | LFO-driven filter modulation |
| Trance Lead | Wide-detuned triple saw with pitch vibrato |
| Fat Unison | Three saws spread ±25 cents |
| Reso Sweep | Near self-oscillating filter with long decay |
| Fifth Stab | Power fifth interval, short punch |
| Glass Bell | Sine harmonics with long crystalline release |
| Noise Sweep | Filtered noise with resonant LFO, sci-fi |

## Architecture

```
synth/
├── dsp/            # Signal processing modules
│   ├── oscillator  # Wavetable synthesis (sine, saw, square, triangle)
│   ├── filter      # Moog ladder filter (24dB/oct, Huovilainen model)
│   ├── envelope    # ADSR envelope generator
│   ├── lfo         # Low-frequency oscillator
│   ├── glide       # Pitch portamento
│   └── noise       # White/pink noise generator
├── engine/         # Audio engine
│   ├── audio_engine  # Master engine, sounddevice output, MIDI routing
│   ├── channel       # Multitimbral channel (patch + voice allocator)
│   ├── voice         # Single voice (oscillators + filter + envelopes)
│   └── voice_allocator  # Polyphonic allocation with voice stealing
├── gui/            # Graphical interface
│   └── app         # tkinter GUI with rotary knobs and virtual keyboard
├── midi/           # MIDI support
│   ├── midi_input  # MIDI port listener (mido/rtmidi)
│   ├── midi_router # Message routing
│   └── cc_map      # CC-to-parameter mapping
├── patch/          # Patch system
│   ├── patch       # Patch data structure
│   ├── patch_manager  # Save/load to disk
│   └── default_patches  # 19 built-in presets
└── cli/            # Command-line interface
    └── repl        # Interactive REPL
```

## License

MIT
