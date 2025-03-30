from abc import abstractmethod
from typing import Optional


class VoiceModule:

    def __init__(self):
        pass

    @abstractmethod
    def setup(self) -> bool:
        """ Initialize the voice recognition module """
        pass

    @abstractmethod
    def start_listening(self) -> None:
        pass

    @abstractmethod
    def loop(self) -> Optional[str]:
        pass

    @abstractmethod
    def pause_listening(self) -> None:
        pass

    @abstractmethod
    def stop_listening(self) -> None:
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass
