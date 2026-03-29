from gtts import gTTS
import pyttsx3
from config.config import Config


# ==========================
# 🔊 GENERATE SPEECH
# ==========================
def generate_speech(text, output_path):
    """
    Generate speech from text
    Supports:
    - gTTS (online, better voice)
    - pyttsx3 (offline)
    """

    try:
        engine_type = Config.TTS_ENGINE

        if engine_type == "gtts":
            return generate_gtts(text, output_path)

        elif engine_type == "pyttsx3":
            return generate_pyttsx3(text, output_path)

        else:
            print("⚠️ Unknown TTS engine")
            return False

    except Exception as e:
        print(f"❌ TTS Error: {str(e)}")
        return False


# ==========================
# 🌐 gTTS (ONLINE)
# ==========================
def generate_gtts(text, output_path):
    try:
        tts = gTTS(text=text, lang="en")
        tts.save(output_path)
        return True
    except Exception as e:
        print(f"❌ gTTS Error: {str(e)}")
        return False


# ==========================
# 💻 pyttsx3 (OFFLINE)
# ==========================
def generate_pyttsx3(text, output_path):
    try:
        engine = pyttsx3.init()

        # Save to file
        engine.save_to_file(text, output_path)
        engine.runAndWait()

        return True

    except Exception as e:
        print(f"❌ pyttsx3 Error: {str(e)}")
        return False