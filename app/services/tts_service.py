from gtts import gTTS
import tempfile
import os

def text_to_speech(text: str) -> bytes:
    tts = gTTS(text=text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        path = f.name

    with open(path, "rb") as audio:
        data = audio.read()

    os.remove(path)
    return data
