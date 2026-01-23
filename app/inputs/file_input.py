from PyPDF2 import PdfReader


def get_file_input() -> str:
    path = input("Enter file path (.txt / .pdf): ").strip().strip('"')

    try:
        if path.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        if path.endswith(".pdf"):
            reader = PdfReader(path)
            content = ""

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    content += text

            if not content.strip():
                print("❌ PDF has no extractable text")
                return ""

            return content

        print("❌ Unsupported file type")
        return ""

    except Exception as e:
        print("❌ File error:", e)
        return ""
