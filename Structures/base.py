import pygame
from pygame.locals import *
import math
class VisualElement(pygame.sprite.Sprite):
    def __init__(self,pos,*groups):
        super().__init__(*groups)
        self.pos:pygame.math.Vector2 = pygame.math.Vector2(pos)
        self.rect = pygame.Rect(self.pos.x,self.pos.y,20,20)

    def update(self):
        pass
    def draw(self,screen):
        pass