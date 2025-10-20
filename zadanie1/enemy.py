import pygame
from collider import Collider 
import random
import math

class Enemy:

    def __init__(self, x, y, radius = 10, color = (200,50,50), debug = False):
        self.pos = pygame.Vector2(x, y)
        self.radius = radius
        self.color = color
        self.debug = debug
        self.collider_radius = radius


        self.speed = 2
        self.collider = Collider(x, y, self.collider_radius)


    def update(self, player):
        direction = player.pos - self.pos 
        if direction.length_squared() > 0:
            direction = direction.normalize() * self.speed
            self.pos += direction
            self.collider.pos = self.pos


    def resolve_collision(self, obstacle):
        if self.collider.collides_with(obstacle.collider):
            self.collider.resolve_collision(obstacle.collider)
            self.pos = self.collider.pos


    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

        if self.debug:
            self.collider.draw_debug(surface, color=(255, 0, 0))