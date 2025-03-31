import json
import os
import queue
from abc import ABC
from typing import Optional

import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel

from lib.voice_module import VoiceModule, VoiceModuleConfig


class ModuleVosk(VoiceModule, ABC):
    def __init__(self, config: VoiceModuleConfig):
        super().__init__(config)
        self.config = config
        self.buffer = None
        self.command_list = None
        self.stream = None
        self.queue = None
        self.recognizer = None

        # configure logging of VOSK
        SetLogLevel(-1)

    def setup(self) -> bool:
        # Load Vosk model (download from https://alphacephei.com/vosk/models)
        model = Model(self.config.model)

        self.command_list = self._load_command_list()

        self.recognizer = KaldiRecognizer(model, 16000, json.dumps(self.command_list))
        self.recognizer.SetMaxAlternatives(1)  # Only return the most likely result
        self.recognizer.SetWords(True)  # Enable word timing (optional)
        self.recognizer.SetPartialWords(False)

        # Queue to store audio data
        self.queue = queue.Queue()

        # Start the microphone stream once
        self.stream = sd.RawInputStream(
            samplerate=self.config.sampling_rate, blocksize=8000, dtype='int16',
            channels=self.config.channels, callback=self._callback
        )

        return True

    def set_command_list_file(self, filename: str) -> None:
        self.config.command_file = filename
        self.command_list = self._load_command_list()
        # vosk requires restart, as I found no way to update command list on the fly

    #   self.restart()

    def loop(self) -> Optional[str]:
        data = self.queue.get()

        if self.recognizer.AcceptWaveform(data):
            result = self.recognizer.Result()

            # return recognized command
            result_dict = json.loads(result)
            recognized_text = result_dict.get("alternatives", [])[0].get("text", "").strip() or None

            if not recognized_text:
                return None  # Ignore empty results

            # Check if the full phrase is a complete command
            if recognized_text in self.command_list:
                return recognized_text  # Return recognized command

        return None

    def start_listening(self) -> None:
        # something, probably Qt, is changing the locale, messing up the vosk json string data
        import locale
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        self.stream.start()  # Start the stream
        pass

    def stop_listening(self) -> None:
        self.stream.stop()  # Start the stream
        pass

    def cleanup(self) -> None:
        self.stop_listening()
        self.stream.close()
        pass

    def restart(self) -> None:
        self.stop_listening()
        self.cleanup()
        self.setup()

    def _load_command_list(self) -> list[str]:
        # Load commands and remove the threshold part
        commands = []
        with open(self.config.command_file, "r") as f:
            for line in f:
                command = line.split("/")[0].strip()  # Keep only the command before "/"
                if command:  # Ignore empty lines
                    commands.append(command)

        # Convert to JSON format for Vosk
        return commands

    def _callback(self, indata, frames, time, status):
        """Callback function to receive microphone input"""
        if status:
            print(status)
        self.queue.put(bytes(indata))
