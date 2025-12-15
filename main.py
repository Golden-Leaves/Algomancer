import pygame
from pygame.locals import *
from Components.utils import *
from Structures.primitives import Cell,Node
import math

def main():
    pygame.init()
    clock = pygame.time.Clock()
    BG_COLOR = (20, 20, 30)
    size = (640, 480)
    screen = pygame.display.set_mode(size,pygame.RESIZABLE)
    pygame.display.set_caption("Algomancer")
    screen.fill(BG_COLOR)
    running = True
    cell = Cell(1,(screen.get_size()[0] // 2,screen.get_size()[1] // 2))
    node = Node(1,(screen.get_size()[0] // 3,screen.get_size()[1] // 3))
    while running:
        screen.fill(BG_COLOR)
        cell.draw(screen)
        node.draw(screen)
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w,event.h), pygame.RESIZABLE)
        clock.tick(60)
        pygame.display.flip()
    
if __name__ == "__main__":
    main()