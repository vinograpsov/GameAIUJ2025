import pygame


class Obstacle:
    def __init__(self, x, y, radius, color):
        self.pos = pygame.Vector2(x, y)
        self.radius = radius
        self.color = color

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)