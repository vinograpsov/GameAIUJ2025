import pygame
import math

class Player:

    def __init__(self, x, y, debug=False):
        self.pos = pygame.Vector2(x, y)
        self.angle = 0
        self.speed = 5
        self.debug = debug
        self. collider_radius = 20

    def handle_input(self):

        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(math.cos(self.angle), math.sin(self.angle))

        if keys[pygame.K_w]:
            self.pos += direction * self.speed
        if keys[pygame.K_s]:    
            self.pos -= direction * self.speed
        if keys[pygame.K_a]:
            perp_direction = pygame.Vector2(-direction.y, direction.x)
            self.pos += perp_direction * self.speed
        if keys[pygame.K_d]:
            perp_direction = pygame.Vector2(direction.y, -direction.x)
            self.pos += perp_direction * self.speed

    def update_angle(self):
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.pos.x
        dy = mouse_pos[1] - self.pos.y
        self.angle = math.atan2(dy, dx)

    def draw(self,surface):
        front = self.pos + pygame.Vector2(math.cos(self.angle), math.sin(self.angle)) * 30
        left = self.pos + pygame.Vector2(math.cos(self.angle + 2.5), math.sin(self.angle + 2.5)) * 20
        right = self.pos + pygame.Vector2(math.cos(self.angle - 2.5), math.sin(self.angle - 2.5)) * 20

        pygame.draw.polygon(surface, (0, 0, 255), [front, left, right])

        if self.debug:
            pygame.draw.circle(surface, (255,0,0), (int(self.pos.x), int(self.pos.y)), self.collider_radius, 1)