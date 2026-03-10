from PIL import Image

def crop_top_square(image_path: str) -> Image.Image:
    img = Image.open(image_path).convert("RGBA")

    width, height = img.size

    # velikost ctverce = menší strana
    square_size = min(width, height)

    # chceme vyríznout stred horizontálne
    left = (width - square_size) // 2
    right = left + square_size

    # a horní cást vertikálne
    top = 0
    bottom = square_size

    cropped = img.crop((left, top, right, bottom))

    return cropped
