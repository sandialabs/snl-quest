from pathlib import Path

try:
    with open(Path(__file__).parent.parent / "version.txt") as f:
        __version__ = f.read().strip()
except FileNotFoundError:
    with open(Path(__file__).parent / "version.txt") as f:
        __version__ = f.read().strip()
