from app.application.utils import extract_audio_format


def test_extract_audio_format_returns_extension():
    assert extract_audio_format("song.mp3") == "mp3"
    assert extract_audio_format("track.wav") == "wav"
    assert extract_audio_format("voice.flac") == "flac"


def test_extract_audio_format_without_extension_returns_empty_string():
    assert extract_audio_format("song") == ""


def test_extract_audio_format_handles_double_extension():
    assert extract_audio_format("archive.tar.gz") == "gz"
