from .patch import Patch, OscParams, NoiseParams, FilterParams, ADSRParams, LFOParams, GlideParams


def init_patch() -> Patch:
    return Patch(name="Init")


def bass_voog() -> Patch:
    """Fat detuned saw bass with filter envelope punch."""
    return Patch(
        name="Bass Voog",
        oscillators=[
            OscParams(waveform="saw", octave=-1, level=1.0),
            OscParams(waveform="saw", octave=-1, detune=8.0, level=0.7),
            OscParams(waveform="square", octave=-2, level=0.5),
        ],
        noise=NoiseParams(level=0.0),
        filter=FilterParams(cutoff=400.0, resonance=0.4, env_amount=24.0, key_tracking=0.5),
        filter_adsr=ADSRParams(attack=0.005, decay=0.4, sustain=0.1, release=0.2),
        amp_adsr=ADSRParams(attack=0.005, decay=0.3, sustain=0.6, release=0.15),
        lfo=LFOParams(depth=0.0),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.8,
    )


def lead_saw() -> Patch:
    """Aggressive dual-saw lead with legato glide."""
    return Patch(
        name="Lead Saw",
        oscillators=[
            OscParams(waveform="saw", octave=0, level=1.0),
            OscParams(waveform="saw", octave=0, detune=12.0, level=0.8),
            OscParams(waveform="saw", octave=1, level=0.3),
        ],
        noise=NoiseParams(level=0.0),
        filter=FilterParams(cutoff=3000.0, resonance=0.3, env_amount=12.0, key_tracking=0.7),
        filter_adsr=ADSRParams(attack=0.01, decay=0.3, sustain=0.3, release=0.3),
        amp_adsr=ADSRParams(attack=0.01, decay=0.1, sustain=0.8, release=0.3),
        lfo=LFOParams(waveform="sine", rate=5.0, depth=0.0, destination="pitch"),
        glide=GlideParams(time=0.05, mode="legato"),
        master_volume=0.7,
    )


def pad_strings() -> Patch:
    """Warm evolving pad with slow filter LFO."""
    return Patch(
        name="Pad Strings",
        oscillators=[
            OscParams(waveform="saw", octave=0, level=0.7),
            OscParams(waveform="saw", octave=0, detune=7.0, level=0.7),
            OscParams(waveform="saw", octave=1, detune=-5.0, level=0.4),
        ],
        noise=NoiseParams(noise_type="pink", level=0.05),
        filter=FilterParams(cutoff=2000.0, resonance=0.1, env_amount=6.0, key_tracking=0.3),
        filter_adsr=ADSRParams(attack=0.8, decay=0.5, sustain=0.6, release=1.5),
        amp_adsr=ADSRParams(attack=0.6, decay=0.3, sustain=0.8, release=1.5),
        lfo=LFOParams(waveform="triangle", rate=0.3, depth=0.15, destination="filter"),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.6,
    )


# ── Subsequent 37 style presets ─────────────────────────────────────


def sub_thunder() -> Patch:
    """Deep sub bass — pure low-end weight with square sub layer."""
    return Patch(
        name="Sub Thunder",
        oscillators=[
            OscParams(waveform="square", octave=-2, level=1.0),
            OscParams(waveform="sine", octave=-1, level=0.4),
            OscParams(waveform="saw", octave=-1, level=0.0),
        ],
        noise=NoiseParams(level=0.0),
        filter=FilterParams(cutoff=180.0, resonance=0.15, env_amount=12.0, key_tracking=0.8),
        filter_adsr=ADSRParams(attack=0.003, decay=0.25, sustain=0.0, release=0.12),
        amp_adsr=ADSRParams(attack=0.003, decay=0.15, sustain=0.9, release=0.1),
        lfo=LFOParams(depth=0.0),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.85,
    )


def acid_squelch() -> Patch:
    """Resonant acid bass — high-Q filter with fast envelope sweep."""
    return Patch(
        name="Acid Squelch",
        oscillators=[
            OscParams(waveform="saw", octave=-1, level=1.0),
            OscParams(waveform="square", octave=-1, semitone=0, level=0.5),
            OscParams(waveform="saw", octave=0, level=0.0),
        ],
        noise=NoiseParams(level=0.0),
        filter=FilterParams(cutoff=200.0, resonance=0.75, env_amount=36.0, key_tracking=0.5),
        filter_adsr=ADSRParams(attack=0.002, decay=0.18, sustain=0.0, release=0.1),
        amp_adsr=ADSRParams(attack=0.002, decay=0.5, sustain=0.4, release=0.12),
        lfo=LFOParams(depth=0.0),
        glide=GlideParams(time=0.04, mode="always"),
        master_volume=0.75,
    )


