from PIL import Image
import os
import math

MAX_PER_ROW = 4

def combine_dice_images(image_paths: list[str], output_dir: str) -> str:
    images = [Image.open(p).convert("RGBA") for p in image_paths]
    if not images:
        raise ValueError("Žádné obrázky k spojení")

    # Velikosti
    img_width = max(img.width for img in images)
    img_height = max(img.height for img in images)

    rows = math.ceil(len(images) / MAX_PER_ROW)
    cols = min(len(images), MAX_PER_ROW)

    # výsledný obrázek
    combined = Image.new("RGBA", (cols * img_width, rows * img_height), (0,0,0,0))

    for index, img in enumerate(images):
        row = index // MAX_PER_ROW
        col = index % MAX_PER_ROW
        combined.paste(img, (col * img_width, row * img_height), img)

    # uložíme
    filename = f"dice_result.png"
    path = os.path.join(output_dir, filename)
    combined.save(path)
    return path
