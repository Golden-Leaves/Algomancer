import pygame
from pygame.locals import *
from Components.utils import *
import math
class DVD(pygame.sprite.Sprite):
    def __init__(self, velocity: tuple[float, float],bounce: bool = True) -> None:
        """
        Initialises a DVD object with the specified velocity.
        
        Parameters
        ----------
        velocity : tuple[float, float]
            The initial velocity of the ball as a tuple of (x, y) components.
            
        Returns
        -------
        None
        """
        super().__init__()
        screen = pygame.display.get_surface()
        self.image, self.rect = load_png("dvd_logo.png",width=0.5,height=0.5)
        self.area = screen.get_rect()
        self.velocity = pygame.math.Vector2(velocity)
        
    def update(self) -> None:
        """
        Updates the position of the DVD based on its current vector.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if self.rect.left < 0 or self.rect.right > self.area.width:
            self.velocity.x = -self.velocity.x
        if self.rect.top < 0 or self.rect.bottom > self.area.height:
            self.velocity.y = -self.velocity.y
        self.rect.move_ip(self.velocity.x, self.velocity.y)
        
    def move(self):
        pass
    
        
def main():
    pygame.init()
    clock = pygame.time.Clock()
    BG_COLOR = (20, 20, 30)
    size = (640, 480)
    screen = pygame.display.set_mode(size,pygame.RESIZABLE)
    pygame.display.set_caption("Hello World")
    screen.fill(BG_COLOR)
    running = True
    dvd_pos = pygame.math.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    dvd = DVD((1,1),bounce=True)
    while running:
        screen.fill(BG_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w,event.h), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == K_w:
                    dvd.pos -= 20
                if event.key == K_s:
                    dvd.pos += 20
                if event.key == K_a:
                    dvd.pos -= 20
                if event.key == K_d:
                    dvd.pos += 20
        
        screen.blit(dvd.image, dvd.rect)
        pygame.display.flip()
        clock.tick(60)
if __name__ == "__main__":
    main()