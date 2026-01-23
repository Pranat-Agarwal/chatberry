from io import BytesIO
from typing import Optional
import PyPDF2


def extract_text_from_file(filename: str, data: bytes) -> str:
    """
    Extract text from uploaded TXT or PDF files.

    :param filename: original filename
    :param data: raw file bytes
    :return: extracted text
    """

    filename = filename.lower()

    # ---------- TXT ----------
    if filename.endswith(".txt"):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1")

    # ---------- PDF ----------
    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(BytesIO(data))
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text.strip()

    # ---------- UNSUPPORTED ----------
    raise ValueError("Unsupported file type")
