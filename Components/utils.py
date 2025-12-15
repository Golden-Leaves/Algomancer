from __future__ import annotations

from pathlib import Path
import pygame

ASSETS_DIR = Path("assets") / "images"


def load_png(
    filename: str, width: float = 1.0, height: float = 1.0
) -> tuple[pygame.Surface, pygame.Rect]:
    """
    Load an image from the assets directory and return the loaded image and its rectangle.

    Args:
        filename: The filename of the image to load.
        width: The width multiplier of the image. Must be positive.
        height: The height multiplier of the image. Must be positive.

    Returns:
        A tuple containing the loaded image and its rectangle.

    Raises:
        FileNotFoundError: If the requested image file does not exist.
        ValueError: If ``width`` or ``height`` is non-positive.
    """

    if width <= 0 or height <= 0:
        raise ValueError("Width and height multipliers must be positive values.")

    image_path = ASSETS_DIR / filename
    if not image_path.exists():
        raise FileNotFoundError(f"Could not load image: {image_path}")

    image = pygame.image.load(image_path.as_posix())
    image = image.convert_alpha() if image.get_alpha() is not None else image.convert()

    scaled_image = pygame.transform.smoothscale(
        image,
        (int(image.get_width() * width), int(image.get_height() * height)),
    )
    return scaled_image, scaled_image.get_rect()
def get_screen_color() -> pygame.Color:
    """
    Get the color of the pixel at the top-left corner of the screen.

    Returns:
        pygame.Color: The color of the pixel at the top-left corner of the screen.
    """
    screen: pygame.Surface = pygame.display.get_surface()
    if screen is None:
        return pygame.Color(0, 0, 0)
    color: tuple[int, int, int, int] = screen.get_at((0, 0))
    return pygame.Color(*color)
