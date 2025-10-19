import pygame
import random
import sys 

from obstacle import Obstacle
from player import Player

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
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


player = Player(WIDTH // 2, HEIGHT // 2, debug=True)

running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if  event.type == pygame.QUIT:
            running = False


    player.update_angle()
    player.handle_input()
    
    screen.fill((50, 50, 50))
    pygame.draw.rect(screen, (0,0,0), (0,0, WIDTH, HEIGHT), 10)

    for o in obstacles:
        o.draw(screen)
    player.draw(screen)


    pygame.display.flip()

pygame.quit()
sys.exit()