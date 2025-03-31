from abc import abstractmethod
from typing import Optional


class VoiceModuleConfig:
    def __init__(self,
                 sampling_rate: int,
                 sample_format: str,
                 channels: int,
                 model: str,
                 dictionary: Optional[str],
                 command_file: str
                 ):
        self.sampling_rate: int = sampling_rate
        self.sample_format: str | int = sample_format
        self.channels: int = channels
        self.model: str = model
        self.dictionary: str | None = dictionary
        self.command_file: str | None = command_file


class VoiceModule:

    def __init__(self, config: VoiceModuleConfig):
        pass

    @abstractmethod
    def setup(self) -> bool:
        """ Initialize the voice recognition module """
        pass

    @abstractmethod
    def set_command_list_file(self, filename: str) -> None:
        pass

    @abstractmethod
    def start_listening(self) -> None:
        pass

    @abstractmethod
    def stop_listening(self) -> None:
        pass

    @abstractmethod
    def restart(self) -> None:
        pass

    @abstractmethod
    def loop(self) -> Optional[str]:
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass
