import os
from abc import ABC
from typing import Optional

import pyaudio
from pocketsphinx._pocketsphinx import Decoder
from sphinxbase.sphinxbase import Config
from pocketsphinx import *

from lib.voice_module import VoiceModule, VoiceModuleConfig


class ModulePocketsphinx(VoiceModule, ABC):

    def __init__(self, config: VoiceModuleConfig):
        super().__init__(config)
        self.config = config

        self.m_decoder = None
        self.m_stream = None
        self.m_pyaudio = None
        self.m_decoder_config = None

    def setup(self) -> bool:
        self.m_decoder_config = Config(
            hmm=self.config.model, # os.path.join('model', 'en-us/en-us'),
            dict=self.config.dictionary, #os.path.join('model', 'en-us/cmudict-en-us.dict'),
            kws=self.config.command_file,
            logfn='/dev/null'
        )

        self.m_pyaudio = pyaudio.PyAudio()
        self.m_stream = self.m_pyaudio.open(
            format=self.config.sample_format,
            channels=self.config.channels,
            rate=self.config.sampling_rate,
            input=True
        )

        # Process audio chunk by chunk. On keyword detected perform action and restart search
        self.m_decoder = Decoder(self.m_decoder_config)

        return True

    def set_command_list_file(self, filename: str) -> None:
        self.config.command_file = filename
        self.m_decoder_config.kws = filename

    def start_listening(self) -> None:
        self.m_stream.start_stream()
        self.m_decoder.start_utt()
        pass

    def stop_listening(self) -> None:
        self.m_decoder.end_utt()
        self.m_stream.stop_stream()
        pass

    def loop(self) -> Optional[str]:
        print("Detection started")

        buf = self.m_stream.read(1024)

        self.m_decoder.process_raw(buf, False, False)
        command: str | None = None

        if self.m_decoder.hyp() is not None:
            #print([(seg.word, seg.prob, seg.start_frame, seg.end_frame) for seg in self.m_decoder.seg()])
            #print("Detected keyword, restarting search")

            #
            # Here you run the code you want based on keyword
            #
            # @todo: why did we iterate here again?
            for w_seg in self.m_decoder.seg():
                command = w_seg.word.rstrip()
                # self.doCommand(w_seg.word.rstrip())
                break

            self.m_decoder.end_utt()
            self.m_decoder.start_utt()

        return command

    def restart(self) -> None:
        self.stop_listening()
        self.cleanup()
        self.setup()

    def cleanup(self) -> None:
        self.stop_listening()
        self.m_stream.close()
        self.m_pyaudio.terminate()
        pass
