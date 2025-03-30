import os
from abc import ABC

import pyaudio
from sphinxbase.sphinxbase import Config
from pocketsphinx import *

from lib.voice_module import VoiceModule


class ModulePocketsphinx(VoiceModule, ABC):

    def __init__(self):
        super().__init__()
        self.m_decoder = None
        self.m_stream = None
        self.m_pyaudio = None
        self.m_config = None

    def setup(self) -> bool:
        self.m_config = Config(
            hmm=os.path.join('model', 'en-us/en-us'),
            dict=os.path.join('model', 'en-us/cmudict-en-us.dict'),
            kws='command.list',
            logfn='/dev/null'
        )

        self.m_pyaudio = pyaudio.PyAudio()
        self.m_stream = self.m_pyaudio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True)

        # Process audio chunk by chunk. On keyword detected perform action and restart search
        self.m_decoder = Decoder(self.m_config)

        return True

    def start_listening(self) -> None:
        pass

    def pause_listening(self) -> None:
        pass

    def stop_listening(self) -> None:
        pass

    def cleanup(self) -> None:
        pass
