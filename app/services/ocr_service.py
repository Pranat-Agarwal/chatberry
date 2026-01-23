from io import BytesIO
from PIL import Image
import pytesseract


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from an image using OCR.

    :param image_bytes: raw image bytes
    :return: extracted text
    """

    try:
        image = Image.open(BytesIO(image_bytes))
    except Exception:
        return ""

    text = pytesseract.image_to_string(image)

    return text.strip()
