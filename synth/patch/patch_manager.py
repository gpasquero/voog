import json
import os
from .patch import Patch
from .default_patches import DEFAULT_PATCHES

_PATCH_DIR = os.path.expanduser("~/.synth_patches")


class PatchManager:
    def __init__(self, patch_dir: str = _PATCH_DIR):
        self.patch_dir = patch_dir
        os.makedirs(self.patch_dir, exist_ok=True)

    def save(self, patch: Patch, filename: str | None = None):
        if filename is None:
            filename = patch.name.replace(" ", "_").lower() + ".json"
        path = os.path.join(self.patch_dir, filename)
        with open(path, "w") as f:
            json.dump(patch.to_dict(), f, indent=2)
        return path

    def load(self, filename: str) -> Patch:
        path = os.path.join(self.patch_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Patch not found: {path}")
        with open(path) as f:
            data = json.load(f)
        return Patch.from_dict(data)

    def list_saved(self) -> list[str]:
        if not os.path.isdir(self.patch_dir):
            return []
        return [f for f in os.listdir(self.patch_dir) if f.endswith(".json")]

    def list_defaults(self) -> list[str]:
        return list(DEFAULT_PATCHES.keys())

    def get_default(self, name: str) -> Patch:
        if name not in DEFAULT_PATCHES:
            raise KeyError(f"Unknown default patch: {name}")
        return DEFAULT_PATCHES[name].copy()
