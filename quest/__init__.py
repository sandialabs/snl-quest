from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _read_local_version() -> str:
    return Path(__file__).resolve().parent.parent.joinpath("version.txt").read_text(
        encoding="utf-8"
    ).strip()


try:
    __version__ = version("Quest")
except PackageNotFoundError:
    __version__ = _read_local_version()
