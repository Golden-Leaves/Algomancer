from __future__ import annotations
from typing import Any
from pathlib import Path
import pygame
from Components.utils import get_screen_color
from Components.logging import DebugLogger
from Structures.base import VisualElement

FONT_PATH = Path("assets") / "fonts" / "DejaVuSans.ttf"
FONT_SIZE = 20
TEXT_COLOR = (255,255,255)

class Cell(VisualElement):
    """A visual representation of a single array cell."""

    def __init__(
        self, value: object, pos: tuple[float, float],*groups: pygame.sprite.AbstractGroup,surface: pygame.Surface = None,
        width: int = 65, height: int = 65,
        fill_color: tuple[int, int, int] = None,
        border_color: tuple[int, int, int] = (255, 255, 255),border_width: int = 1, border_radius: int = 0
        
    ) -> None:
        self.logger = DebugLogger(logger_name=f"{__name__}.{self.__class__.__name__}")
        self.logger.debug("Height: %s", height)
        super().__init__(pos,width,height,surface=surface,*groups)
        self.value = value
        self.text = pygame.font.Font(FONT_PATH.as_posix(), FONT_SIZE).render(
            str(value), True, TEXT_COLOR
        )
        self.fill_color = fill_color if fill_color is not None else get_screen_color()
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius

    def draw(self, surface: pygame.Surface,fill_color: tuple[int, int, int] = None,
             border_color: tuple[int, int, int] = None,border_width: int = None,border_radius: int = None) -> None:
        """Render the cell and its text onto the given surface."""
        if surface is None:
            surface = self.surface
        if fill_color is None:
            fill_color = self.fill_color
        if border_color is None:
            border_color = self.border_color
        if border_width is None:
            border_width = self.border_width
        if border_radius is None:
            border_radius = self.border_radius
        
        
        pygame.draw.rect(surface, fill_color, self.rect,width=border_width,border_radius=border_radius)
        pygame.draw.rect(surface, border_color, self.rect,border_width)
        
        text_rect = self.text.get_rect(center=self.rect.center)
        surface.blit(self.text, text_rect)
        
    def update(self):        
        self.pos.update(self.rect.center)
    
    def set_value(self,value:Any):
        self.value = value
        self.text = pygame.font.Font(FONT_PATH.as_posix(), FONT_SIZE).render(
            str(value), True, TEXT_COLOR
        )
        text_rect = self.text.get_rect(center=self.rect.center)
        self.surface.blit(self.text, text_rect)
        
        
class Node(VisualElement):
    def __init__(self,value, pos,radius:int = 40, *groups, surface: pygame.Surface = None,
                 fill_color: tuple[int, int, int] = None,
                 border_color: tuple[int, int, int] = (255, 255, 255),border_width: int = 1, border_radius: int = 0):
        super().__init__(pos, radius * 2, radius * 2, surface, *groups)
        self.logger = DebugLogger(logger_name=f"{__name__}.{self.__class__.__name__}")
        self.radius = radius
        self.value = value
        self.fill_color = fill_color if fill_color is not None else get_screen_color()
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.text = pygame.font.Font(FONT_PATH.as_posix(), FONT_SIZE).render(str(value), True, TEXT_COLOR)
        self.text_rect = self.text.get_rect(center=self.rect.center)
    
    def draw(self,surface: pygame.Surface,
             fill_color: tuple[int, int, int] = None,
             border_color: tuple[int, int, int] = None,border_width: int = None,border_radius: int = None) -> None:
        surface = surface if surface is not None else self.surface
        fill_color = fill_color if fill_color is not None else self.fill_color    
        border_color = border_color if border_color is not None else self.border_color
        border_width = border_width if border_width is not None else self.border_width
        border_radius = border_radius if border_radius is not None else self.border_radius

        pygame.draw.circle(surface, fill_color, self.rect.center, self.radius,width=border_width)
        pygame.draw.circle(surface, border_color, self.rect.center, self.radius,border_width)
        surface.blit(self.text, self.text_rect)
    
    def update(self):
        self.pos.update(self.rect.center)
