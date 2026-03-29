import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from middleware.auth_middleware import token_required
from services.file_service import process_text_file, process_image_file


file_bp = Blueprint("file", __name__)


# ==========================
# 📁 CHECK ALLOWED FILE
# ==========================
def allowed_file(filename):
    allowed_extensions = current_app.config.get("ALLOWED_EXTENSIONS", {"txt", "png", "jpg", "jpeg"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


# ==========================
# 📤 UPLOAD FILE
# ==========================
@file_bp.route("/upload", methods=["POST"])
@token_required
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400

        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")

        # Ensure upload directory exists
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # ==========================
        # 📄 PROCESS FILE
        # ==========================
        file_ext = filename.rsplit(".", 1)[1].lower()

        if file_ext == "txt":
            extracted_text = process_text_file(file_path)

        else:
            extracted_text = process_image_file(file_path)

        return jsonify({
            "message": "File processed successfully",
            "filename": filename,
            "content": extracted_text
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# 📄 DIRECT TEXT INPUT (OPTIONAL)
# ==========================
@file_bp.route("/text", methods=["POST"])
@token_required
def direct_text():
    try:
        data = request.get_json()
        text = data.get("text")

        if not text:
            return jsonify({"error": "Text is required"}), 400

        return jsonify({
            "message": "Text received successfully",
            "content": text
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500