import pygame    
from pygame.locals import *
from Structures.base import VisualElement
class Cell(VisualElement):
    def __init__(self,value,pos,*groups):
        self.value = value
        super().__init__(pos,*groups)
        self.text = pygame.font.Font(r"assets\fonts\DejaVuSans.ttf", 20).render(str(value), 1, (0, 0, 0))
    def draw(self,surface):
        pygame.draw.rect(surface,(255,255,255),self.rect)
        text_rect = self.text.get_rect(center=self.rect.center)
        surface.blit(self.text,text_rect)