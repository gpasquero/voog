from dataclasses import dataclass, field, asdict
import copy


@dataclass
class OscParams:
    waveform: str = "saw"
    octave: int = 0          # -2..+2
    semitone: int = 0        # -12..+12
    detune: float = 0.0      # cents
    level: float = 1.0
    pulse_width: float = 0.5


@dataclass
class NoiseParams:
    noise_type: str = "white"
    level: float = 0.0


@dataclass
class FilterParams:
    cutoff: float = 8000.0      # Hz
    resonance: float = 0.0      # 0..1
    env_amount: float = 0.0     # semitones
    key_tracking: float = 0.0   # 0..1


@dataclass
class ADSRParams:
    attack: float = 0.01
    decay: float = 0.1
    sustain: float = 0.7
    release: float = 0.3


@dataclass
class LFOParams:
    waveform: str = "sine"
    rate: float = 1.0
    depth: float = 0.0
    destination: str = "filter"  # filter, pitch, amp
    key_sync: bool = True


@dataclass
class GlideParams:
    time: float = 0.0
    mode: str = "off"  # off, always, legato


@dataclass
class Patch:
    name: str = "Init"
    oscillators: list[OscParams] = field(default_factory=lambda: [
        OscParams(waveform="saw", level=1.0),
        OscParams(waveform="saw", level=0.0),
        OscParams(waveform="saw", level=0.0),
    ])
    noise: NoiseParams = field(default_factory=NoiseParams)
    filter: FilterParams = field(default_factory=FilterParams)
    filter_adsr: ADSRParams = field(default_factory=lambda: ADSRParams(
        attack=0.01, decay=0.3, sustain=0.2, release=0.3,
    ))
    amp_adsr: ADSRParams = field(default_factory=lambda: ADSRParams(
        attack=0.01, decay=0.1, sustain=0.7, release=0.3,
    ))
    lfo: LFOParams = field(default_factory=LFOParams)
    glide: GlideParams = field(default_factory=GlideParams)
    master_volume: float = 0.7

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Patch":
        p = cls()
        p.name = d.get("name", "Init")
        if "oscillators" in d:
            p.oscillators = [OscParams(**o) for o in d["oscillators"]]
        if "noise" in d:
            p.noise = NoiseParams(**d["noise"])
        if "filter" in d:
            p.filter = FilterParams(**d["filter"])
        if "filter_adsr" in d:
            p.filter_adsr = ADSRParams(**d["filter_adsr"])
        if "amp_adsr" in d:
            p.amp_adsr = ADSRParams(**d["amp_adsr"])
        if "lfo" in d:
            p.lfo = LFOParams(**d["lfo"])
        if "glide" in d:
            p.glide = GlideParams(**d["glide"])
        if "master_volume" in d:
            p.master_volume = d["master_volume"]
        return p

    def copy(self) -> "Patch":
        return copy.deepcopy(self)
