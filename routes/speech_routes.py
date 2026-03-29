import os
import uuid
from flask import Blueprint, request, jsonify, send_file, current_app

from middleware.auth_middleware import token_required
from services.tts_service import generate_speech


speech_bp = Blueprint("speech", __name__)


# ==========================
# 🔊 TEXT → SPEECH
# ==========================
@speech_bp.route("/tts", methods=["POST"])
@token_required
def text_to_speech():
    try:
        data = request.get_json()

        text = data.get("text")

        if not text:
            return jsonify({"error": "Text is required"}), 400

        # Generate unique filename
        filename = f"{uuid.uuid4()}.mp3"
        output_folder = "uploads/audio"

        os.makedirs(output_folder, exist_ok=True)

        file_path = os.path.join(output_folder, filename)

        # Generate speech
        success = generate_speech(text, file_path)

        if not success:
            return jsonify({"error": "Failed to generate speech"}), 500

        return jsonify({
            "message": "Speech generated successfully",
            "audio_url": f"/speech/play/{filename}"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# ▶️ PLAY AUDIO
# ==========================
@speech_bp.route("/play/<filename>", methods=["GET"])
def play_audio(filename):
    try:
        file_path = os.path.join("uploads/audio", filename)

        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        return send_file(file_path, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# ❌ DELETE AUDIO FILE
# ==========================
@speech_bp.route("/delete/<filename>", methods=["DELETE"])
@token_required
def delete_audio(filename):
    try:
        file_path = os.path.join("uploads/audio", filename)

        if os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({
            "message": "Audio deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500