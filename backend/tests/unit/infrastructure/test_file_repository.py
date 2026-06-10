import zipfile
from io import BytesIO

import pytest
from app.infrastructure.repositories.file_repository import FileRepository


def test_save_upload_writes_bytes(tmp_path):
    upload_dir = tmp_path / "uploads"
    output_dir = tmp_path / "outputs"
    upload_dir.mkdir()
    output_dir.mkdir()

    repo = FileRepository(upload_dir=upload_dir, output_dir=output_dir)
    stream = BytesIO(b"hello world")

    result = repo.save_upload(stream, "song.mp3", "job-1")

    assert result == upload_dir / "job-1_song.mp3"
    assert result.read_bytes() == b"hello world"


def test_get_upload_path_and_zip_path(tmp_path):
    repo = FileRepository(
        upload_dir=tmp_path / "uploads",
        output_dir=tmp_path / "outputs"
    )

    assert repo.get_upload_path(
        "job-1",
        "song.mp3"
    ) == tmp_path / "uploads" / "job-1_song.mp3"
    assert repo.get_zip_path("job-1") == tmp_path / "outputs" / "job-1.zip"


def test_create_zip_archive_raises_when_source_missing(tmp_path):
    repo = FileRepository(
        upload_dir=tmp_path / "uploads",
        output_dir=tmp_path / "outputs"
    )

    with pytest.raises(
        FileNotFoundError,
        match="No separated tracks were found"
    ):
        repo.create_zip_archive("job-1", "song.mp3")


def test_create_zip_archive_creates_zip(tmp_path):
    output_dir = tmp_path / "outputs"
    source_dir = output_dir / "htdemucs" / "job-1_song"
    source_dir.mkdir(parents=True)

    (source_dir / "vocals.txt").write_text("voice")

    repo = FileRepository(
        upload_dir=tmp_path / "uploads",
        output_dir=output_dir
    )

    zip_path = repo.create_zip_archive("job-1", "song.mp3")

    assert zip_path == output_dir / "job-1.zip"
    assert zip_path.exists()
    assert zipfile.is_zipfile(zip_path)

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        assert any(name.endswith("vocals.txt") for name in names)
