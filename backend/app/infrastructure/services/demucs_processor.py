import asyncio
import subprocess
from pathlib import Path
from typing import List

from app.application.interfaces.audio_processor_interface import IAudioProcessor


class DemucsProcessor(IAudioProcessor):
    """
    A specific implementation of the Demucs CLI-utility.
    It contains pure automation code without abstractions.
    """

    _DEMUCS_FORMAT_FLAGS = {
        "mp3": ["--mp3"],
        "flac": ["--flac"],
        "wav": ["--int24"]
    }

    _TIMEOUT = 300

    _SEMAPHORE = asyncio.Semaphore(2)  # Semaphore allows only two tasks


    def __init__(self, output_dir: Path, log_path: Path):
        self.output_dir = output_dir
        self.log_path = log_path

    async def run_separation(self, input_path, audio_format, job_id) -> None:
        cmd = self._prepare_command(
            input_path, self.output_dir, audio_format
        )

        log_path = self.log_path.parent / f"demucs_{job_id}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        async with self._SEMAPHORE:
            try:
                return_code = await asyncio.wait_for(
                    # While two tasks are available, to_thread executes 
                    # one task in a separate thread
                    asyncio.to_thread(self._run_subprocess,
                                      cmd, log_path
                                     ),
                    timeout=self._TIMEOUT
                )
            except asyncio.TimeoutError:
                raise RuntimeError("Demucs timeout")

        if return_code != 0:
            raise RuntimeError("Demucs failed")

    def _run_subprocess(self, cmd, log_path: Path):
        with open(log_path, "w", encoding="utf-8") as log:
            return subprocess.run(cmd, stdout=log, stderr=log).returncode

    def _prepare_command(self, input_path: Path, output_path: Path,
                         audio_format: str) -> List[str]:
        cmd = ["demucs", "-o", str(output_path), str(input_path)]

        if audio_format in self._DEMUCS_FORMAT_FLAGS:
            cmd.extend(self._DEMUCS_FORMAT_FLAGS[audio_format])

        return cmd
