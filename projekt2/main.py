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
import navigation

import weapons
import bots
import pickup

pygame.init()
clock = pygame.time.Clock()
FPS = 60

#already at start create camera as global object
CameraObject = game_object.GameObject(Transform(Vector([800 / 2, 600 / 2]), 0, Vector([1, 1])), [], None)
CameraObject.AddComp(rendering.Camera([800, 600], (92, 92, 92), "Stable Cobra Deathmatch Mega Bestseller 6000"))
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

    GeneralDebugFlag = enums.GeneralDebug.SPAWNPLAYER | enums.GeneralDebug.SPAWNDUMMY


    #------------------------MAP AND BORDERS ----------------------------
    Map = game_object.GameObject(Transform(Vector(singletons.MainCamera.windowSize) / 2, 0, Vector([singletons.MainCamera.windowSize[0] / 2, singletons.MainCamera.windowSize[1] / 2])), [], None)
    Map.AddComp(rendering.Model('Assets\Map.obj', [192, 192, 192], enums.RenderMode.WIREFRAME));
    Map.AddComp(collisions.PolygonCollider(enums.ColliderType.POLYGON, 'Assets/Map.obj'))
    singletons.MapObjects.append(Map)

    #TO DO: REPLACE WORLD BORDER WITH POLYGON COLLIDER (OR MAP)
    # MainBorder = game_object.GameObject(Transform(Vector(singletons.MainCamera.windowSize) / 2, 0, Vector([singletons.MainCamera.windowSize[0], singletons.MainCamera.windowSize[1]])), [], None)
    # Border1 = game_object.GameObject(Transform(Vector([0.5, 0]), DegToRad(180), Vector([0.1, 0.1])), [], MainBorder)
    # Border1.AddComp(collisions.Collider(enums.ColliderType.LINE))
    # Border2 = game_object.GameObject(Transform(Vector([0, 0.5]), DegToRad(270), Vector([1, 1])), [], MainBorder)
    # Border2.AddComp(collisions.Collider(enums.ColliderType.LINE))
    # Border3 = game_object.GameObject(Transform(Vector([-0.5, 0]), 0, Vector([1, 1])), [], MainBorder)
    # Border3.AddComp(collisions.Collider(enums.ColliderType.LINE))
    # Border4 = game_object.GameObject(Transform(Vector([0, -0.5]), DegToRad(90), Vector([1, 1])), [], MainBorder)
    # Border4.AddComp(collisions.Collider(enums.ColliderType.LINE))

    # GlobalObjects.append(MainBorder)
    # GlobalObjects.append(Border1)
    # GlobalObjects.append(Border2)
    # GlobalObjects.append(Border3)
    # GlobalObjects.append(Border4)

    # Borders.append(Border1)
    # Borders.append(Border2)
    # Borders.append(Border3)
    # Borders.append(Border4)

    #------------------------MAP AND BORDERS ----------------------------



    # ------------------------PLAYER SETUP ----------------------------
    Player = game_object.GameObject(Transform(Vector(singletons.MainCamera.windowSize) / 2, 0, Vector([15, 15])), [], None)
    Player.AddComp(rendering.Primitive(enums.PrimitiveType.SPHERE, [0, 0, 255], 0))
    Player.AddComp(collisions.Collider(enums.ColliderType.SPHERE))
    
    Player.AddComp(physics.PhysicObject(1))
    Player.AddComp(bots.Bot(3, 100, math.pi)) #player is still considered a bot
    singletons.Bots.append(Player)
    
    Player.GetComp(bots.Bot).debugFlag = enums.BotDebug.FIELDOFVIEW

    PlayerWeapon = game_object.GameObject(Transform(Vector([1, 0]), 0, Vector([1, 1])), [], None)
    PlayerWeapon.AddComp(weapons.Railgun(Player, 0.1, 4096, 100, 60, 0)) #for debug weapon has no cooldown and nearly infinite ammo
    PlayerWeapon.SetParent(Player)

    PlayerWeapon.GetComp(weapons.Weapon).debugFlag = enums.WeaponDebug.LINEPOINTER | enums.WeaponDebug.FIRESOUND
    singletons.GlobalObjects.append(Player);

    Cursor = game_object.GameObject(Transform(Vector(singletons.MainCamera.windowSize) / 2, 0, Vector([15, 15])), [], None)
    Cursor.AddComp(rendering.Model('Assets\Cursor.obj', [255, 0, 0], enums.RenderMode.WIREFRAME))
    singletons.GlobalObjects.append(Cursor);
    # ------------------------PLAYER SETUP ----------------------------



    #--------------------------BOTS SETUP -----------------------------
    for _ in range(1):
        botPosition = Vector([150, 150])
        CurBot = game_object.GameObject(Transform(botPosition, 0, Vector([15, 15])), [], None)
        CurBot.AddComp(rendering.Primitive(enums.PrimitiveType.CIRCLE, (255, 0, 0), 0))
        CurBot.AddComp(collisions.Collider(enums.ColliderType.SPHERE))
        CurBot.AddComp(physics.PhysicObject(1))
        
        bot_ai = bots.Bot(3, 100, math.pi)
        bot_ai.debugFlag = enums.BotDebug.DIRECTION | enums.BotDebug.PATH
        
        CurBot.AddComp(bot_ai)
        singletons.Bots.append(CurBot)
        singletons.GlobalObjects.append(CurBot)
    #--------------------------BOTS SETUP -----------------------------
    
    #--------------------------------------- 
    #DUMMY
    #---------------------------------------

    Dummy = None
    if enums.GeneralDebug.SPAWNDUMMY in GeneralDebugFlag:
        Dummy = game_object.GameObject(Transform(Vector([singletons.MainCamera.windowSize[0] / 2, singletons.MainCamera.windowSize[1] / 2 - 20]), 0, Vector([15, 15])), [], None)
        Dummy.AddComp(rendering.Primitive(enums.PrimitiveType.SPHERE, [0, 0, 255], 0))
        Dummy.AddComp(collisions.Collider(enums.ColliderType.SPHERE))
        Dummy.AddComp(physics.PhysicObject(1))
        Dummy.AddComp(bots.Bot(3, 100, math.pi))
        #dummy should later also hold a weapon
        singletons.Bots.append(Dummy)

        Dummy.GetComp(bots.Bot).debugFlag = enums.BotDebug.VISION | enums.BotDebug.MEMORYPOSITIONS


    #--------------------------------------- 
    #DUMMY
    #---------------------------------------

    #------------------------------------------------------------------
    #FLOODFILL and ASTAR
    #------------------------------------------------------------------

    # allObstacles = Obstacles + Borders + [Map]
    allObstacles = [Map]
    NavGraph = navigation.NavigationGraph(30, 15)
    start_point = Vector([100, 100])
    NavGraph.generateFloodFill(start_point, allObstacles)

    #------------------------------------------------------------------
    #FLOODFILL and ASTAR
    #------------------------------------------------------------------



    #-----------------------------------------------
    # PICKUPS SETUP
    #-----------------------------------------------

    Pickups = []

    HealthObj = game_object.GameObject(Transform(Vector([600, 400]), 0, Vector([10, 10])), [], None)
    HealthObj.AddComp(rendering.Primitive(enums.PrimitiveType.CIRCLE, (0, 255, 0), 0))
    p_comp = pickup.Pickup(pickup.PickupType.HEALTH, 25, 10.0)
    p_comp.gameObject = HealthObj
    HealthObj.AddComp(p_comp)
    Pickups.append(HealthObj)
    singletons.GlobalObjects.append(HealthObj)

    AmmoObj = game_object.GameObject(Transform(Vector([200, 500]), 0, Vector([10, 10])), [], None)
    AmmoObj.AddComp(rendering.Primitive(enums.PrimitiveType.CIRCLE, (255, 0, 0), 0))
    p_comp_ammp = pickup.Pickup(pickup.PickupType.AMMO_ROCKET, 10)
    p_comp_ammp.gameObject = AmmoObj
    AmmoObj.AddComp(p_comp_ammp)
    Pickups.append(AmmoObj)
    singletons.GlobalObjects.append(AmmoObj)

    for p_obj in Pickups:
        NavGraph.register_pickup(p_obj)

    #-----------------------------------------------
    # PICKUPS SETUP
    #-----------------------------------------------


    MyPathFinder = navigation.Pathfinder(NavGraph)
    
    while 1:
        
        clock.tick(FPS)
        now = time.time()
        pastTime = now 
        deltaTime = now - pastTime

        
        #-----------------------------------------------
        # INPUT HANDLING
        #-----------------------------------------------
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
                    sys.exit()
                if event.key == pygame.K_F1:
                    NavGraph.toggle_debug()
                if event.key == pygame.K_F2:
                    for obj in singletons.Bots:
                        bot = obj.GetComp(bots.Bot)
                        bot.toggle_debug_path()


                # TMP TEST BOT GO TO PICKUP
                if event.key == pygame.K_e:
                    if len(singletons.Bots) > 0:
                        bot_obj = singletons.Bots[0]
                        bot_ai = bot_obj.GetComp(bots.Bot)

                        path = MyPathFinder.create_path_to_pickup(bot_obj.transform.pos, pickup.PickupType.AMMO_ROCKET)
                        if path: bot_ai.set_path(path)
                        else: print("No path to pickup found")


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
                
                if event.button == 3:
                    target_pos = Cursor.transform.pos
                    if len(singletons.Bots) > 0:
                        bot = singletons.Bots[0].GetComp(bots.Bot)
                        start_pos = singletons.Bots[0].transform.pos
                        path_vectors = MyPathFinder.create_path_to_position(start_pos, target_pos)
                        if path_vectors:
                            bot.set_path(path_vectors)
                        else:
                            print("No path found")
            
            if event.type == pygame.MOUSEBUTTONUP: #apparently pygame do not sends inputs when mouse is button up, only informs that it is at all
                MouseInputs[1] = [-MouseInputs[0][0], -MouseInputs[0][1], -MouseInputs[0][2]]
                MouseInputs[0] = [MouseInputs[0][0] + MouseInputs[1][0], MouseInputs[0][1] + MouseInputs[1][1], MouseInputs[0][2] + MouseInputs[1][2]]
                
        #-----------------------------------------------
        # INPUT HANDLING
        #-----------------------------------------------


        Cursor.transform.lpos = GetWorldMousePos(singletons.MainCamera.windowSize, singletons.MainCamera.gameObject.transform.lpos)
        Cursor.transform.Desynch()

        #-----------------------------------------------
        #Player handling
        #-----------------------------------------------
        if Player != None: 
            Player.transform.FaceTowards(Cursor.transform);
            moveVector = Vector([LeftRightInput[0], UpDownInput[0]])
            playerSpeed = 0.2
            Player.GetComp(physics.PhysicObject).vel += moveVector * playerSpeed



        #-----------------------------------------------
        #Bots handling
        #-----------------------------------------------

        #singular bot
        for obj in singletons.Bots:

            BotComp = obj.GetComp(bots.Bot)
            if BotComp: BotComp.update()

            physComp = obj.GetComp(physics.PhysicObject)
            if physComp: physComp.ExecutePos()

            obj.transform.SynchGlobals()

        #-----------------------------------------------
        #Global rendering
        #-----------------------------------------------
        singletons.MainCamera.Clear()
        PlayerWeapon.transform.SynchGlobals()

        for Object in singletons.GlobalObjects:
            for Model in Object.GetComps(rendering.Model):
                singletons.MainCamera.RenderWireframe(Model)
            for Primitive in Object.GetComps(rendering.Primitive):
                singletons.MainCamera.RenderPrimitive(Primitive)

        NavGraph.debugDraw(singletons.MainCamera)

        for obj in singletons.Bots:
            bot = obj.GetComp(bots.Bot)
            bot.Debug(singletons.MainCamera)

        if enums.WeaponDebug.LINEPOINTER in PlayerWeapon.GetComp(weapons.Railgun).debugFlag:
            PlayerWeapon.GetComp(weapons.Railgun).ShowLinePointer([Map], [])

        
        for Renderer in singletons.RenderObjects:
            singletons.MainCamera.Render(Renderer)

        #-----------------------------------------------
        #Collision handling
        #-----------------------------------------------

        #if player keeps mouse button down he tries to shoot
        if MouseInputs[0][0] > 0:
            PlayerWeapon.GetComp(weapons.Weapon).TryShoot([Map], [])

        #get all physic components in game: (as collision reaction happens only for them)
        PhysicComponents = []
        for i in range(0, len(singletons.GlobalObjects)):
            iPhys = singletons.GlobalObjects[i].GetComp(physics.PhysicObject)
            if iPhys:
                PhysicComponents.append(iPhys)

        #for every physic object, find colliders in all objects
        for i in range(0, len(PhysicComponents)):
            for j in range(0, len(singletons.GlobalObjects)):
                #check for every collider in object
                for OtherCollider in singletons.GlobalObjects[j].GetComps(collisions.Collider):

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

        for object in singletons.Bots:
            botAI = object.GetComp(bots.Bot)

            #TO DO
            #reduce number of vision calls like in the book
            #vision
            botAI.UpdateVision(singletons.Bots, singletons.MapObjects)
            #hearing
            botAI.UpdateHearing(singletons.Sounds, singletons.MapObjects)

            #dummy does not act, but can still be a receiver and can use it's perception
            if object == Dummy:
                continue

        #singular bot
        for Object in singletons.Bots:
            
            #physics execution for bots
            for Phys in Object.GetComps(physics.PhysicObject):
                Phys.UpdateVelocity()
                #first rotate the bot towards it's velocity
                #Bot.UpdateForwardDirection() #part of old project, could this still be important?
                Phys.ExecutePos()


        #-----------------------------------------------
        #Timets Update
        #-----------------------------------------------

        for Timer in singletons.Timers:
            Timer.UpdateTimer()

        pygame.display.flip();


if __name__ == '__main__':
    main()
    pygame.quit()
    sys.exit()