import pytesseract
from PIL import Image
import os


# ==========================
# 📄 TXT FILE PROCESSING
# ==========================
def process_text_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"❌ TXT Read Error: {str(e)}")
        return "Error reading text file."


# ==========================
# 🖼 IMAGE OCR PROCESSING
# ==========================
def process_image_file(file_path):
    try:
        # Load image
        image = Image.open(file_path)

        # Optional: convert to grayscale (better OCR)
        image = image.convert("L")

        # OCR extraction
        text = pytesseract.image_to_string(image)

        return text.strip()

    except Exception as e:
        print(f"❌ OCR Error: {str(e)}")
        return "Error extracting text from image."


# ==========================
# 🧹 CLEANUP FILE (OPTIONAL)
# ==========================
def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"❌ File delete error: {str(e)}")