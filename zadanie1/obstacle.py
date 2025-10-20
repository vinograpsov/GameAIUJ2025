import pygame
from collider import Collider

class Obstacle:
    def __init__(self, x, y, radius, color):
        self.pos = pygame.Vector2(x, y)
        self.radius = radius
        self.color = color

        self.collider = Collider(x, y, radius)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)


    def draw_debug(self, surface):
        self.collider.draw_debug(surface, color=(255, 255, 0))