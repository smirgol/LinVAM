from abc import ABC
from typing import Optional

from lib.voice_module import VoiceModule
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json


class ModuleVosk(VoiceModule, ABC):
    def __init__(self):
        super().__init__()
        self.buffer = None
        self.command_list = None
        self.stream = None
        self.queue = None
        self.recognizer = None

    def setup(self) -> bool:
        # Load Vosk model (download from https://alphacephei.com/vosk/models)
        model = Model("model/vosk-model-small-en-us-0.15")

        self.command_list = self._load_command_list()

        self.recognizer = KaldiRecognizer(model, 16000, json.dumps(self.command_list))
        self.recognizer.SetMaxAlternatives(1)  # Only return the most likely result
        self.recognizer.SetWords(True)  # Enable word timing (optional)
        self.recognizer.SetPartialWords(False)

        # Queue to store audio data
        self.queue = queue.Queue()

        # Start the microphone stream once
        self.stream = sd.RawInputStream(
            samplerate=16000, blocksize=8000, dtype='int16',
            channels=1, callback=self._callback
        )

        return True

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

    def pause_listening(self) -> None:
        pass

    def stop_listening(self) -> None:
        self.stream.stop()  # Start the stream
        pass

    def cleanup(self) -> None:
        self.stop_listening()
        pass

    @staticmethod
    def _load_command_list() -> list[str]:
        # Load commands and remove the threshold part
        commands = []
        with open("command.list", "r") as f:
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
