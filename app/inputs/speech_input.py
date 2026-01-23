import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os


def get_speech_input() -> str:
    path = input("Enter audio file path (.wav / .mp3): ").strip().strip('"')

    if not os.path.exists(path):
        print("❌ Audio file not found")
        return ""

    recognizer = sr.Recognizer()

    try:
        audio = AudioSegment.from_file(path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
            wav_path = temp.name
            audio.export(wav_path, format="wav")

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)
        print("🗣 Transcribed:", text)
        return text

    except Exception:
        return ""

    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
