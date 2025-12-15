import pygame
from pygame.locals import *
def main():
    pygame.init()
    BG_COLOR = (0, 0, 0)
    size = ((400, 300))
    screen = pygame.display.set_mode(size,pygame.RESIZABLE)
    pygame.display.set_caption("Hello World")
    running = True
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(BG_COLOR)
    
    font = pygame.font.Font(r"static\fonts\DejaVuSans.ttf", 80)
    text = font.render("Hello World", 1, (255, 255, 255))
    text_size = text.get_size()
    text = pygame.transform.smoothscale(text, (text_size[0] // 2, text_size[1] // 2))
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    background.blit(text, textpos)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w,event.h), pygame.RESIZABLE)
                background = pygame.Surface(screen.get_size())
                background = background.convert()
                background.fill(BG_COLOR)
                textpos = text.get_rect()
                textpos.centerx = background.get_rect().centerx
                background.blit(text, textpos)
        screen.blit(background, (0, 0))
        pygame.display.flip()
if __name__ == "__main__":
    main()