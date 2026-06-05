import subprocess
from pathlib import Path
from typing import List

from app.application.interfaces.audio_processor_interface import IAudioProcessor


class DemucsProcessor(IAudioProcessor):
    """
    Synchronous wrapper over Demucs CLI.
    It runs inside the Celery worker — the event loop is not needed.
    The concurrency limit is set by the --concurrency flag
    when starting the worker.
    """

    _DEMUCS_FORMAT_FLAGS = {
        "mp3": ["--mp3"],
        "flac": ["--flac"],
        "wav": ["--int24"],
    }
    _TIMEOUT = 300

    def __init__(self, output_dir: Path, log_path: Path):
        self.output_dir = output_dir
        self.log_path = log_path

    def run_separation(
        self, input_path: Path, audio_format: str, job_id: str
    ) -> None:
        # Executes the source separation process using Demucs
        cmd = self._prepare_command(input_path, self.output_dir, audio_format)

        log_path = self.log_path.parent / f"demucs_{job_id}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        return_code = self._run_subprocess(cmd, log_path)
        if return_code != 0:
            raise RuntimeError(
                f"Demucs ended with the code {return_code}. "
                f"Log: {log_path}"
            )

    def _run_subprocess(self, cmd: List[str], log_path: Path) -> int:
        # Runs a command as a subprocess and logs its output
        with open(log_path, "w", encoding="utf-8") as log:
            result = subprocess.run(
                cmd,
                stdout=log,
                stderr=log,
                timeout=self._TIMEOUT,
            )
        return result.returncode

    def _prepare_command(
        self, input_path: Path, output_path: Path, audio_format: str
    ) -> List[str]:
        # Builds and returns a command line
        cmd = ["demucs", "-o", str(output_path), str(input_path)]
        if audio_format in self._DEMUCS_FORMAT_FLAGS:
            cmd.extend(self._DEMUCS_FORMAT_FLAGS[audio_format])
        return cmd
