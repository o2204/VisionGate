from TTS.api import TTS
import os
from pathlib import Path

from src.core.constant_manger import VOICE_DIR

tts = TTS(model_name="tts_models/en/vctk/vits")


Path(VOICE_DIR).mkdir(parents=True, exist_ok=True)


def speak_access(name: str | None, allowed=True):

    if allowed and name:
        text = f"Welcome {name}. Access granted."
        file_name = f"welcome_{name.lower()}.wav"

    else:
        text = "Access denied."
        file_name = "access_denied.wav"

    voice_path = f"{VOICE_DIR}/{file_name}"

    if not os.path.exists(voice_path):

        tts.tts_to_file(
            text=text,
            speaker="p225",
            file_path=voice_path
        )

    os.system(f"aplay {voice_path}")