from __future__ import annotations

import threading

import pyttsx3


class TtsService:
    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)

    def speak(self, text: str) -> None:
        if not text:
            return
        thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
        thread.start()

    def _speak_sync(self, text: str) -> None:
        self.engine.say(text)
        self.engine.runAndWait()
