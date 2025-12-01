#python ligraries
import pygame
import time
import random, math, sys
#game libraries
from transforms import *
import game_object
import rendering
import collisions
import physics
import enums

import enemies

pygame.init()

clock = pygame.time.Clock()
FPS = 60

#already at start create camera as global object
CameraObject = game_object.GameObject(Transform(Vector([800 / 2, 600 / 2]), 0, Vector([1, 1])), [], None)
CameraObject.AddComp(rendering.Camera([800, 600], (255, 255, 255), "Zombie Survival Killer Mega Bestseller 3000"))
MainCamera = CameraObject.GetComp('Camera')

def GetFixedMousePos(windowSize):
    pygamePos = pygame.mouse.get_pos()
    return Vector([pygamePos[0], windowSize[1] - pygamePos[1]])

def GetWorldMousePos(windowSize, cameraPivot):
    pygamePos = pygame.mouse.get_pos()
    return Vector([pygamePos[0] + cameraPivot.x() - windowSize[0] / 2, windowSize[1] - pygamePos[1] + cameraPivot.y() - windowSize[1] / 2])

def main():
    #------------------------------------------------------------------
    #START
    #------------------------------------------------------------------

    #For now vector testing
    '''
    vectTest = Vector([0, 1])
    #vectTest += Vector([2, 2])
    #vectTest /= 2
    print(RadiansToDegrees(Vector([0, 1]).ToRotation()))
    vectTest.Rotate(Vector([1, 1]).ToRotation());
    #vectTest.x = 2
    print(vectTest.data)
    print(Vector.RotToVect(DegToRad(90)).data)


    return;
    '''
    transTest = Transform(Vector([0, 0]), DegToRad(0), Vector([1, 1]))
    print(transTest.GlobalToLocal(Vector([1, 0]), True).data)

    #vectTest = Vector([1, 1])
    #print(Vector.Proj(vectTest, Vector([0, 1])).data)

    size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
    background = (255, 255, 255)

    deltaTime = time.time()
    pastTime = time.time()

    #Input declaration
    UpDownInput = [0, 0]
    LeftRightInput = [0, 0] 
    RechargeInput = [0, 0] #determines if the player wants to recharge manually
    MouseInputs = [[0, 0, 0], [0, 0, 0]]

    #----------------------------------------
    #Game objects containers
    #----------------------------------------
    GlobalObjects = []
    Obstacles = [] #game objects
    Borders = [] #game objects
    Enemies = [] #physic object

    #create player object
    Player = game_object.GameObject(Transform(Vector(MainCamera.windowSize) / 2, 0, Vector([15, 15])), [], None)
    Player.AddComp(rendering.Model('Assets\Triangle.obj', [0, 0, 255], enums.RenderMode.POLYGON));
    Player.AddComp(collisions.Collider(enums.ColliderType.SPHERE))
    Player.AddComp(physics.PhysicObject(1))
    PlayerRaycast = game_object.GameObject(Transform(Vector([1, 0]), 0, Vector([1, 1])), [], None)
    PlayerRaycast.SetParent(Player)
    #Player.GetComp('PhysicObject').restitution = 1

    GlobalObjects.append(Player);

    #create cursor object
    Cursor = game_object.GameObject(Transform(Vector(MainCamera.windowSize) / 2, 0, Vector([15, 15])), [], None)
    #Cursor = game_object.GameObject(transforms.Transform([size[0] / 2, size[1] / 2], 0, [15, 15]), [], None)
    Cursor.AddComp(rendering.Model('Assets\Cursor.obj', [255, 0, 0], enums.RenderMode.WIREFRAME))
    #Cursor.AddComp(physics.Collider(0, [1, 1]))
    GlobalObjects.append(Cursor);


    #WORLD BORDER
    MainBorder = game_object.GameObject(Transform(Vector(MainCamera.windowSize) / 2, 0, Vector([MainCamera.windowSize[0], MainCamera.windowSize[1]])), [], None)
    Border1 = game_object.GameObject(Transform(Vector([0.5, 0]), DegToRad(180), Vector([0.1, 0.1])), [], MainBorder)
    Border1.AddComp(collisions.Collider(enums.ColliderType.LINE))
    Border2 = game_object.GameObject(Transform(Vector([0, 0.5]), DegToRad(270), Vector([1, 1])), [], MainBorder)
    Border2.AddComp(collisions.Collider(enums.ColliderType.LINE))
    Border3 = game_object.GameObject(Transform(Vector([-0.5, 0]), 0, Vector([1, 1])), [], MainBorder)
    Border3.AddComp(collisions.Collider(enums.ColliderType.LINE))
    Border4 = game_object.GameObject(Transform(Vector([0, -0.5]), DegToRad(90), Vector([1, 1])), [], MainBorder)
    Border4.AddComp(collisions.Collider(enums.ColliderType.LINE))

    GlobalObjects.append(MainBorder)
    GlobalObjects.append(Border1)
    GlobalObjects.append(Border2)
    GlobalObjects.append(Border3)
    GlobalObjects.append(Border4)

    Borders.append(Border1)
    Borders.append(Border2)
    Borders.append(Border3)
    Borders.append(Border4)
    #Obstacles.append(Border1)
    #Obstacles.append(Border2)
    #Obstacles.append(Border3)
    #Obstacles.append(Border4)

    #enviromental obstacles creation
    for _ in range(10):
        borderDist = 50
        obstacleSize = random.randint(10, 50)
        CurObstacle = game_object.GameObject(Transform(Vector([random.randint(borderDist, MainCamera.windowSize[0] - borderDist), random.randint(borderDist, MainCamera.windowSize[1] - borderDist)]), 0, Vector([obstacleSize, obstacleSize])), [], None)
        CurObstacle.AddComp(collisions.Collider(enums.ColliderType.SPHERE))
        CurObstacle.AddComp(rendering.Primitive(enums.PrimitiveType.CIRCLE, (0, 255, 0), 0))
        GlobalObjects.append(CurObstacle)
        Obstacles.append(CurObstacle)

    #enemies spawn
    Enemies = []
    for _ in range(1):
        borderDist = 10
        enemyPosition = Vector([random.randint(borderDist, MainCamera.windowSize[0] - borderDist), random.randint(borderDist, MainCamera.windowSize[0] - borderDist)])
        CurEnemy = game_object.GameObject(Transform(enemyPosition, 0, Vector([15, 15])), [], None)
        CurEnemy.AddComp(rendering.Primitive(enums.PrimitiveType.CIRCLE, (255, 0, 0), 0))
        #CurEnemy.AddComp(rendering.Model('Assets\Triangle.obj', [255, 0, 0], enums.RenderMode.POLYGON));
        CurEnemy.AddComp(collisions.Collider(enums.ColliderType.SPHERE))
        CurEnemy.AddComp(physics.PhysicObject(1))
        CurEnemy.AddComp(enemies.Enemy())

        #ENEMY AI AND PHYSICS SETUP
        CurEnemy.GetComp('PhysicObject').maxForce = 2;
        CurEnemyAI = CurEnemy.GetComp('Enemy')
        #Wander
        CurEnemyAI.wanderDistance = 48
        CurEnemyAI.wanderRadius = 8
        CurEnemyAI.wanderJitter = 4
        #ObstacleAvoidance
        CurEnemyAI.breakMultiplier = 2
        CurEnemyAI.wallDetectionRange = CurEnemy.transform.lscale.MaxComponent() * 3

        #debug on / off
        #CurEnemyAI.debugFlag = enums.DebugFlag.WANDER | enums.DebugFlag.OBSTACLE | enums.DebugFlag.WALL
        CurEnemyAI.debugFlag = enums.DebugFlag.HIDE | enums.DebugFlag.ARRIVE

        CurEnemy.GetComp('PhysicObject').vel = Vector([1, 1])
        #values references setup
        CurEnemyAI.Start(Player.transform, Player.GetComp('PhysicObject'), MainCamera)
        Enemies.append(CurEnemy)
        GlobalObjects.append(CurEnemy)

    #------------------------------------------------------------------
    #UPDATE
    #------------------------------------------------------------------

    while 1:
        clock.tick(FPS)

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


        Cursor.transform.lpos = GetWorldMousePos(MainCamera.windowSize, MainCamera.gameObject.transform.lpos)
        Cursor.transform.Desynch()

        #-----------------------------------------------
        #Player handling
        #-----------------------------------------------
        Player.transform.FaceTowards(Cursor.transform);
        #LATER MOVE PLAYER SPEED TO SOME SPECIAL CLASS
        moveVector = Vector([LeftRightInput[0], UpDownInput[0]])
        playerSpeed = 0.2
        Player.GetComp('PhysicObject').maxVelocity = 0.2
        Player.GetComp('PhysicObject').vel += moveVector * playerSpeed

        #debug version of raycast
        PlayerRaycast.transform.SynchGlobals()
        #print(PlayerRaycast.transform.isSynch)
        raycastObject, raycastPoint = collisions.Raycast.CastRay(PlayerRaycast.transform, GlobalObjects)

        #killing enemies
        #print(raycastObject.GetComp('Enemy'))
        if raycastObject and raycastObject.GetComp('Enemy'):
            pass
            #Enemies.remove(raycastObject)
            #GlobalObjects.remove(raycastObject)
            #del raycastObject

        #-----------------------------------------------
        #Physics update
        #-----------------------------------------------


        #-----------------------------------------------
        #Collision handling
        #-----------------------------------------------


        #get all physic components in game: (as collision reaction happens only for them)
        PhysicComponents = []
        for i in range(0, len(GlobalObjects)):
            iPhys = GlobalObjects[i].GetComp('PhysicObject')
            if iPhys:
                PhysicComponents.append(iPhys)

        #for every physic object, find colliders in all objects
        for i in range(0, len(PhysicComponents)):
            for j in range(i, len(GlobalObjects)):
                #check for every collider in object
                for OtherCollider in GlobalObjects[j].GetComps('Collider'):

                    #for PhysCollider in PhysicComponents[i].GetCompsInChilds('Collider'):

                    #check if not self colliding
                    #if OtherCollider.gameObject.GetObjsInParents('PhysicObject') == PhysicComponents[i].gameObject:
                        #continue

                    PhysCollider = PhysicComponents[i].gameObject.GetComp('Collider')
                    if PhysCollider:
                        PhysCollider.ResolveCollision(OtherCollider)
               

        #-----------------------------------------------
        #Global rendering
        #-----------------------------------------------
        MainCamera.Clear()
        
        PlayerRaycast.transform.SynchGlobals()
        #Player.transform.SynchGlobals()
        #print(PlayerRaycast.transform.pos.data)
        MainCamera.RenderRawLine(PlayerRaycast.transform.pos, raycastPoint, (255, 0, 0), 1)


        for Object in GlobalObjects:
            for Model in Object.GetComps('Model'):
                MainCamera.RenderWireframe(Model)
            for Primitive in Object.GetComps('Primitive'):
                MainCamera.RenderPrimitive(Primitive)

        #ENEMIES DEBUG!!!
        for Object in Enemies:
            EnemyAI = Object.GetComp('Enemy')
            EnemyAI.Debug()
            #print(EnemyAI.phys.vel.data)

        #-----------------------------------------------
        #Physics execution
        #-----------------------------------------------
        Player.GetComp('PhysicObject').ExecutePos()

        #enemy logic
        for Object in Enemies:
            for Enemy in Object.GetComps('Enemy'):
                pass

                #update enemy AI sequentially
                #Enemy.ObstacleAvoidance(Obstacles)
                #Enemy.WallAvoidance(Borders)
                Enemy.Hide(Obstacles)
                #Enemy.Wander()
            for Phys in Object.GetComps('PhysicObject'):
                Phys.UpdateVelocity()
                #first rotate the enemy towards it's velocity
                Enemy.UpdateForwardDirection()
                Phys.ExecutePos()


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