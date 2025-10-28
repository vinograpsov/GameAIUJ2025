#python ligraries
import pygame
import time
import random, math, sys
#game libraries
import transforms
import game_object
import rendering

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival Killer Mega Bestseller 3000")

def GetFixedMousePos(windowSize):
    pygamePos = pygame.mouse.get_pos()
    return [pygamePos[0], windowSize[1] - pygamePos[1]]

def GetWorldMousePos(windowSize, cameraPivot):
    pygamePos = pygame.mouse.get_pos()
    return [pygamePos[0] + cameraPivot[0] - windowSize[0] / 2, windowSize[1] - pygamePos[1] + cameraPivot[1] - windowSize[1] / 2]

def main():
    #------------------------------------------------------------------
    #START
    #------------------------------------------------------------------
    size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
    center = [size[0] / 2, size[1] / 2]
    background = (255, 255, 255)

    deltaTime = time.time()
    pastTime = time.time()

    #Input declaration
    UpDownInput = [0, 0]
    LeftRightInput = [0, 0] 
    RechargeInput = [0, 0] #determines if the player wants to recharge manually
    MouseInputs = [[0, 0, 0], [0, 0, 0]]

    GlobalObjects = []

    #create player (now not moving) object
    Player = game_object.GameObject(transforms.Transform([size[0] / 2, size[1] / 2], 0, [15, 15]), [], None)
    Player.AddComp(rendering.Model('Assets\Triangle.obj', [0, 0, 255]));

    GlobalObjects.append(Player);

    #create cursor object
    Cursor = game_object.GameObject(transforms.Transform([size[0] / 2, size[1] / 2], 0, [15, 15]), [], None)
    GlobalObjects.append(Cursor);
    Cursor.AddComp(rendering.Model('Assets\Cursor.obj', [255, 0, 0]))
    #Cursor.AddComp(physics.Collider(0, [1, 1]))
    GlobalObjects.append(Cursor);



    #------------------------------------------------------------------
    #UPDATE
    #------------------------------------------------------------------

    while 1:
        deltaTime = time.time() - pastTime
        pastTime = time.time()

        #checkingInputs
        MouseInputs[1] = [0, 0, 0]
        RechargeInput[1] = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    RechargeInput[0] += 1;
                    RechargeInput[1] = 1;

                if event.key == pygame.K_w:
                    UpDownInput[0] += 1
                    UpDownInput[1] = 1
                if event.key == pygame.K_s:
                    UpDownInput[0] -= 1
                    UpDownInput[1] = 1
                if event.key == pygame.K_a:
                    LeftRightInput[0] -= 1
                    LeftRightInput[1] = 1
                if event.key == pygame.K_d:
                    LeftRightInput[0] += 1
                    LeftRightInput[1] = 1
                if event.key == pygame.K_ESCAPE:
                    #if player wants to leave then just leave
                    sys.exit()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_r:
                    RechargeInput[0] -= 1;
                    RechargeInput[1] = -1;

                if event.key == pygame.K_w:
                    UpDownInput[0] -= 1
                    UpDownInput[1] = -1
                if event.key == pygame.K_s:
                    UpDownInput[0] += 1
                    UpDownInput[1] = -1
                if event.key == pygame.K_a:
                    LeftRightInput[0] += 1
                    LeftRightInput[1] = -1
                if event.key == pygame.K_d:
                    LeftRightInput[0] -= 1
                    LeftRightInput[1] = -1

            if event.type == pygame.MOUSEBUTTONDOWN:
                MouseInputs[1] = pygame.mouse.get_pressed()
                MouseInputs[1] = [int(MouseInputs[1][0]), int(MouseInputs[1][1]), int(MouseInputs[1][2])]
                MouseInputs[0] = [MouseInputs[0][0] + MouseInputs[1][0], MouseInputs[0][1] + MouseInputs[1][1], MouseInputs[0][2] + MouseInputs[1][2]]
            if event.type == pygame.MOUSEBUTTONUP: #apparently pygame do not sends inputs when mouse is button up, only informs that it is at all
                MouseInputs[1] = [-MouseInputs[0][0], -MouseInputs[0][1], -MouseInputs[0][2]]
                MouseInputs[0] = [MouseInputs[0][0] + MouseInputs[1][0], MouseInputs[0][1] + MouseInputs[1][1], MouseInputs[0][2] + MouseInputs[1][2]]


        Cursor.transform.lpos = GetWorldMousePos(size, Player.transform.lpos)
        Cursor.transform.Desynch()

        #Player movement
        Player.transform.FaceTowards(Cursor.transform);


        #Global rendering
        screen.fill(background)
        #afferting position for camera pourposes:
        CameraPivot = Player.transform.lpos

        for Object in GlobalObjects:
            for Model in Object.GetComps('Model'):
                Model.Render(screen, size, CameraPivot)
            for Primitive in Object.GetComps('Primitive'):
                Primitive.Render(screen, size, CameraPivot)

        pygame.display.flip();

if __name__ == '__main__':
    main()
    pygame.quit()
    sys.exit()

'''
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
'''