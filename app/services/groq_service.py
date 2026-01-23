import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def ask_groq(prompt: str) -> str:
    """
    Send prompt to Groq and return text response
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. "
            "Set it in environment variables or .env file."
        )

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content
