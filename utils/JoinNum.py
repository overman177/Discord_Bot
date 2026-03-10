from PIL import Image
from .config import FONT_DIR
import os

def render_number(number: int, spacing: int = 0) -> Image.Image:

    digits = list(str(number))

    images = []

    # Nacti všechny číslice
    for digit in digits:
        path = os.path.join(FONT_DIR, f"{digit}.png")
        img = Image.open(path).convert("RGBA")
        images.append(img)

    # V�pocet v�sledn� ��rky
    total_width = sum(img.width for img in images) + spacing * (len(images) - 1)
    max_height = max(img.height for img in images)

    # Vytvoren� pr�zdn�ho canvasu (transparent)
    final_image = Image.new("RGBA", (total_width, max_height), (0, 0, 0, 0))

    # Vkl�d�n� c�slic vedle sebe
    x_offset = 0
    for img in images:
        y_offset = (max_height - img.height) // 2
        final_image.paste(img, (x_offset, y_offset), img)
        x_offset += img.width + spacing

    return final_image


