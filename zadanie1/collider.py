import pygame


class Collider: 

    def __init__(self, x, y, radius):
        self.pos = pygame.Vector2(x, y)
        self.radius = radius 

    def collides_with(self, other):
        return self.pos.distance_to(other.pos) < (self.radius + other.radius)
    

    def resolve_collision(self, other):
        delta = self.pos - other.pos
        distance = delta.length()
        if distance == 0:
            delta
            distance = 0.01
        

        overlap = self.radius + other.radius - distance
        if overlap > 0:
            delta.normalize_ip()
            self.pos += delta * overlap


    def draw_debug(self, surface, color=(255, 0, 0)):
        pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), self.radius, 1)