from abc import ABC, abstractmethod
from pathlib import Path


class IAudioProcessor(ABC):

    @abstractmethod
    async def run_separation(self, input_path: Path,
                             audio_format: str) -> None:
        pass
