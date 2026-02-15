# CC number → (param_path, min_value, max_value)
CC_MAP: dict[int, tuple[str, float, float]] = {
    1:   ("lfo.depth", 0.0, 1.0),          # Mod wheel → LFO depth
    7:   ("master_volume", 0.0, 1.0),       # Channel volume
    71:  ("filter.resonance", 0.0, 1.0),    # Resonance
    74:  ("filter.cutoff", 20.0, 20000.0),   # Cutoff (brightness)
    73:  ("amp_adsr.attack", 0.001, 2.0),    # Attack time
    75:  ("amp_adsr.decay", 0.001, 2.0),     # Decay time
    72:  ("amp_adsr.release", 0.001, 3.0),   # Release time
    76:  ("lfo.rate", 0.1, 20.0),            # LFO rate (vibrato rate)
    77:  ("filter.env_amount", 0.0, 48.0),   # Filter envelope amount
    78:  ("filter_adsr.attack", 0.001, 2.0), # Filter attack
    79:  ("filter_adsr.decay", 0.001, 2.0),  # Filter decay
}
