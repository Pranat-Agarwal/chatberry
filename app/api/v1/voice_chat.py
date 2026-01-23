from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import JSONResponse
from typing import Optional
import base64

from app.services.groq_service import ask_groq
from app.services.speech_service import speech_to_text
from app.services.tts_service import text_to_speech
from app.services.image_service import text_to_image
from app.services.file_service import extract_text_from_file
from app.services.ocr_service import extract_text_from_image

# ❌ NO prefix here
router = APIRouter(tags=["Voice Chat"])


@router.post("/voice-chat")
async def voice_chat(
    request: Request,
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None),
):
    """
    Main multimodal ChatBerry endpoint
    """

    user_text = ""

    # -------- TEXT INPUT --------
    if request.headers.get("content-type", "").startswith("application/json"):
        body = await request.json()
        user_text = body.get("text", "")

    # -------- VOICE INPUT --------
    elif audio:
        user_text = speech_to_text(await audio.read())

    # -------- IMAGE INPUT --------
    elif image:
        user_text = extract_text_from_image(await image.read())

    # -------- FILE INPUT --------
    elif file:
        user_text = extract_text_from_file(
            file.filename,
            await file.read()
        )

    if not user_text.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "No valid input provided"},
        )

    # -------- LLM --------
    llm_response = ask_groq(user_text)

    response = {"text": llm_response}
    intent = user_text.lower()

    # -------- VOICE OUTPUT --------
    if any(w in intent for w in ["voice", "say", "read aloud"]):
        audio_mp3 = text_to_speech(llm_response)
        response["audio_base64"] = base64.b64encode(audio_mp3).decode()

    # -------- IMAGE OUTPUT --------
    if any(w in intent for w in ["image", "picture", "show visually"]):
        img_bytes = text_to_image(llm_response)
        response["image_base64"] = base64.b64encode(img_bytes).decode()

    return JSONResponse(content=response)
