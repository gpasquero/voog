import tkinter as tk
from tkinter import ttk, messagebox
import math
from pathlib import Path

from ..engine.audio_engine import AudioEngine
from ..midi.midi_input import MidiInput
from ..patch.patch_manager import PatchManager
from ..patch.default_patches import DEFAULT_PATCHES
from ..config import MAX_VOICES

# ── Color palette — Moog Subsequent 37 inspired ────────────────────
BG_DARK = "#1a1a1a"
BG_PANEL = "#242424"
BG_HEADER = "#2c1e10"
BORDER = "#3a3a3a"
AMBER = "#e8a025"
AMBER_DIM = "#b37a1a"
CREAM = "#d4c9a8"
CREAM_DIM = "#8a8068"
TROUGH = "#2a2a2a"
WHITE_KEY = "#e8e4d8"
BLACK_KEY = "#1a1a1a"
KEY_ACTIVE = "#e8a025"
KEY_ACTIVE_BK = "#b37a1a"
CHAN_ACTIVE = "#e8a025"
CHAN_INACTIVE = "#3a3a3a"

# Knob body colors
KNOB_OUTER = "#383838"
KNOB_BODY = "#2c2c2c"
KNOB_EDGE = "#444444"

KEY_MAP = {
    "a": 0, "s": 2, "d": 4, "f": 5, "g": 7, "h": 9, "j": 11,
    "k": 12, "l": 14,
    "w": 1, "e": 3, "t": 6, "y": 8, "u": 10, "o": 13, "p": 15,
}

WAVEFORMS = ["sine", "saw", "square", "triangle"]
NOISE_TYPES = ["white", "pink"]
LFO_DESTINATIONS = ["filter", "pitch", "amp"]
GLIDE_MODES = ["off", "always", "legato"]
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# ── Rotary knob widget ─────────────────────────────────────────────

class RotaryKnob(tk.Canvas):
    """Rotary knob control — Moog Subsequent 37 style.

    Arc sweeps 300 degrees clockwise from 7 o'clock (min) to 5 o'clock (max).
    Drag vertically to change value (up = increase).
    """

    _ARC_START = 240   # tkinter arc degrees: 7 o'clock
    _ARC_SWEEP = 300   # total clockwise sweep (passed as negative extent)
    _DRAG_PX = 200     # pixels of vertical drag for full range

    def __init__(self, parent, label="", from_=0.0, to=1.0,
                 resolution=0.01, command=None, size=50, value_format=None):
        pad = 4
        label_h = 14
        value_h = 14
        cw = size + pad * 2
        ch = label_h + size + value_h + pad
        super().__init__(parent, width=cw, height=ch,
                         bg=BG_PANEL, highlightthickness=0)

        self._from = float(from_)
        self._to = float(to)
        self._range = self._to - self._from
        self._res = float(resolution)
        self._cmd = command
        self._size = size
        self._vfmt = value_format
        self._value = self._from

        self._cx = cw // 2
        self._cy = label_h + size // 2
        self._arc_r = size // 2 - 2
        self._knob_r = size // 2 - 9
        self._label = label

        self._drag_y = 0
        self._drag_v = 0.0

        self._draw()

        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<MouseWheel>", self._on_scroll)

    # Public interface (compatible with tk.DoubleVar)

    def get(self):
        return self._value

    def set(self, value):
        self._value = self._clamp(float(value))
        self._draw()

    # Internal

    def _clamp(self, v):
        v = max(self._from, min(self._to, v))
        if self._res >= 0.0001:
            v = round(v / self._res) * self._res
        return v

    def _ratio(self):
        if self._range == 0:
            return 0
        return (self._value - self._from) / self._range

    def _ratio_to_rad(self, ratio):
        deg = self._ARC_START - ratio * self._ARC_SWEEP
        return math.radians(deg)

    def _fmt(self):
        if self._vfmt:
            return self._vfmt(self._value)
        v = self._value
        if self._res >= 1:
            return str(int(v))
        if self._res >= 0.1:
            return f"{v:.1f}"
        if self._res >= 0.01:
            return f"{v:.2f}"
        return f"{v:.3f}"

    def _draw(self):
        self.delete("all")
        cx, cy = self._cx, self._cy
        ar, kr = self._arc_r, self._knob_r
        ratio = self._ratio()

        # Label
        self.create_text(cx, 8, text=self._label, fill=CREAM_DIM,
                         font=("Helvetica", 8))

        # Track arc (full range, dim)
        self.create_arc(cx - ar, cy - ar, cx + ar, cy + ar,
                        start=self._ARC_START, extent=-self._ARC_SWEEP,
                        style=tk.ARC, outline=TROUGH, width=3)

        # Value arc (filled portion, amber)
        if ratio > 0.005:
            self.create_arc(cx - ar, cy - ar, cx + ar, cy + ar,
                            start=self._ARC_START,
                            extent=-ratio * self._ARC_SWEEP,
                            style=tk.ARC, outline=AMBER, width=3)

        # Knob body — outer ring
        self.create_oval(cx - kr - 3, cy - kr - 3, cx + kr + 3, cy + kr + 3,
                         fill=KNOB_OUTER, outline=KNOB_EDGE, width=1)

        # Knob body — inner disc
        self.create_oval(cx - kr, cy - kr, cx + kr, cy + kr,
                         fill=KNOB_BODY, outline="#353535", width=1)

        # Center dot
        self.create_oval(cx - 2, cy - 2, cx + 2, cy + 2,
                         fill="#404040", outline="")

        # Indicator line
        angle = self._ratio_to_rad(ratio)
        ri = kr * 0.35
        ro = kr * 0.88
        x1 = cx + ri * math.cos(angle)
        y1 = cy - ri * math.sin(angle)
        x2 = cx + ro * math.cos(angle)
        y2 = cy - ro * math.sin(angle)
        self.create_line(x1, y1, x2, y2, fill=AMBER, width=2.5,
                         capstyle=tk.ROUND)

        # Value text
        self.create_text(cx, cy + ar + 10, text=self._fmt(), fill=CREAM,
                         font=("Helvetica", 7))

    # Interaction

    def _on_press(self, event):
        self._drag_y = event.y_root
        self._drag_v = self._value

    def _on_drag(self, event):
        dy = self._drag_y - event.y_root  # up = positive = increase
        delta = dy / self._DRAG_PX * self._range
        new = self._clamp(self._drag_v + delta)
        if new != self._value:
            self._value = new
            self._draw()
            if self._cmd:
                self._cmd(self._value)

    def _on_scroll(self, event):
        direction = 1 if event.delta > 0 else -1
        step = self._res * 5
        new = self._clamp(self._value + direction * step)
        if new != self._value:
            self._value = new
            self._draw()
            if self._cmd:
                self._cmd(self._value)


