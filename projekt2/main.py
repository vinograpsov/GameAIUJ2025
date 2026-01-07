#python libraries
import pygame
import time
import random, math, sys
#game libraries
import singletons
from transforms import *
import game_object
import rendering
import collisions
import physics
import enums

import weapons
import bots

pygame.init()

clock = pygame.time.Clock()
FPS = 60

#already at start create camera as global object
CameraObject = game_object.GameObject(Transform(Vector([800 / 2, 600 / 2]), 0, Vector([1, 1])), [], None)
CameraObject.AddComp(rendering.Camera([800, 600], (255, 255, 255), "Stable Cobra Deathmatch Mega Bestseller 6000"))
singletons.MainCamera = CameraObject.GetComp(rendering.Camera)

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
    GlobalObjects = [] #game objects
    Obstacles = [] #game objects
    Borders = [] #game objects
    Bots = [] #game objects with physic object + BotAI

    #PLAYER IS SIMPLY BOT THAT CAN BE CONTROLLED BY OUTSIDE INPUT AND HAS NON FUNCTIONING AI
    Player = game_object.GameObject(Transform(Vector(singletons.MainCamera.windowSize) / 2, 0, Vector([15, 15])), [], None)
    Player.AddComp(rendering.Primitive(enums.PrimitiveType.SPHERE, [0, 0, 255], 0))
    #Player.AddComp(rendering.Model('Assets\Triangle.obj', [0, 0, 255], enums.RenderMode.POLYGON));
    Player.AddComp(collisions.Collider(enums.ColliderType.SPHERE))
    Player.AddComp(physics.PhysicObject(1))
    Player.AddComp(bots.Bot()) #player is still considered a bot
    #TO DO
    #REPLACE PLAYER RAYCAST WITH RAILGUN WEAPON
    PlayerWeapon = game_object.GameObject(Transform(Vector([1, 0]), 0, Vector([1, 1])), [], None)
    PlayerWeapon.AddComp(weapons.Railgun(Player, 0, 4096, 100)) #for debug weapon has no cooldown and nearly infinite ammo
    PlayerWeapon.SetParent(Player)

    PlayerWeapon.GetComp(weapons.Weapon).debugFlag = enums.WeaponDebug.LINEPOINTER

    GlobalObjects.append(Player);

    #create cursor object
    Cursor = game_object.GameObject(Transform(Vector(singletons.MainCamera.windowSize) / 2, 0, Vector([15, 15])), [], None)
    Cursor.AddComp(rendering.Model('Assets\Cursor.obj', [255, 0, 0], enums.RenderMode.WIREFRAME))
    GlobalObjects.append(Cursor);


    #WORLD BORDER
    #TO DO: REPLACE WORLD BORDER WITH POLYGON COLLIDER (OR MAP)
    MainBorder = game_object.GameObject(Transform(Vector(singletons.MainCamera.windowSize) / 2, 0, Vector([singletons.MainCamera.windowSize[0], singletons.MainCamera.windowSize[1]])), [], None)
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

    #enviromental obstacles creation
    #TO DO
    #replace it by map creation
    Map = game_object.GameObject(Transform(Vector(singletons.MainCamera.windowSize) / 2, 0, Vector([singletons.MainCamera.windowSize[0] / 2, singletons.MainCamera.windowSize[1] / 2])), [], None)
    Map.AddComp(rendering.Model('Assets\Map.obj', [64, 64, 64], enums.RenderMode.WIREFRAME));
    Map.AddComp(collisions.PolygonCollider(enums.ColliderType.POLYGON, 'Assets/Map.obj'))
    GlobalObjects.append(Map)

    #TO DO
    #bots spawns
    #bots spawns in set positions (not random)
    #btw we may randomize for now it for better testing
    for _ in range(0):
        borderDist = 10
        botPosition = Vector([random.randint(borderDist, singletons.MainCamera.windowSize[0] - borderDist), random.randint(borderDist, singletons.MainCamera.windowSize[0] - borderDist)])
        CurBot = game_object.GameObject(Transform(botPosition, 0, Vector([15, 15])), [], None)
        CurBot.AddComp(rendering.Primitive(enums.PrimitiveType.CIRCLE, (255, 0, 0), 0))
        #CurBot.AddComp(rendering.Model('Assets\Triangle.obj', [255, 0, 0], enums.RenderMode.POLYGON));
        CurBot.AddComp(collisions.Collider(enums.ColliderType.SPHERE))
        CurBot.AddComp(physics.PhysicObject(1)) #?
        CurBot.AddComp(Bot())

        #BOT AI SETUP
        CurBotAI = CurBot.GetComp('Bot')
        #(...)

        #debug on / off
        CurBotAI.debugFlag = enums.BotDebug.DIRECTION

        #values references setup
        Bots.append(CurBot)
        GlobalObjects.append(CurBot)
    
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


        Cursor.transform.lpos = GetWorldMousePos(singletons.MainCamera.windowSize, singletons.MainCamera.gameObject.transform.lpos)
        Cursor.transform.Desynch()

        #-----------------------------------------------
        #Player handling
        #-----------------------------------------------
        if Player != None: #we can have no player
            Player.transform.FaceTowards(Cursor.transform);
            #LATER MOVE PLAYER SPEED TO SOME SPECIAL CLASS
            moveVector = Vector([LeftRightInput[0], UpDownInput[0]])
            playerSpeed = 0.2
            Player.GetComp(physics.PhysicObject).maxVelocity = 0.2
            Player.GetComp(physics.PhysicObject).vel += moveVector * playerSpeed

        #-----------------------------------------------
        #Special Events
        #-----------------------------------------------

        #TO DO
        #replace to use weapon system, or make it so that weapon kills
        #killing enemies
        #print(raycastObject.GetComp('Enemy'))
        #if raycastObject and raycastObject.GetComp('Enemy'):
            #pass
            #Enemies.remove(raycastObject)
            #GlobalObjects.remove(raycastObject)
            #del raycastObject

        #-----------------------------------------------
        #Global rendering
        #-----------------------------------------------
        singletons.MainCamera.Clear()
        
        PlayerWeapon.transform.SynchGlobals()

        #test raycast collision by player weapon
        if enums.WeaponDebug.LINEPOINTER in PlayerWeapon.GetComp(weapons.Railgun).debugFlag:
            PlayerWeapon.GetComp(weapons.Railgun).ShowLinePointer([Map], [])


        for Object in GlobalObjects:
            for Model in Object.GetComps(rendering.Model):
                singletons.MainCamera.RenderWireframe(Model)
            for Primitive in Object.GetComps(rendering.Primitive):
                singletons.MainCamera.RenderPrimitive(Primitive)

        #ENEMIES DEBUG!!!
        for Object in Bots:
            BotAI = Object.GetComp(bots.Bot)
            BotAI.Debug()

        #-----------------------------------------------
        #Collision handling
        #-----------------------------------------------

        #now for testing collision with map
        '''
        if collisions.CollisionSolver.CheckCollision(Player.GetComp(collisions.Collider), Map.GetComp(collisions.Collider)):
            Player.GetComp(rendering.RenderObject).col = [0, 255, 0]
        else:
            Player.GetComp(rendering.RenderObject).col = [255, 0, 0]
        '''

        #if player keeps mouse button down he tries to shoot
        if MouseInputs[0][0] > 0:
            PlayerWeapon.GetComp(weapons.Weapon).TryShoot([Map], [])

        #get all physic components in game: (as collision reaction happens only for them)
        PhysicComponents = []
        for i in range(0, len(GlobalObjects)):
            iPhys = GlobalObjects[i].GetComp(physics.PhysicObject)
            if iPhys:
                PhysicComponents.append(iPhys)

        #for every physic object, find colliders in all objects
        for i in range(0, len(PhysicComponents)):
            for j in range(0, len(GlobalObjects)):
                #check for every collider in object
                for OtherCollider in GlobalObjects[j].GetComps(collisions.Collider):

                    PhysCollider = PhysicComponents[i].gameObject.GetComp(collisions.Collider)
                    #UNUSED, we no longer need to resolve any collisions
                    #if PhysCollider:
                    #    PhysCollider.ResolveCollision(OtherCollider)

        #-----------------------------------------------
        #Physics execution
        #-----------------------------------------------

        Player.GetComp(physics.PhysicObject).ExecutePos()
        Player.transform.SynchGlobals()

        #-----------------------------------------------
        #AI logic
        #-----------------------------------------------

        #singular bot
        for Object in Bots:
            for Bot in Object.GetComps(bots.Bot):
                pass
            
            #physics execution for bots
            for Phys in Object.GetComps(physics.PhysicObject):
                Phys.UpdateVelocity()
                #first rotate the bot towards it's velocity
                Bot.UpdateForwardDirection()
                Phys.ExecutePos()


        pygame.display.flip();


if __name__ == '__main__':
    main()
    pygame.quit()
    sys.exit()