def funky_pluck() -> Patch:
    """Snappy percussive pluck — short decay, punchy attack."""
    return Patch(
        name="Funky Pluck",
        oscillators=[
            OscParams(waveform="saw", octave=0, level=1.0),
            OscParams(waveform="square", octave=0, detune=5.0, level=0.6),
            OscParams(waveform="saw", octave=-1, level=0.3),
        ],
        noise=NoiseParams(level=0.0),
        filter=FilterParams(cutoff=350.0, resonance=0.35, env_amount=30.0, key_tracking=0.6),
        filter_adsr=ADSRParams(attack=0.001, decay=0.12, sustain=0.0, release=0.08),
        amp_adsr=ADSRParams(attack=0.001, decay=0.25, sustain=0.0, release=0.08),
        lfo=LFOParams(depth=0.0),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.75,
    )


def screaming_lead() -> Patch:
    """Bright aggressive lead — full resonance, always-on glide."""
    return Patch(
        name="Screaming Lead",
        oscillators=[
            OscParams(waveform="saw", octave=0, level=1.0),
            OscParams(waveform="saw", octave=0, detune=15.0, level=0.9),
            OscParams(waveform="square", octave=1, level=0.4),
        ],
        noise=NoiseParams(level=0.02),
        filter=FilterParams(cutoff=1200.0, resonance=0.55, env_amount=18.0, key_tracking=0.9),
        filter_adsr=ADSRParams(attack=0.01, decay=0.4, sustain=0.5, release=0.35),
        amp_adsr=ADSRParams(attack=0.008, decay=0.15, sustain=0.85, release=0.25),
        lfo=LFOParams(waveform="sine", rate=5.5, depth=0.08, destination="pitch", key_sync=True),
        glide=GlideParams(time=0.06, mode="always"),
        master_volume=0.7,
    )


def warm_brass() -> Patch:
    """Mellow brass tone — square/saw mix with medium attack."""
    return Patch(
        name="Warm Brass",
        oscillators=[
            OscParams(waveform="square", octave=0, level=0.9),
            OscParams(waveform="saw", octave=0, detune=3.0, level=0.6),
            OscParams(waveform="saw", octave=-1, level=0.25),
        ],
        noise=NoiseParams(level=0.0),
        filter=FilterParams(cutoff=800.0, resonance=0.15, env_amount=16.0, key_tracking=0.7),
        filter_adsr=ADSRParams(attack=0.06, decay=0.35, sustain=0.45, release=0.25),
        amp_adsr=ADSRParams(attack=0.04, decay=0.2, sustain=0.75, release=0.2),
        lfo=LFOParams(depth=0.0),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.7,
    )


def dark_drone() -> Patch:
    """Low detuned drone with slow filter LFO sweep."""
    return Patch(
        name="Dark Drone",
        oscillators=[
            OscParams(waveform="saw", octave=-1, level=0.8),
            OscParams(waveform="saw", octave=-1, detune=-10.0, level=0.8),
            OscParams(waveform="square", octave=-2, detune=5.0, level=0.5),
        ],
        noise=NoiseParams(noise_type="pink", level=0.08),
        filter=FilterParams(cutoff=500.0, resonance=0.45, env_amount=4.0, key_tracking=0.2),
        filter_adsr=ADSRParams(attack=1.0, decay=0.5, sustain=0.7, release=2.0),
        amp_adsr=ADSRParams(attack=0.8, decay=0.4, sustain=0.85, release=2.0),
        lfo=LFOParams(waveform="triangle", rate=0.15, depth=0.25, destination="filter", key_sync=False),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.6,
    )


def perc_hit() -> Patch:
    """Percussive transient hit — noise burst with pitched body."""
    return Patch(
        name="Perc Hit",
        oscillators=[
            OscParams(waveform="triangle", octave=0, level=0.7),
            OscParams(waveform="sine", octave=1, level=0.4),
            OscParams(waveform="saw", octave=0, level=0.0),
        ],
        noise=NoiseParams(noise_type="white", level=0.3),
        filter=FilterParams(cutoff=600.0, resonance=0.2, env_amount=40.0, key_tracking=0.4),
        filter_adsr=ADSRParams(attack=0.001, decay=0.06, sustain=0.0, release=0.04),
        amp_adsr=ADSRParams(attack=0.001, decay=0.15, sustain=0.0, release=0.06),
        lfo=LFOParams(depth=0.0),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.75,
    )