# ── VU Meter widget ───────────────────────────────────────────────

class VUMeter(tk.Canvas):
    """Vertical VU meter with green→yellow→red gradient and peak hold."""

    _DB_MIN = -60.0
    _DB_MAX = 0.0
    _PEAK_DECAY = 0.6  # dB drop per update tick

    def __init__(self, parent, width=20, height=100):
        super().__init__(parent, width=width, height=height,
                         bg=BG_PANEL, highlightthickness=0)
        self._vu_w = width
        self._vu_h = height
        self._level_db = self._DB_MIN
        self._peak_db = self._DB_MIN
        self._draw()

    def set_level(self, linear):
        """Set the current level from a linear 0..1+ value."""
        if linear < 1e-10:
            self._level_db = self._DB_MIN
        else:
            self._level_db = max(self._DB_MIN,
                                 min(self._DB_MAX, 20.0 * math.log10(linear)))
        # Peak hold: only rise instantly, decay slowly
        if self._level_db > self._peak_db:
            self._peak_db = self._level_db
        else:
            self._peak_db = max(self._DB_MIN,
                                self._peak_db - self._PEAK_DECAY)
        self._draw()

    def _db_to_y(self, db):
        """Map dB value to y coordinate (0=top, height=bottom)."""
        ratio = (db - self._DB_MIN) / (self._DB_MAX - self._DB_MIN)
        ratio = max(0.0, min(1.0, ratio))
        return int(self._vu_h * (1.0 - ratio))

    def _draw(self):
        self.delete("all")
        w, h = self._vu_w, self._vu_h
        bar_x1, bar_x2 = 3, w - 3
        level_y = self._db_to_y(self._level_db)

        # Reference marks at -6, -12, -24, -48 dB
        for db in (-6, -12, -24, -48):
            y = self._db_to_y(db)
            self.create_line(0, y, w, y, fill="#333333", width=1)

        # Draw filled bar as segments with color gradient
        seg_h = max(1, h // 30)
        y = h
        while y > level_y:
            ratio = 1.0 - (y / h)  # 0 at bottom, 1 at top
            if ratio < 0.6:
                color = "#22cc44"   # green
            elif ratio < 0.8:
                color = "#cccc22"   # yellow
            else:
                color = "#cc3322"   # red
            y_top = max(level_y, y - seg_h)
            self.create_rectangle(bar_x1, y_top, bar_x2, y - 1,
                                  fill=color, outline="")
            y -= seg_h

        # Peak hold indicator
        peak_y = self._db_to_y(self._peak_db)
        if self._peak_db > self._DB_MIN + 1:
            self.create_line(bar_x1, peak_y, bar_x2, peak_y,
                             fill=AMBER, width=2)


# ── Value formatters ───────────────────────────────────────────────

def _fmt_cutoff(v):
    hz = 20.0 * (1000.0 ** (v / 1000.0))
    hz = min(hz, 20000)
    if hz < 1000:
        return f"{int(hz)}Hz"
    return f"{hz / 1000:.1f}k"


def _fmt_time(v):
    if v < 0.1:
        return f"{v * 1000:.0f}ms"
    return f"{v:.2f}s"


def _fmt_rate(v):
    return f"{v:.1f}Hz"


# ── Main GUI ───────────────────────────────────────────────────────

class SynthGUI(tk.Tk):
    def __init__(self, engine: AudioEngine, midi_input: MidiInput):
        super().__init__()
        self.engine = engine
        self.midi_input = midi_input
        self.patch_manager = PatchManager()
        self.current_channel = 0
        self.kbd_octave = 4
        self._held_keys: dict[str, int] = {}
        self._pending_releases: dict[str, str] = {}  # key → after-id
        self._mouse_note: int | None = None

        self.title("VOOG Synthesizer")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        style = ttk.Style(self)
        style.theme_use("clam")
        self._configure_styles(style)

        self._load_logo()
        # Place logo as centered background watermark
        if self._logo_img:
            self._bg_logo = tk.Label(self, image=self._logo_img, bg=BG_DARK,
                                     borderwidth=0)
            self._bg_logo.place(relx=0.5, rely=0.5, anchor="center")
        self._build_header()
        self._build_top_bar()
        self._build_synth_panels()
        self._build_bottom_row()
        self._build_keyboard()

        self._load_controls_from_patch()

        self.bind("<KeyPress>", self._on_key_press)
        self.bind("<KeyRelease>", self._on_key_release)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configure_styles(self, style: ttk.Style):
        style.configure(".", background=BG_DARK, foreground=CREAM,
                        fieldbackground="#3a3a3a")
        style.configure("TLabel", background=BG_DARK, foreground=CREAM)
        style.configure("TLabelframe", background=BG_PANEL, foreground=AMBER,
                        bordercolor=BORDER, relief="flat")
        style.configure("TLabelframe.Label", background=BG_PANEL,
                        foreground=AMBER, font=("Helvetica", 10, "bold"))
        style.configure("TCombobox", fieldbackground="#3a3a3a",
                        foreground=CREAM, selectbackground=AMBER_DIM)
        style.configure("TCheckbutton", background=BG_PANEL, foreground=CREAM)
        style.map("TCombobox", fieldbackground=[("readonly", "#3a3a3a")])
        style.map("TCheckbutton", background=[("active", BG_PANEL)])

    # ── Header ──────────────────────────────────────────────────────

    def _load_logo(self):
        """Load the logo image for window background and icon."""
        logo_path = Path(__file__).resolve().parent.parent.parent / "voog-logo.png"
        self._logo_img = None
        if logo_path.exists():
            try:
                raw = tk.PhotoImage(file=str(logo_path))
                img_h = raw.height()
                # Icon: small version for window titlebar
                icon_factor = max(1, img_h // 48)
                self._icon_img = raw.subsample(icon_factor)
                self.iconphoto(True, self._icon_img)
                # Background: use full size or light subsample
                factor = max(1, img_h // 400)
                if factor > 1:
                    self._logo_img = raw.subsample(factor)
                else:
                    self._logo_img = raw
            except tk.TclError:
                pass

    def _build_header(self):
        header = tk.Frame(self, bg=BG_HEADER, height=48)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Frame(header, bg="#5a3a1e", height=2).place(relx=0, rely=0,
                                                        relwidth=1)
        tk.Label(header, text="VOOG", bg=BG_HEADER, fg=AMBER,
                 font=("Helvetica", 22, "bold")).pack(side=tk.LEFT,
                                                       padx=16, pady=4)
        tk.Label(header, text="VIRTUAL ANALOG SYNTHESIZER",
                 bg=BG_HEADER, fg=CREAM_DIM,
                 font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(0, 20),
                                              pady=(14, 0))
        tk.Frame(header, bg="#5a3a1e", height=2).place(relx=0, rely=1.0,
                                                        relwidth=1,
                                                        anchor="sw")

    # ── Top bar ─────────────────────────────────────────────────────

    def _build_top_bar(self):
        bar = tk.Frame(self, bg=BG_DARK, height=40, padx=8, pady=6)
        bar.pack(fill=tk.X)

        tk.Label(bar, text="PATCH", bg=BG_DARK, fg=CREAM_DIM,
                 font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.patch_var = tk.StringVar()
        names = list(DEFAULT_PATCHES.keys()) + self._saved_patch_names()
        self.patch_combo = ttk.Combobox(bar, textvariable=self.patch_var,
                                        values=names, width=16,
                                        state="readonly")
        self.patch_combo.pack(side=tk.LEFT, padx=2)
        self.patch_combo.bind("<<ComboboxSelected>>", self._on_patch_select)
        cur = self.engine.channels[self.current_channel].patch.name
        if cur in names:
            self.patch_combo.set(cur)

        tk.Button(bar, text="SAVE", width=5, bg=CHAN_INACTIVE, fg=CREAM,
                  activebackground=AMBER_DIM, activeforeground="white",
                  relief=tk.FLAT, font=("Helvetica", 9, "bold"),
                  command=self._on_save_patch).pack(side=tk.LEFT, padx=6)

        tk.Frame(bar, bg=BORDER, width=1, height=24).pack(side=tk.LEFT,
                                                           padx=10)

        tk.Label(bar, text="CH", bg=BG_DARK, fg=CREAM_DIM,
                 font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.channel_buttons: list[tk.Button] = []
        for i in range(4):
            btn = tk.Button(
                bar, text=str(i + 1), width=3, relief=tk.FLAT,
                bg=CHAN_ACTIVE if i == 0 else CHAN_INACTIVE,
                fg=BG_DARK if i == 0 else CREAM,
                activebackground=AMBER, font=("Helvetica", 10, "bold"),
                command=lambda ch=i: self._select_channel(ch))
            btn.pack(side=tk.LEFT, padx=1)
            self.channel_buttons.append(btn)


    def _saved_patch_names(self) -> list[str]:
        return [f.replace(".json", "") for f in self.patch_manager.list_saved()]

    # ── Synth panels ────────────────────────────────────────────────

    def _build_synth_panels(self):
        # Row 1: Oscillators + Noise
        row1 = tk.Frame(self, bg=BG_DARK)
        row1.pack(fill=tk.X, padx=6, pady=2)
        row1.columnconfigure((0, 1, 2, 3), weight=1)

        self.osc_panels: list[dict] = []
        for i in range(3):
            p = self._build_osc_panel(row1, i)
            p["frame"].grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            self.osc_panels.append(p)

        n = self._build_noise_panel(row1)
        n["frame"].grid(row=0, column=3, sticky="nsew", padx=2, pady=2)
        self.noise_panel = n

        # Row 2: Filter, Filter Env, Amp Env, LFO
        row2 = tk.Frame(self, bg=BG_DARK)
        row2.pack(fill=tk.X, padx=6, pady=2)
        row2.columnconfigure((0, 1, 2, 3), weight=1)

        f = self._build_filter_panel(row2)
        f["frame"].grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.filter_panel = f

        fe = self._build_adsr_panel(row2, "FILTER ENVELOPE", "filter_adsr")
        fe["frame"].grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.filter_adsr_panel = fe

        ae = self._build_adsr_panel(row2, "AMP ENVELOPE", "amp_adsr")
        ae["frame"].grid(row=0, column=2, sticky="nsew", padx=2, pady=2)
        self.amp_adsr_panel = ae

        l = self._build_lfo_panel(row2)
        l["frame"].grid(row=0, column=3, sticky="nsew", padx=2, pady=2)
        self.lfo_panel = l

    def _make_combo_row(self, parent, label, values, callback):
        """Small combo with label, packed in a frame."""
        f = tk.Frame(parent, bg=BG_PANEL)
        tk.Label(f, text=label, bg=BG_PANEL, fg=CREAM_DIM,
                 font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(2, 3))
        var = tk.StringVar()
        cb = ttk.Combobox(f, textvariable=var, values=values,
                          width=7, state="readonly")
        cb.pack(side=tk.LEFT)
        cb.bind("<<ComboboxSelected>>", lambda e: callback(var.get()))
        return f, var

    def _build_osc_panel(self, parent, idx: int) -> dict:
        frame = ttk.LabelFrame(parent, text=f"OSCILLATOR {idx + 1}",
                               padding=4)
        ctrl: dict = {"frame": frame}

        # Waveform combo
        cf, wvar = self._make_combo_row(
            frame, "Wave", WAVEFORMS,
            lambda v, i=idx: self._set_osc_param(i, "waveform", v))
        cf.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 4))
        ctrl["wave"] = wvar

        # Knobs row
        knobs = [
            ("Oct", "octave", -2, 2, 1, None),
            ("Semi", "semitone", -12, 12, 1, None),
            ("Detune", "detune", -50, 50, 0.1, None),
            ("Level", "level", 0, 1, 0.01, None),
        ]
        for col, (lbl, key, fr, to, res, vf) in enumerate(knobs):
            knob = RotaryKnob(
                frame, label=lbl, from_=fr, to=to, resolution=res,
                value_format=vf,
                command=lambda v, i=idx, k=key: self._set_osc_param(
                    i, k, int(v) if k in ("octave", "semitone") else v))
            knob.grid(row=1, column=col, padx=1)
            ctrl[key] = knob

        return ctrl

    def _build_noise_panel(self, parent) -> dict:
        frame = ttk.LabelFrame(parent, text="NOISE", padding=4)
        ctrl: dict = {"frame": frame}

        cf, tvar = self._make_combo_row(
            frame, "Type", NOISE_TYPES,
            lambda v: self._set_param("noise.noise_type", v))
        cf.grid(row=0, column=0, sticky="w", pady=(0, 4))
        ctrl["noise_type"] = tvar

        knob = RotaryKnob(
            frame, label="Level", from_=0, to=1, resolution=0.01,
            command=lambda v: self._set_param("noise.level", v))
        knob.grid(row=1, column=0, padx=1)
        ctrl["level"] = knob

        return ctrl

    def _build_filter_panel(self, parent) -> dict:
        frame = ttk.LabelFrame(parent, text="FILTER", padding=4)
        ctrl: dict = {"frame": frame}

        knobs = [
            ("Cutoff", "cutoff", 0, 1000, 1, _fmt_cutoff),
            ("Reso", "resonance", 0, 1, 0.01, None),
            ("EnvAmt", "env_amount", 0, 48, 0.5, None),
            ("KeyTrk", "key_tracking", 0, 1, 0.01, None),
        ]
        for col, (lbl, key, fr, to, res, vf) in enumerate(knobs):
            cb = (lambda v: self._on_cutoff_change(v)) if key == "cutoff" \
                else (lambda v, k=key: self._set_param(f"filter.{k}", v))
            knob = RotaryKnob(frame, label=lbl, from_=fr, to=to,
                              resolution=res, command=cb, value_format=vf)
            knob.grid(row=0, column=col, padx=1, pady=4)
            ctrl[key] = knob

        return ctrl

    def _build_adsr_panel(self, parent, title: str, prefix: str) -> dict:
        frame = ttk.LabelFrame(parent, text=title, padding=4)
        ctrl: dict = {"frame": frame}

        knobs = [
            ("A", "attack", 0.001, 2.0, 0.001, _fmt_time),
            ("D", "decay", 0.001, 2.0, 0.001, _fmt_time),
            ("S", "sustain", 0.0, 1.0, 0.01, None),
            ("R", "release", 0.001, 3.0, 0.001, _fmt_time),
        ]
        for col, (lbl, key, fr, to, res, vf) in enumerate(knobs):
            knob = RotaryKnob(
                frame, label=lbl, from_=fr, to=to, resolution=res,
                value_format=vf,
                command=lambda v, p=prefix, k=key: self._set_param(
                    f"{p}.{k}", v))
            knob.grid(row=0, column=col, padx=1, pady=4)
            ctrl[key] = knob

        return ctrl

    def _build_lfo_panel(self, parent) -> dict:
        frame = ttk.LabelFrame(parent, text="LFO", padding=4)
        ctrl: dict = {"frame": frame}

        # Two combos side by side
        combo_row = tk.Frame(frame, bg=BG_PANEL)
        combo_row.grid(row=0, column=0, columnspan=2, sticky="w",
                       pady=(0, 4))

        cf1, wvar = self._make_combo_row(
            combo_row, "Wave", WAVEFORMS,
            lambda v: self._set_param("lfo.waveform", v))
        cf1.pack(side=tk.LEFT, padx=(0, 6))
        ctrl["waveform"] = wvar

        cf2, dvar = self._make_combo_row(
            combo_row, "Dest", LFO_DESTINATIONS,
            lambda v: self._set_param("lfo.destination", v))
        cf2.pack(side=tk.LEFT)
        ctrl["destination"] = dvar

        # Knobs
        rate = RotaryKnob(frame, label="Rate", from_=0.1, to=20, resolution=0.1,
                          value_format=_fmt_rate,
                          command=lambda v: self._set_param("lfo.rate", v))
        rate.grid(row=1, column=0, padx=1)
        ctrl["rate"] = rate

        depth = RotaryKnob(frame, label="Depth", from_=0, to=1, resolution=0.01,
                           command=lambda v: self._set_param("lfo.depth", v))
        depth.grid(row=1, column=1, padx=1)
        ctrl["depth"] = depth

        # Key sync
        sync_var = tk.BooleanVar()
        chk = ttk.Checkbutton(
            frame, text="Key Sync", variable=sync_var,
            command=lambda: self._set_param("lfo.key_sync", sync_var.get()))
        chk.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ctrl["key_sync"] = sync_var

        return ctrl

    # ── Bottom row ──────────────────────────────────────────────────

    def _build_bottom_row(self):
        row = tk.Frame(self, bg=BG_DARK)
        row.pack(fill=tk.X, padx=6, pady=2)
        row.columnconfigure((0, 1), weight=1)

        # Glide
        gf = ttk.LabelFrame(row, text="GLIDE", padding=4)
        gf.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.glide_panel: dict = {"frame": gf}

        cf, mvar = self._make_combo_row(
            gf, "Mode", GLIDE_MODES,
            lambda v: self._set_param("glide.mode", v))
        cf.grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.glide_panel["mode"] = mvar

        time_knob = RotaryKnob(
            gf, label="Time", from_=0, to=1, resolution=0.01,
            value_format=_fmt_time,
            command=lambda v: self._set_param("glide.time", v))
        time_knob.grid(row=1, column=0, padx=1)
        self.glide_panel["time"] = time_knob

        # Status
        sf = ttk.LabelFrame(row, text="STATUS", padding=6)
        sf.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)

        status_inner = tk.Frame(sf, bg=BG_PANEL)
        status_inner.pack(fill=tk.BOTH, expand=True)

        self.voices_label = tk.Label(status_inner, text="Voices: 0/8",
                                     bg=BG_PANEL, fg=AMBER,
                                     font=("Helvetica", 13, "bold"))
        self.voices_label.pack(side=tk.LEFT, padx=10, pady=10)

        # VU meter
        self.vu_meter = VUMeter(status_inner, width=20, height=80)
        self.vu_meter.pack(side=tk.LEFT, padx=(10, 6), pady=4)

        # Master volume knob
        self.master_knob = RotaryKnob(
            status_inner, label="MASTER", from_=0, to=100, resolution=1,
            command=self._on_master_volume)
        self.master_knob.set(int(self.engine.master_volume * 100))
        self.master_knob.pack(side=tk.LEFT, padx=6, pady=4)

        self._update_voices_display()
        self._update_vu_meter()

    # ── Virtual keyboard ────────────────────────────────────────────

    def _build_keyboard(self):
        kf = ttk.LabelFrame(self, text="KEYBOARD", padding=6)
        kf.pack(fill=tk.X, padx=8, pady=(2, 8))

        self.kbd_canvas = tk.Canvas(kf, height=120, bg=BG_DARK,
                                    highlightthickness=0)
        self.kbd_canvas.pack(fill=tk.X, padx=2, pady=2)

        cf = tk.Frame(kf, bg=BG_PANEL)
        cf.pack(fill=tk.X)
        tk.Button(cf, text="OCT -", width=6, bg=CHAN_INACTIVE, fg=CREAM,
                  activebackground=AMBER_DIM, activeforeground="white",
                  relief=tk.FLAT, font=("Helvetica", 9, "bold"),
                  command=self._oct_down).pack(side=tk.LEFT, padx=4, pady=3)
        self.oct_label = tk.Label(cf, text=f"Octave: {self.kbd_octave}",
                                  bg=BG_PANEL, fg=AMBER,
                                  font=("Helvetica", 11, "bold"))
        self.oct_label.pack(side=tk.LEFT, padx=8)
        tk.Button(cf, text="OCT +", width=6, bg=CHAN_INACTIVE, fg=CREAM,
                  activebackground=AMBER_DIM, activeforeground="white",
                  relief=tk.FLAT, font=("Helvetica", 9, "bold"),
                  command=self._oct_up).pack(side=tk.LEFT, padx=4, pady=3)

        self.kbd_canvas.bind("<Configure>", lambda e: self._draw_keys())
        self.kbd_canvas.bind("<ButtonPress-1>", self._on_kbd_mouse_down)
        self.kbd_canvas.bind("<B1-Motion>", self._on_kbd_mouse_drag)
        self.kbd_canvas.bind("<ButtonRelease-1>", self._on_kbd_mouse_up)
        self._key_rects: list[tuple] = []

    def _draw_keys(self):
        c = self.kbd_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10:
            return

        num_oct = 3
        total_w = num_oct * 7 + 1
        wk = w / total_w
        bk_w = wk * 0.6
        bk_h = h * 0.62
        self._key_rects = []

        whites = [0, 2, 4, 5, 7, 9, 11]
        blacks = {0: 1, 1: 3, 3: 6, 4: 8, 5: 10}
        base = self.kbd_octave * 12 + 12

        # White keys
        wi = 0
        for octave in range(num_oct):
            for wn, semi in enumerate(whites):
                note = base + octave * 12 + semi
                x1, x2 = wi * wk, (wi + 1) * wk
                self._key_rects.append((x1, 0, x2, h, note, False))
                c.create_rectangle(x1, 0, x2, h, fill=WHITE_KEY,
                                   outline="#a09880", width=1,
                                   tags=f"key_{note}")
                name = NOTE_NAMES[semi]
                if semi == 0:
                    name += str(self.kbd_octave + octave)
                c.create_text((x1 + x2) / 2, h - 12, text=name,
                              fill="#8a8068", font=("Helvetica", 8),
                              tags=f"key_{note}")
                wi += 1

        note = base + num_oct * 12
        x1, x2 = wi * wk, (wi + 1) * wk
        self._key_rects.append((x1, 0, x2, h, note, False))
        c.create_rectangle(x1, 0, x2, h, fill=WHITE_KEY,
                           outline="#a09880", width=1, tags=f"key_{note}")
        c.create_text((x1 + x2) / 2, h - 12,
                      text=f"C{self.kbd_octave + num_oct}",
                      fill="#8a8068", font=("Helvetica", 8),
                      tags=f"key_{note}")

        # Black keys
        wi = 0
        for octave in range(num_oct):
            for wn in range(7):
                if wn in blacks:
                    semi = blacks[wn]
                    note = base + octave * 12 + semi
                    cx = (wi + 1) * wk
                    x1, x2 = cx - bk_w / 2, cx + bk_w / 2
                    self._key_rects.append((x1, 0, x2, bk_h, note, True))
                    c.create_rectangle(x1, 0, x2, bk_h, fill=BLACK_KEY,
                                       outline="#000", width=1,
                                       tags=f"key_{note}")
                wi += 1

    def _note_at_pos(self, x, y):
        for x1, y1, x2, y2, note, blk in self._key_rects:
            if blk and x1 <= x <= x2 and y1 <= y <= y2:
                return note
        for x1, y1, x2, y2, note, blk in self._key_rects:
            if not blk and x1 <= x <= x2 and y1 <= y <= y2:
                return note
        return None

    def _highlight_key(self, note, pressed):
        blk = note % 12 in (1, 3, 6, 8, 10)
        color = (KEY_ACTIVE_BK if blk else KEY_ACTIVE) if pressed \
            else (BLACK_KEY if blk else WHITE_KEY)
        self.kbd_canvas.itemconfigure(f"key_{note}", fill=color)

    def _on_kbd_mouse_down(self, e):
        note = self._note_at_pos(e.x, e.y)
        if note is not None:
            self._mouse_note = note
            self._play_note(note)
            self._highlight_key(note, True)

    def _on_kbd_mouse_drag(self, e):
        note = self._note_at_pos(e.x, e.y)
        if note != self._mouse_note:
            if self._mouse_note is not None:
                self._stop_note(self._mouse_note)
                self._highlight_key(self._mouse_note, False)
            if note is not None:
                self._mouse_note = note
                self._play_note(note)
                self._highlight_key(note, True)
            else:
                self._mouse_note = None

    def _on_kbd_mouse_up(self, e):
        if self._mouse_note is not None:
            self._stop_note(self._mouse_note)
            self._highlight_key(self._mouse_note, False)
            self._mouse_note = None

    def _oct_down(self):
        if self.kbd_octave > 0:
            self.kbd_octave -= 1
            self.oct_label.config(text=f"Octave: {self.kbd_octave}")
            self._draw_keys()

    def _oct_up(self):
        if self.kbd_octave < 7:
            self.kbd_octave += 1
            self.oct_label.config(text=f"Octave: {self.kbd_octave}")
            self._draw_keys()

    # ── PC keyboard ─────────────────────────────────────────────────

    def _on_key_press(self, event):
        key = event.char.lower()
        if key not in KEY_MAP:
            return
        # Cancel pending release from OS key-repeat (Release→Press pair)
        if key in self._pending_releases:
            self.after_cancel(self._pending_releases.pop(key))
            return  # key was already held, just keep it going
        if key not in self._held_keys:
            note = (self.kbd_octave + 1) * 12 + KEY_MAP[key]
            self._held_keys[key] = note
            self._play_note(note)
            self._highlight_key(note, True)

    def _on_key_release(self, event):
        key = event.char.lower()
        if key in self._held_keys and key not in self._pending_releases:
            # Delay release briefly — if a KeyPress follows immediately
            # (OS repeat), _on_key_press will cancel this timer.
            self._pending_releases[key] = self.after(
                30, lambda k=key: self._do_key_release(k))

    def _do_key_release(self, key):
        self._pending_releases.pop(key, None)
        if key in self._held_keys:
            note = self._held_keys.pop(key)
            self._stop_note(note)
            self._highlight_key(note, False)

    # ── Engine interaction ──────────────────────────────────────────

    def _play_note(self, note, velocity=100):
        self.engine.channels[self.current_channel].note_on(note, velocity)
        self._update_voices_display()

    def _stop_note(self, note):
        self.engine.channels[self.current_channel].note_off(note)
        self.after(50, self._update_voices_display)

    def _set_param(self, param, value):
        self.engine.channels[self.current_channel].set_param(param, value)

    def _set_osc_param(self, idx, key, value):
        self._set_param(f"osc{idx + 1}.{key}", value)

    def _on_master_volume(self, value):
        self.engine.master_volume = float(value) / 100.0

    def _update_vu_meter(self):
        self.vu_meter.set_level(self.engine.peak_level)
        self.after(50, self._update_vu_meter)

    def _on_cutoff_change(self, value):
        freq = 20.0 * (1000.0 ** (value / 1000.0))
        freq = min(freq, 20000.0)
        self._set_param("filter.cutoff", freq)

    def _cutoff_to_slider(self, freq):
        if freq <= 20:
            return 0.0
        return 1000.0 * math.log(freq / 20.0) / math.log(1000.0)

    # ── Patch management ────────────────────────────────────────────

    def _on_patch_select(self, event=None):
        name = self.patch_var.get()
        if not name:
            return
        if name in DEFAULT_PATCHES:
            patch = DEFAULT_PATCHES[name].copy()
        else:
            try:
                patch = self.patch_manager.load(name + ".json")
            except FileNotFoundError:
                messagebox.showerror("Error", f"Patch not found: {name}")
                return
        self.engine.channels[self.current_channel].set_patch(patch)
        self._load_controls_from_patch()

    def _on_save_patch(self):
        try:
            self.patch_manager.save(
                self.engine.channels[self.current_channel].patch)
            names = list(DEFAULT_PATCHES.keys()) + self._saved_patch_names()
            self.patch_combo["values"] = names
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def _select_channel(self, ch_idx):
        for key, note in list(self._held_keys.items()):
            self._stop_note(note)
            self._highlight_key(note, False)
        self._held_keys.clear()
        self.current_channel = ch_idx
        for i, btn in enumerate(self.channel_buttons):
            btn.config(bg=CHAN_ACTIVE if i == ch_idx else CHAN_INACTIVE,
                       fg=BG_DARK if i == ch_idx else CREAM)
        self._load_controls_from_patch()
        self._update_voices_display()

    def _load_controls_from_patch(self):
        patch = self.engine.channels[self.current_channel].patch
        self.patch_var.set(patch.name)

        for i, osc in enumerate(patch.oscillators):
            p = self.osc_panels[i]
            p["wave"].set(osc.waveform)
            p["octave"].set(osc.octave)
            p["semitone"].set(osc.semitone)
            p["detune"].set(osc.detune)
            p["level"].set(osc.level)

        self.noise_panel["noise_type"].set(patch.noise.noise_type)
        self.noise_panel["level"].set(patch.noise.level)

        self.filter_panel["cutoff"].set(
            self._cutoff_to_slider(patch.filter.cutoff))
        self.filter_panel["resonance"].set(patch.filter.resonance)
        self.filter_panel["env_amount"].set(patch.filter.env_amount)
        self.filter_panel["key_tracking"].set(patch.filter.key_tracking)

        for key in ("attack", "decay", "sustain", "release"):
            self.filter_adsr_panel[key].set(
                getattr(patch.filter_adsr, key))
            self.amp_adsr_panel[key].set(
                getattr(patch.amp_adsr, key))

        self.lfo_panel["waveform"].set(patch.lfo.waveform)
        self.lfo_panel["rate"].set(patch.lfo.rate)
        self.lfo_panel["depth"].set(patch.lfo.depth)
        self.lfo_panel["destination"].set(patch.lfo.destination)
        self.lfo_panel["key_sync"].set(patch.lfo.key_sync)

        self.glide_panel["time"].set(patch.glide.time)
        self.glide_panel["mode"].set(patch.glide.mode)

    def _update_voices_display(self):
        ch = self.engine.channels[self.current_channel]
        active = ch.allocator.active_voice_count()
        self.voices_label.config(text=f"Voices: {active}/{MAX_VOICES}")
        if hasattr(self, '_voice_update_id'):
            self.after_cancel(self._voice_update_id)
        self._voice_update_id = self.after(200, self._update_voices_display)

    def _on_close(self):
        for ch in self.engine.channels:
            ch.all_notes_off()
        self.destroy()
