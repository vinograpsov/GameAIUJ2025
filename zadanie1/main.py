import pygame
import random
import sys 

from obstacle import Obstacle
from player import Player
from enemy import Enemy

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


enemies = []
for _ in range(5):
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    enemies.append(Enemy(x, y))


running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if  event.type == pygame.QUIT:
            running = False

    player.update_angle()
    player.handle_input()
    


    for o in obstacles:
        player.resolve_collision(o)
            

    for e in enemies:
        e.update(player)
         
        for o in obstacles:
            e.resolve_collision(o)

    screen.fill((50, 50, 50))
    pygame.draw.rect(screen, (0,0,0), (0,0, WIDTH, HEIGHT), 10)

    for o in obstacles:
        o.draw(screen)

    for e in enemies:
        e.draw(screen)

    player.draw(screen)


    pygame.display.flip()

pygame.quit()
sys.exit()