def vintage_keys() -> Patch:
    """Vintage electric piano tone — triangle/square mix, bell-like decay."""
    return Patch(
        name="Vintage Keys",
        oscillators=[
            OscParams(waveform="triangle", octave=0, level=1.0),
            OscParams(waveform="square", octave=1, level=0.2),
            OscParams(waveform="sine", octave=0, detune=1.5, level=0.3),
        ],
        noise=NoiseParams(level=0.0),
        filter=FilterParams(cutoff=2500.0, resonance=0.1, env_amount=10.0, key_tracking=0.8),
        filter_adsr=ADSRParams(attack=0.001, decay=0.6, sustain=0.15, release=0.4),
        amp_adsr=ADSRParams(attack=0.001, decay=0.8, sustain=0.2, release=0.5),
        lfo=LFOParams(waveform="sine", rate=4.0, depth=0.03, destination="pitch", key_sync=True),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.7,
    )


def wobble_bass() -> Patch:
    """Wobble bass — LFO-driven filter modulation, heavy low end."""
    return Patch(
        name="Wobble Bass",
        oscillators=[
            OscParams(waveform="saw", octave=-1, level=1.0),
            OscParams(waveform="square", octave=-1, detune=4.0, level=0.7),
            OscParams(waveform="square", octave=-2, level=0.6),
        ],
        noise=NoiseParams(level=0.0),
        filter=FilterParams(cutoff=300.0, resonance=0.5, env_amount=6.0, key_tracking=0.4),
        filter_adsr=ADSRParams(attack=0.005, decay=0.2, sustain=0.3, release=0.15),
        amp_adsr=ADSRParams(attack=0.005, decay=0.1, sustain=0.9, release=0.12),
        lfo=LFOParams(waveform="sine", rate=3.0, depth=0.6, destination="filter", key_sync=True),
        glide=GlideParams(time=0.03, mode="legato"),
        master_volume=0.75,
    )


def trance_lead() -> Patch:
    """Bright supersaw lead with pitch vibrato."""
    return Patch(
        name="Trance Lead",
        oscillators=[
            OscParams(waveform="saw", octave=0, level=1.0),
            OscParams(waveform="saw", octave=0, detune=20.0, level=0.8),
            OscParams(waveform="saw", octave=0, detune=-18.0, level=0.8),
        ],
        noise=NoiseParams(level=0.0),
        filter=FilterParams(cutoff=5000.0, resonance=0.2, env_amount=8.0, key_tracking=0.6),
        filter_adsr=ADSRParams(attack=0.01, decay=0.4, sustain=0.4, release=0.35),
        amp_adsr=ADSRParams(attack=0.01, decay=0.1, sustain=0.85, release=0.3),
        lfo=LFOParams(waveform="sine", rate=5.8, depth=0.06, destination="pitch", key_sync=True),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.65,
    )


def fat_unison() -> Patch:
    """Massive detuned unison — three saws wide-spread, full spectrum."""
    return Patch(
        name="Fat Unison",
        oscillators=[
            OscParams(waveform="saw", octave=0, detune=-25.0, level=0.9),
            OscParams(waveform="saw", octave=0, detune=0.0, level=1.0),
            OscParams(waveform="saw", octave=0, detune=25.0, level=0.9),
        ],
        noise=NoiseParams(level=0.0),
        filter=FilterParams(cutoff=4000.0, resonance=0.15, env_amount=10.0, key_tracking=0.5),
        filter_adsr=ADSRParams(attack=0.01, decay=0.5, sustain=0.3, release=0.4),
        amp_adsr=ADSRParams(attack=0.01, decay=0.15, sustain=0.8, release=0.35),
        lfo=LFOParams(depth=0.0),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.6,
    )


