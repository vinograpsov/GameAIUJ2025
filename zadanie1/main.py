import pygame
import random
import sys 

from obstacle import Obstacle


pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.displayset_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival Killer Mega Bestseller 3000")

clock = pygame.time.Clock()
FPS = 60

obstacles = []
for _ in range(10):
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    radius = random.randint(20, 100)
    color = (0, 255, 0)
    obstacles.append(Obstacle(x, y, radius, color))




