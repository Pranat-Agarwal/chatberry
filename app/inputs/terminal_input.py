from app.services.groq_service import ask_groq
from app.inputs.text_input import get_text_input
from app.inputs.file_input import get_file_input
from app.inputs.speech_input import get_speech_input
from app.inputs.image_input import get_image_input, IMAGE_AVAILABLE


def main():
    print("\n🔹 ChatBerry Terminal")

    print("1. Text input")
    print("2. File input (.txt / .pdf)")
    print("3. Speech input (audio file)")
    if IMAGE_AVAILABLE:
        print("4. Image input (OCR)")
    print("Type 'exit' to quit\n")

    while True:
        choice = input("Choose: ").strip()

        if choice == "exit":
            break

        if choice == "1":
            query = get_text_input()
        elif choice == "2":
            query = get_file_input()
        elif choice == "3":
            query = get_speech_input()
        elif choice == "4" and IMAGE_AVAILABLE:
            query = get_image_input()
        else:
            print("Invalid choice")
            continue

        if not query:
            print("Empty input")
            continue

        response = ask_groq(query)
        print("\n🤖 Bot:", response, "\n")


if __name__ == "__main__":
    main()
