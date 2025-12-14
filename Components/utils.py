import pygame
import os
def load_png(filename: str, width: float = 1, height: float = 1) -> tuple[pygame.Surface, pygame.Rect]:
    """
    Load an image from the assets directory and return the loaded image
    and its rectangle.

    Args:
        filename (str): The filename of the image to load.
        width (float): The width multiplier of the image. Defaults to 1.
        height (float): The height multiplier of the image. Defaults to 1.

    Returns:
        tuple[pygame.Surface, pygame.Rect]: A tuple containing the loaded
        image and its rectangle.
    """
    fullname = os.path.join("assets","images",filename)
    try:
        image = pygame.image.load(fullname)
        if image.convert_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except FileNotFoundError:
        raise Exception(f"Could not load image: {fullname}")
    
    image = pygame.transform.smoothscale(image, (int(image.get_width() * width), int(image.get_height() * height)))
    return image, image.get_rect()
    