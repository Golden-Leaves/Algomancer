from __future__ import annotations

import pygame


class VisualElement(pygame.sprite.Sprite):
    """Base class for visual elements rendered with pygame sprites."""

    def __init__(
        self, pos: tuple[float, float], *groups: pygame.sprite.AbstractGroup
    ) -> None:
        super().__init__(*groups)
        self.pos: pygame.math.Vector2 = pygame.math.Vector2(pos)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, 20, 20)

    def update(self) -> None:
        """Update the sprite each frame. Subclasses may override as needed."""

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the sprite onto the provided screen surface."""
