from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap


def text_to_image(text: str) -> bytes:
    """
    Convert text into a PNG image and return image bytes
    """

    # Image size
    width = 800
    padding = 40
    bg_color = (15, 23, 42)     # dark background
    text_color = (255, 255, 255)

    # Wrap text
    wrapped_text = textwrap.fill(text, width=60)

    # Temporary font (default PIL font – deploy safe)
    font = ImageFont.load_default()

    # Calculate height
    lines = wrapped_text.split("\n")
    line_height = font.getbbox("A")[3] + 6
    height = padding * 2 + line_height * len(lines)

    # Create image
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    y = padding
    for line in lines:
        draw.text((padding, y), line, fill=text_color, font=font)
        y += line_height

    # Save image to bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer.read()
