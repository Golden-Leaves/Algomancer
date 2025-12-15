from __future__ import annotations

from pathlib import Path
import pygame

from Structures.base import VisualElement

FONT_PATH = Path("assets") / "fonts" / "DejaVuSans.ttf"
FONT_SIZE = 20
TEXT_COLOR = (0, 0, 0)
BACKGROUND_COLOR = (255, 255, 255)


class Cell(VisualElement):
    """A visual representation of a single array cell."""

    def __init__(
        self, value: object, pos: tuple[float, float], *groups: pygame.sprite.AbstractGroup
    ) -> None:
        super().__init__(pos, *groups)
        self.value = value
        self.text = pygame.font.Font(FONT_PATH.as_posix(), FONT_SIZE).render(
            str(value), True, TEXT_COLOR
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Render the cell and its text onto the given surface."""
        pygame.draw.rect(surface, BACKGROUND_COLOR, self.rect)
        text_rect = self.text.get_rect(center=self.rect.center)
        surface.blit(self.text, text_rect)
