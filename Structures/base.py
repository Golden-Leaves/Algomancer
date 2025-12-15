from __future__ import annotations
from Components.logging import DebugLogger
import pygame


class VisualElement(pygame.sprite.Sprite):
    """Base class for visual elements rendered with pygame sprites."""

    def __init__(
        self, pos: tuple[float, float], width: int, height: int, *groups: pygame.sprite.AbstractGroup
    ) -> None:
        super().__init__(*groups)
        self.logger = DebugLogger(logger_name=f"{__name__}.{self.__class__.__name__}")
        self.pos: pygame.math.Vector2 = pygame.math.Vector2(pos)
        self.rect = pygame.Rect(0, 0 , width, height)
        self.rect.center = (self.pos.x, self.pos.y)

    def update(self) -> None:
        """Update the sprite each frame. Subclasses may override as needed."""

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the sprite onto the provided screen surface."""
