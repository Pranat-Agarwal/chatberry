from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.groq_service import ask_groq
from app.services.file_service import extract_text_from_file
from app.services.ocr_service import extract_text_from_image
from app.services.speech_service import speech_to_text
from app.services.tts_service import text_to_speech
from app.services.image_service import text_to_image
from app.models.chat import ChatHistory

router = APIRouter()

# -------------------------------------------------
# MULTIMODAL CHAT ENDPOINT
# Input: text | file | image | voice
# Output: text | image | voice
# -------------------------------------------------

@router.post("/chat")
async def chat(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),

    output_voice: bool = Form(False),
    output_image: bool = Form(False),

    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user),
):
    prompt = ""

    # -------- TEXT --------
    if text:
        prompt += text.strip() + "\n"

    # -------- FILE --------
    if file:
        data = await file.read()
        prompt += extract_text_from_file(file.filename, data) + "\n"

    # -------- IMAGE --------
    if image:
        img_bytes = await image.read()
        extracted = extract_text_from_image(img_bytes)
        if extracted:
            prompt += extracted + "\n"

    # -------- VOICE --------
    if audio:
        audio_bytes = await audio.read()
        voice_text = speech_to_text(audio_bytes)
        if voice_text:
            prompt += voice_text + "\n"

    if not prompt.strip():
        raise HTTPException(status_code=400, detail="No input provided")

    # -------- LLM --------
    try:
        response_text = ask_groq(prompt)
    except Exception:
        raise HTTPException(status_code=500, detail="AI service error")

    # -------- SAVE HISTORY --------
    if user_id is not None:
        db.add(ChatHistory(
            user_id=user_id,
            message=prompt.strip(),
            response=response_text
        ))
        db.commit()

    result = {
        "text": response_text
    }

    # -------- VOICE OUTPUT --------
    if output_voice:
        audio_bytes = text_to_speech(response_text)
        result["voice"] = audio_bytes.hex()

    # -------- IMAGE OUTPUT --------
    if output_image:
        image_bytes = text_to_image(response_text)
        result["image"] = image_bytes.hex()

    return result

from fastapi import HTTPException

@router.get("/history")
def get_chat_history(
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user_id)
        .order_by(ChatHistory.created_at.desc())
        .all()
    )

    return [
        {
            "id": c.id,
            "message": c.message,
            "response": c.response,
            "created_at": c.created_at.isoformat(),
        }
        for c in chats
    ]
