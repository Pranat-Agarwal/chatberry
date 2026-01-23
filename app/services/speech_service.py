import speech_recognition as sr
import tempfile
import os


def speech_to_text(audio_bytes: bytes) -> str:
    """
    Convert WAV audio bytes to text using Google Speech Recognition
    """

    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        temp_path = f.name

    try:
        with sr.AudioFile(temp_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)

    except Exception as e:
        print("Speech recognition error:", e)
        return ""

    finally:
        os.remove(temp_path)
