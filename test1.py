import pygame
from pygame.locals import *
pygame.init()
BG_COLOR = (0, 0, 0)
size = width, height = (640, 480)
screen = pygame.display.set_mode(size,pygame.RESIZABLE)
speed = [2,2]
clock = pygame.time.Clock()
running = True
dt = 0
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

ball = pygame.image.load("dvd_logo.png").convert_alpha()
ballrect = ball.get_rect()

while running:
    width,height = screen.get_rect().size
    screen.fill(BG_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w,event.h), pygame.RESIZABLE)
            
    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[-1] = -speed[-1]
    screen.blit(ball, ballrect)
    pygame.display.flip()
    dt = clock.tick(60) / 1000
pygame.quit()