def reso_sweep() -> Patch:
    """Resonant sweep — self-oscillating filter with slow envelope."""
    return Patch(
        name="Reso Sweep",
        oscillators=[
            OscParams(waveform="saw", octave=0, level=0.7),
            OscParams(waveform="saw", octave=-1, detune=6.0, level=0.5),
            OscParams(waveform="saw", octave=0, level=0.0),
        ],
        noise=NoiseParams(noise_type="pink", level=0.04),
        filter=FilterParams(cutoff=120.0, resonance=0.85, env_amount=44.0, key_tracking=0.6),
        filter_adsr=ADSRParams(attack=0.005, decay=1.5, sustain=0.0, release=0.8),
        amp_adsr=ADSRParams(attack=0.005, decay=1.8, sustain=0.0, release=0.8),
        lfo=LFOParams(depth=0.0),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.65,
    )


def fifth_stab() -> Patch:
    """Power fifth stab — osc2 tuned to a fifth, short punchy hit."""
    return Patch(
        name="Fifth Stab",
        oscillators=[
            OscParams(waveform="saw", octave=0, level=1.0),
            OscParams(waveform="saw", octave=0, semitone=7, level=0.7),
            OscParams(waveform="square", octave=-1, level=0.4),
        ],
        noise=NoiseParams(level=0.0),
        filter=FilterParams(cutoff=500.0, resonance=0.25, env_amount=28.0, key_tracking=0.5),
        filter_adsr=ADSRParams(attack=0.001, decay=0.15, sustain=0.05, release=0.1),
        amp_adsr=ADSRParams(attack=0.001, decay=0.3, sustain=0.0, release=0.1),
        lfo=LFOParams(depth=0.0),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.7,
    )


def glass_bell() -> Patch:
    """Crystalline bell tone — sine harmonics with long release."""
    return Patch(
        name="Glass Bell",
        oscillators=[
            OscParams(waveform="sine", octave=0, level=1.0),
            OscParams(waveform="triangle", octave=1, level=0.35),
            OscParams(waveform="sine", octave=2, detune=2.0, level=0.15),
        ],
        noise=NoiseParams(level=0.0),
        filter=FilterParams(cutoff=6000.0, resonance=0.3, env_amount=12.0, key_tracking=0.9),
        filter_adsr=ADSRParams(attack=0.001, decay=1.2, sustain=0.1, release=1.5),
        amp_adsr=ADSRParams(attack=0.001, decay=1.5, sustain=0.05, release=2.0),
        lfo=LFOParams(waveform="sine", rate=3.5, depth=0.02, destination="pitch", key_sync=True),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.7,
    )


def noise_sweep() -> Patch:
    """Noise texture — filtered noise with resonant sweep, sci-fi flavor."""
    return Patch(
        name="Noise Sweep",
        oscillators=[
            OscParams(waveform="saw", octave=0, level=0.2),
            OscParams(waveform="saw", octave=0, level=0.0),
            OscParams(waveform="saw", octave=0, level=0.0),
        ],
        noise=NoiseParams(noise_type="white", level=0.8),
        filter=FilterParams(cutoff=150.0, resonance=0.7, env_amount=40.0, key_tracking=0.0),
        filter_adsr=ADSRParams(attack=0.3, decay=1.0, sustain=0.2, release=0.8),
        amp_adsr=ADSRParams(attack=0.2, decay=0.8, sustain=0.4, release=1.0),
        lfo=LFOParams(waveform="triangle", rate=0.2, depth=0.3, destination="filter", key_sync=False),
        glide=GlideParams(time=0.0, mode="off"),
        master_volume=0.6,
    )


DEFAULT_PATCHES: dict[str, Patch] = {
    "Init": init_patch(),
    # ── Classic ──
    "Bass Voog": bass_voog(),
    "Lead Saw": lead_saw(),
    "Pad Strings": pad_strings(),
    # ── Subsequent 37 ──
    "Sub Thunder": sub_thunder(),
    "Acid Squelch": acid_squelch(),
    "Funky Pluck": funky_pluck(),
    "Screaming Lead": screaming_lead(),
    "Warm Brass": warm_brass(),
    "Dark Drone": dark_drone(),
    "Perc Hit": perc_hit(),
    "Vintage Keys": vintage_keys(),
    "Wobble Bass": wobble_bass(),
    "Trance Lead": trance_lead(),
    "Fat Unison": fat_unison(),
    "Reso Sweep": reso_sweep(),
    "Fifth Stab": fifth_stab(),
    "Glass Bell": glass_bell(),
    "Noise Sweep": noise_sweep(),
}
