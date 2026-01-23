try:
    import pytesseract
    from PIL import Image
    IMAGE_AVAILABLE = True
except Exception:
    IMAGE_AVAILABLE = False


def get_image_input() -> str:
    if not IMAGE_AVAILABLE:
        print("❌ Image OCR not available on this system")
        return ""

    path = input("Enter image path: ").strip().strip('"')

    try:
        image = Image.open(path)
        text = pytesseract.image_to_string(image)

        if not text.strip():
            print("❌ No readable text in image")
            return ""

        return text

    except Exception as e:
        print("❌ Image error:", e)
        return ""
