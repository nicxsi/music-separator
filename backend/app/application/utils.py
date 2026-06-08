from pathlib import Path


def extract_audio_format(filename: str) -> str:
    return Path(filename).suffix.removeprefix(".")
