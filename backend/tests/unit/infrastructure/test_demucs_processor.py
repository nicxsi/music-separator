from pathlib import Path
from types import SimpleNamespace

import pytest
from app.infrastructure.services.demucs_processor import DemucsProcessor


def test_prepare_command_builds_expected_command(tmp_path):
    processor = DemucsProcessor(
        output_dir=tmp_path / "outputs",
        log_path=tmp_path / "logs" / "demucs.log",
    )

    cmd = processor._prepare_command(
        input_path=Path("/tmp/input/song.mp3"),
        output_path=Path("/tmp/outputs"),
        audio_format="mp3",
    )

    assert cmd == [
        "demucs",
        "-o",
        str(Path("/tmp/outputs")),
        str(Path("/tmp/input/song.mp3")),
        "--mp3",
    ]


def test_prepare_command_ignores_unknown_format(tmp_path):
    processor = DemucsProcessor(
        output_dir=tmp_path / "outputs",
        log_path=tmp_path / "logs" / "demucs.log",
    )

    cmd = processor._prepare_command(
        input_path=Path("/tmp/input/song.ogg"),
        output_path=Path("/tmp/outputs"),
        audio_format="ogg",
    )

    assert cmd == [
        "demucs",
        "-o",
        str(Path("/tmp/outputs")),
        str(Path("/tmp/input/song.ogg")),
    ]


def test_run_separation_success(monkeypatch, tmp_path):
    processor = DemucsProcessor(
        output_dir=tmp_path / "outputs",
        log_path=tmp_path / "logs" / "demucs.log",
    )

    captured = {}

    def fake_run(cmd, stdout, stderr, timeout):
        captured["cmd"] = cmd
        captured["timeout"] = timeout
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(
        "app.infrastructure.services.demucs_processor.subprocess.run",
        fake_run,
    )

    processor.run_separation(
        input_path=Path("/tmp/input/song.mp3"),
        audio_format="mp3",
        job_id="job-1",
    )

    assert captured["cmd"] == [
        "demucs",
        "-o",
        str(tmp_path / "outputs"),
        str(Path("/tmp/input/song.mp3")),
        "--mp3",
    ]
    assert captured["timeout"] == 300

    log_file = tmp_path / "logs" / "demucs_job-1.log"
    assert log_file.exists()


def test_run_separation_raises_on_nonzero_exit_code(monkeypatch, tmp_path):
    processor = DemucsProcessor(
        output_dir=tmp_path / "outputs",
        log_path=tmp_path / "logs" / "demucs.log",
    )

    def fake_run(cmd, stdout, stderr, timeout):
        return SimpleNamespace(returncode=2)

    monkeypatch.setattr(
        "app.infrastructure.services.demucs_processor.subprocess.run",
        fake_run,
    )

    with pytest.raises(RuntimeError, match="Demucs ended with the code 2"):
        processor.run_separation(
            input_path=Path("/tmp/input/song.mp3"),
            audio_format="mp3",
            job_id="job-1",
        )
