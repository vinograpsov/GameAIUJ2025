import pygame
import time
import random, math, sys 
import transforms
import collisions
import rendering
import combat
import items
import physics
import objects_structure

#print

pygame.init()
pygame.mixer.init()

pygame.display.set_caption("The lost theorem")

def getRandCol():
    return [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]

def GetRandomItem(ItemPool):
    return ItemPool[random.randint(0, len(ItemPool) - 1)]

#here comes types of enemies
def GetDesignedAI(ID):
    #reminder about enemy stats:
    #rangePrec, accPrec, rechargePrec, haltPrec, distPrec
    if ID == 0: #obstacle, does absolutely nothing
        return combat.Enemy(100, 100, 0, 1, 100) #I just simply made him always wants to recharge
    elif ID == 1: #turret, generally not moving, but precise
        return combat.Enemy(1.2, 5, 1.2, 5, 3)
    elif ID == 2: #shade, slowly chases player, waiting for his return
        return combat.Enemy(0.8, 1, 2.5, 3, 1)
    elif ID == 3: #pursuit, rushes into player
        return combat.Enemy(1.6, 0.8, 1.5, 1, 0)
    elif ID == 4: #random, let's make it more chaotic!
        return combat.Enemy(0.8 + random.random() * 0.8, 0.8 + random.random() * 0.8, 1 + random.random() * 2, 1 + random.random() * 2, 0 + random.random() * 2)

    #for debugging pourposes if not found desired type return classic one
    return combat.Enemy(1, 1, 2, 1, 0.8) #classic, most balanced in bahaviour, yet not interesting


def GetFixedMousePos(windowSize):
    pygamePos = pygame.mouse.get_pos()
    return [pygamePos[0], windowSize[1] - pygamePos[1]]

def GetWorldMousePos(windowSize, cameraPiviot):
    pygamePos = pygame.mouse.get_pos()
    return [pygamePos[0] + cameraPiviot[0] - windowSize[0] / 2, windowSize[1] - pygamePos[1] + cameraPiviot[1] - windowSize[1] / 2]


#def SpawnEnemies(Enemies): #takes a list of game enemies as argument
def UpgradePrevab():
    upgrade = objects_structure.GameObject(transforms.Transform([0, 0], 0, [20, 20]), [], None)
    upgrade.AddComp(rendering.Model('Assets\Item(1).obj', [0, 196, 128]))
    upgrade.AddComp(physics.Collider(1, [1, 1]))
    upgrade.AddComp(items.Item('none Item', 'none desc', 'Assets\Item(1).obj')) #well it has to be having some
    #upgrade.childs.append(objects_structure.GameObject(transforms.Transform([0, 2], 0, [1, 1]), [], upgrade))
    #upgrade.childs.append(objects_structure.GameObject(transforms.Transform([0, 3], 0, [0.5, 0.5]), [], upgrade))
    objects_structure.GameObject(transforms.Transform([0, 2], 0, [1, 1]), [], None).SetParent(upgrade)
    objects_structure.GameObject(transforms.Transform([0, 3], 0, [0.8, 0.8]), [], None).SetParent(upgrade)
    #print(Upgrades[0].childs)
    upgrade.childs[0].AddComp(rendering.Text("anticross.ttf", 'none Item', [0, 196, 128]))
    upgrade.childs[1].AddComp(rendering.Text("anticross.ttf", 'none description', [0, 196, 128]))
    return upgrade

def AmmoPreset(pos, scale):
    ammo = objects_structure.GameObject(transforms.Transform(pos, 0, scale), [], None)
    ammo.AddComp(rendering.Model('Assets\JustSquare.obj', [196, 196, 196]))
    ammo.AddComp(rendering.Primitive(0, [128, 128, 128]))

def main():
    pygame.mixer.music.load("Assets\GlazingSun.mp3")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1)
    #size = [800, 600]
    #size = [1280, 1024]
    size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
    center = [size[0] / 2, size[1] / 2]
    border = [size[0] * 1.5, size[1] * 1.5]
    background = (255, 255, 255)
    #screen = pygame.display.set_mode(size)
    screen = pygame.display.set_mode((0, 0), pygame.DOUBLEBUF | pygame.FULLSCREEN, 16)
    pygame.mouse.set_visible(False)

    GlobalObjects = []
    #create player as a gameObject
    Player = objects_structure.GameObject(transforms.Transform([size[0] / 2, size[1] / 2], 0, [1, 1]), [], None)
    Player.AddComp(rendering.Model('Assets\Ship1.obj', [0, 0, 255]))
    Player.AddComp(physics.PhysicObject([0, 0], [0, 0], 1))
    Player.AddComp(physics.Collider(0, [1, 1]))
    Player.AddComp(combat.Ship(10, 15, 3, 5, 1))
    Player.GetComp('Ship').maxhp.multipliers.append(10)
    Player.GetComp('Ship').maxhp.PreupdateModifiers()
    #recalculate object scale based on size:
    Player.transform.lscale = transforms.ScaleVect(Player.transform.lscale, Player.GetComp('Ship').size.value)
    Player.transform.Desynch()

    #TestingDummy (enemy)
    #already unused, but left for testing purposes
    Dummy = objects_structure.GameObject(transforms.Transform([size[0] / 2, size[1] / 2 + size[1] / 4], 0, [1, 1]), [], None)
    Dummy.AddComp(rendering.Model('Assets\Ship1.obj', [255, 0, 0]))
    Dummy.AddComp(physics.PhysicObject([0, 0], [0, 0], 1))
    Dummy.AddComp(physics.Collider(0, [1, 1]))
    Dummy.AddComp(combat.Ship(100, 15, 3, 1, 0.5))
    #recalculate object scale based on size:
    Dummy.transform.lscale = transforms.ScaleVect(Dummy.transform.lscale, Dummy.GetComp('Ship').size.value)
    Dummy.transform.Desynch()
    Dummy.AddComp(combat.Enemy(1, 1, 2, 1, 1))

    DummyGun = objects_structure.GameObject(transforms.Transform([2, 0], 0, [2 / Dummy.transform.lscale[0], 2 / Dummy.transform.lscale[1]]), [], Dummy)
    #standard gun for dummy
    DummyGun.AddComp(combat.Gun([0, 128, 196], 10, 1, 6, 1, 3, 3, 0.1, 2, 1, 15))

    #get items from file:
    AllItems = items.LoadItems('Assets\items.txt')

    #for Item in AllItems:
        #print(Item.stats)
        #print(Item.name)
    #print(AllItems[random.randint(0, len(AllItems) - 1)].name)

    #create cursor object
    Cursor = objects_structure.GameObject(transforms.Transform([size[0] / 2, size[1] / 2], 0, [15, 15]), [], None)
    GlobalObjects.append(Cursor);
    Cursor.AddComp(rendering.Model('Assets\Cursor.obj', [255, 0, 0]))
    Cursor.AddComp(physics.Collider(0, [1, 1]))
    #gun atributes
    #__init__(self, acc, recoil, vel, size, dmg, range, delay, recharge, multishot, ammo):
    PlayerGun = objects_structure.GameObject(transforms.Transform([2, 0], 0, [2 / Player.transform.lscale[0], 2 / Player.transform.lscale[1]]), [], Player)
    #PlayerGun.AddComp(rendering.Primitive(2, [0, 255, 0])) #just for debugging, delete later
    PlayerGun.AddComp(combat.Gun([0, 128, 196], 10, 5, 6, 2, 2, 3, 5, 1, 1, 15))

    GlobalObjects.append(PlayerGun)

    UpDownInput = [0, 0]
    LeftRightInput = [0, 0] 
    RechargeInput = [0, 0] #determines if the player wants to recharge manually
    MouseInputs = [[0, 0, 0], [0, 0, 0]]

    #Global enemiesList
    Enemies = []

    #Pregenerating upgrades objects
    Upgrades = [UpgradePrevab(), UpgradePrevab(), UpgradePrevab()] #3 upgrades to choose from, just as for now
    Upgrades[0].transform.lpos = [0, border[1] / 4]
    Upgrades[1].transform.lpos = [0, border[1] / 2]
    Upgrades[2].transform.lpos = [0, border[1] * 3 / 4]
    Upgrades[0].transform.Desynch()
    Upgrades[1].transform.Desynch()
    Upgrades[2].transform.Desynch()

    #gameOverText
    GameOverScreen = objects_structure.GameObject(transforms.Transform([0, size[1] - size[1]/1.65], 0, [20, 30]), [], None)
    GameOverScreen.AddComp(rendering.Text("anticross.ttf", 'game over', [196, 64, 0]))

    #Interface
    UI = objects_structure.GameObject(transforms.Transform([-size[0] + size[0]/1.5, size[1] - size[1]/1.65], 0, [1, 1]), [], None)
    #hp bar
    objects_structure.GameObject(transforms.Transform([0, -15], 0, [200, 20]), [], None).SetParent(UI)
    UI.childs[0].AddComp(rendering.Model('Assets\JustSquare.obj', [255, 128, 128]))
    objects_structure.GameObject(transforms.Transform([0, 0], 0, [1, 1]), [], None).SetParent(UI.childs[0])
    UI.childs[0].childs[0].AddComp(rendering.Primitive(0, [255, 196, 196]))
    #ammo bar
    objects_structure.GameObject(transforms.Transform([0, 15], 0, [200, 20]), [], None).SetParent(UI)
    UI.childs[1].AddComp(rendering.Model('Assets\JustSquare.obj', [128, 128, 255]))
    objects_structure.GameObject(transforms.Transform([0, 0], 0, [1, 1]), [], None).SetParent(UI.childs[1])
    UI.childs[1].childs[0].AddComp(rendering.Primitive(0, [196, 196, 255]))
    #recharge bar
    objects_structure.GameObject(transforms.Transform([0, 45], 0, [200, 20]), [], None).SetParent(UI)
    UI.childs[2].AddComp(rendering.Model('Assets\JustSquare.obj', [128, 255, 128]))
    objects_structure.GameObject(transforms.Transform([0, 0], 0, [1, 1]), [], None).SetParent(UI.childs[2])
    UI.childs[2].childs[0].AddComp(rendering.Primitive(0, [196, 255, 196]))

    #Creating Background:
    Stars = []
    for i in range(0, 100):
        star = objects_structure.GameObject(transforms.Transform([random.random() * border[0], random.random() * border[1]], random.random() * 360, [random.randint(5, 15), random.randint(5, 15)]), [], None)
        star.AddComp(rendering.Model('Assets\Cursor.obj', getRandCol()))
        Stars.append(star)

    deltaTime = time.time()
    pastTime = time.time()

    #phasesHandling
    inBattle = True
    dangerLevel = 1

    while 1:
        #Frames and time managment
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
                #MouseInputs[1] = [-int(MouseInputs[1][0]), -int(MouseInputs[1][1]), -int(MouseInputs[1][2])]
                MouseInputs[0] = [MouseInputs[0][0] + MouseInputs[1][0], MouseInputs[0][1] + MouseInputs[1][1], MouseInputs[0][2] + MouseInputs[1][2]]
        
        #Waves handling:
        if len(Enemies) == 0: #if no enemies proceed to upgrade phase
            #print('No enemies here')
            if inBattle == True: #changing phases
                inBattle = False
                #applying spawned Item to upgrade object
                for upgrade in Upgrades:
                    randomItem = GetRandomItem(AllItems)
                    #upgrade.GetComp('Item') = GetRandomItem(AllItems) #will it work?
                    upgrade.RemoveComp(upgrade.GetComp('Item')) #removing old item
                    upgrade.AddComp(randomItem)
                    upgrade.GetComp('Model').file = 'Assets/' + randomItem.image + '.obj' #'Assets\' + randomItem.image + '.obj'
                    upgrade.GetComp('Model').LoadModel()
                    upgrade.childs[0].GetComp('Text').content = randomItem.name
                    upgrade.childs[1].GetComp('Text').content = randomItem.desc
            else: #we are already in upgrade phase
                for upgrade in Upgrades:
                    #if cursor is over an upgrade and right mouse button has been pressed
                    if upgrade.GetComp('Collider').Collide(Cursor.GetComp('Collider')) == True and MouseInputs[1][2] == 1:
                       inBattle = True
                       upgrade.GetComp('Item').ApplyItem(Player.GetComp('Ship'), [PlayerGun.GetComp('Gun')])
                       print('You got an Item!')
                       #fully heal player:
                       Player.GetComp('Ship').maxhp.UpdateModifiers()
                       Player.GetComp('Ship').hp = Player.GetComp('Ship').maxhp.value
                       #and do needed stuff for player:
                       Player.GetComp('Ship').size.UpdateModifiers()
                       Player.transform.lscale = transforms.ScaleVect([1, 1], Player.GetComp('Ship').size.value)
                       Player.transform.Desynch()

                       #also spawn enemies here
                       dangerLevel += 3
                       spawnPower = dangerLevel
                       #spawn until filled the level
                       while spawnPower > 0:
                           #directEnemySpawn
                           enemyType = random.randint(1, 4)
                           enemy = objects_structure.GameObject(transforms.Transform([random.random() * border[0], random.random() * border[1]], 0, [1, 1]), [], None)
                           #Changing enemy apperance based on type
                           if enemyType == 1:
                                enemy.AddComp(rendering.Model('Assets\Ship2.obj', [255, 0, 0]))
                           elif enemyType == 2:
                                enemy.AddComp(rendering.Model('Assets\Ship1.obj', [255, 0, 0]))
                           elif enemyType == 3:
                                enemy.AddComp(rendering.Model('Assets\Ship3.obj', [255, 0, 0]))
                           elif enemyType == 4:
                                enemy.AddComp(rendering.Model('Assets\Ship4.obj', [255, 0, 0]))
                           enemy.AddComp(rendering.Model('Assets\Ship1.obj', [255, 0, 0]))
                           enemy.AddComp(physics.PhysicObject([0, 0], [0, 0], 1))
                           enemy.AddComp(physics.Collider(0, [1, 1]))
                           enemy.AddComp(combat.Ship(10, 15, 3, 5, 0.5))
                           #recalculate object scale based on size:
                           enemy.transform.lscale = transforms.ScaleVect(enemy.transform.lscale, enemy.GetComp('Ship').size.value)
                           enemy.transform.Desynch()
                           #enemy.AddComp(combat.Enemy(1, 1, 2, 1, 1))
                           enemy.AddComp(GetDesignedAI(enemyType))
                           #enemy.AddComp(GetDesignedAI(4))
                           #generating enemy gun
                           enemyGun = objects_structure.GameObject(transforms.Transform([2, 0], 0, [2 / enemy.transform.lscale[0], 2 / enemy.transform.lscale[1]]), [], enemy)
                           enemyGun.AddComp(combat.Gun([196, 128, 0], 10, 1, 6, 2, 3, 3, 2.5, 0.5, 1, 10))
                           Enemies.append(enemy)

                           spawnPower -= 1
                           #addingItemsToEnemy
                           while random.random() * dangerLevel > math.sqrt(dangerLevel) and spawnPower != 0:
                                GetRandomItem(AllItems).ApplyItem(enemy.GetComp('Ship'), enemy.GetCompsInChilds('Gun'))
                                spawnPower -= 1
                           #synchEnemiesSize:
                           enemy.transform.lscale = transforms.ScaleVect([1, 1], enemy.GetComp('Ship').size.value)
                           enemy.transform.Desynch()

                       inBattle = True
                       break

        #CursorPos:
        #Cursor.transform.lpos = GetFixedMousePos(size)
        Cursor.transform.lpos = GetWorldMousePos(size, Player.transform.lpos)
        Cursor.transform.Desynch()

        #updatingPLayerMovement
        if Player.GetComp('Ship').hp > 0: #well player can only act if still alive
            Player.GetComp('Ship').Move(max(0, UpDownInput[0]), -min(0, UpDownInput[0]), 1, Cursor.transform, deltaTime)
            Player.GetComp('PhysicObject').UpdateVel()
            #preventing from not so rare glitch about player reaching uncontrollable high speed
            Player.GetComp('PhysicObject').vel = transforms.RangeVect(Player.GetComp('PhysicObject').vel, 100)
            Player.GetComp('PhysicObject').PreupdatePos()
            Player.GetComp('PhysicObject').ExecutePos()

            #playerShooting
            for comp in PlayerGun.GetComps('Gun'):
                comp.UpdateShootingState(deltaTime, MouseInputs[0][0], MouseInputs[1][2])
                comp.UpdateBullets(deltaTime)

        #updating enemies
        for enemy in Enemies:
            enemy.GetComp('Enemy').UpdateAI(deltaTime, Player.transform)
            enemy.GetComp('PhysicObject').PreupdatePos()
            enemy.GetComp('PhysicObject').ExecutePos()
            #shooting:
            for guns in enemy.GetCompsInChilds('Gun'):
                guns.UpdateBullets(deltaTime)
            #destroyEnemy if techincally dead:
            if enemy.isRemoved == True:
                Enemies.remove(enemy)

        #enemies shooting:
        for guns in Dummy.GetCompsInChilds('Gun'):
            guns.UpdateBullets(deltaTime)

        #afferting position for camera pourposes:
        CameraPiviot = Player.transform.lpos

        #simpleBackgroundAnimation
        for star in Stars:
            randomAnim = (random.random() -0.5) * 2
            star.transform.lscale = transforms.RangeVect(transforms.AddVect(star.transform.lscale, [randomAnim, randomAnim]), 20)
            star.transform.Desynch()

        #BoderHandling
        #for Object in GlobalObjects:
        for star in Stars:
            star.transform.LimitByTransform(Player.transform, border)
        for enemy in Enemies:
            enemy.transform.LimitByTransform(Player.transform, border)
            for guns in enemy.GetCompsInChilds('Gun'):
                for bullet in guns.Bullets:
                    bullet.transform.LimitByTransform(Player.transform, border)
        for upgrade in Upgrades:
            upgrade.transform.LimitByTransform(Player.transform, border)
        for guns in Player.GetCompsInChilds('Gun'):
            for bullet in guns.Bullets:
                bullet.transform.LimitByTransform(Player.transform, border)

        #Dummy.transform.LimitByTransform(Player.transform, border)

        #Collision Detection On Dummy:
        #if PlayerGun.GetComp('Gun').Bullets[0]
        #for bullet in PlayerGun.GetComp('Gun').Bullets:
            #if(Dummy.GetComp('Collider').Collide(bullet.GetComp('Collider')) == True):
                #Dummy.GetComp('Ship').ReceiveDamage(PlayerGun.GetComp('Gun').dmg)
                #PlayerGun.GetComp('Gun').Bullets.remove(bullet)
        #CollisionDetectionOnEnemies:
        for enemy in Enemies:
            for bullet in PlayerGun.GetComp('Gun').Bullets:
                if enemy.GetComp('Collider').Collide(bullet.GetComp('Collider')) == True:
                    enemy.GetComp('Ship').ReceiveDamage(PlayerGun.GetComp('Gun').dmg)
                    PlayerGun.GetComp('Gun').Bullets.remove(bullet)

        #CollisionDetectionForPlayer:
        #really dumb for now, with no optimization
        if Player.GetComp('Ship').hp > 0:
            for enemy in Enemies:
                playerCollider = Player.GetComp('Collider')
                playerShip = Player.GetComp('Ship')
                for guns in enemy.GetCompsInChilds('Gun'):
                    for bullet in guns.Bullets:
                        if playerCollider.Collide(bullet.GetComp('Collider')) == True:
                            playerShip.ReceiveDamage(guns.dmg)
                            guns.Bullets.remove(bullet)

        #UpdatingInteface:
        UI.childs[0].childs[0].transform.lscale[0] = max(0, Player.GetComp('Ship').hp / Player.GetComp('Ship').maxhp.value / 2)
        UI.childs[0].childs[0].transform.lpos[0] = (1 - UI.childs[0].childs[0].transform.lscale[0] * 2) / 2
        UI.childs[0].childs[0].transform.Desynch()
        for gun in  Player.GetCompsInChilds('Gun'):
            UI.childs[1].childs[0].transform.lscale[0] = gun.magazine / gun.ammo.value / 2
            UI.childs[1].childs[0].transform.lpos[0] = (1 - UI.childs[1].childs[0].transform.lscale[0] * 2) / 2
            UI.childs[2].childs[0].transform.lscale[0] = gun.waitTime * gun.recharge.value / 2
            UI.childs[2].childs[0].transform.lpos[0] = (1 - UI.childs[2].childs[0].transform.lscale[0] * 2) / 2
        UI.childs[1].childs[0].transform.Desynch()
        UI.childs[2].childs[0].transform.Desynch()


        #global rendering
        screen.fill(background)

        #also for now
        for star in Stars:
            star.GetComp("Model").Render(screen, size, CameraPiviot)

        #enemies
        for enemy in Enemies:
            enemy.GetComp('Model').Render(screen, size, CameraPiviot)
            for guns in enemy.GetCompsInChilds('Gun'):
                guns.RenderBullets(screen, size, CameraPiviot)

        #for now
        #Dummy.GetComp('Model').Render(screen, size)
        #for guns in Dummy.GetCompsInChilds('Gun'):
            #print('I have a gun')
            #guns.RenderBullets(screen, size, CameraPiviot)
        
        #
        #for playerComp in Player.components:
            #print(type(playerComp))
        for Object in GlobalObjects:
            for Model in Object.GetComps('Model'):
                Model.Render(screen, size, CameraPiviot)
            for Primitive in Object.GetComps('Primitive'):
                Primitive.Render(screen, size, CameraPiviot)

        #RenderingBullets
        PlayerGun.GetComp('Gun').RenderBullets(screen, size, CameraPiviot)

        #only render upgrades when not fighting
        if inBattle == False:
            #print('out of battle')
            for upgrade in Upgrades:
                upgrade.GetComp('Model').Render(screen, size, CameraPiviot)
                for child in upgrade.childs:
                    child.GetComp('Text').Render(screen, size, CameraPiviot)
                #upgrade.childs[0].GetComp('Text').Render(screen, size, CameraPiviot)
                #print(upgrade.childs[1].GetComp('Text').content)
                #upgrade.childs[1].GetComp('Text').Render(screen, size, CameraPiviot)
        
        #RenderingUI:
        #UI.GetComp('Model').Render(screen, size, [0, 0])
        for model in UI.GetCompsInChilds('Model'):
            model.Render(screen, size, [0, 0])
        for primitive in UI.GetCompsInChilds('Primitive'):
            primitive.Render(screen, size, [0, 0])
        #UI.childs[0].GetComp('Primitive').Render(screen, size, [0, 0])
        UI.childs[2].childs[0].GetComp('Primitive').Render(screen, size, [0, 0])

        #rendering accoring to player being alive or dead
        if Player.GetComp('Ship').hp <= 0:
            #here show game over screen:
            GameOverScreen.GetComp('Text').Render(screen, size, [0, 0])
            #print('game over')
            #pygame.quit()
            #sys.exit()
        else:
            Player.GetComp('Model').Render(screen, size, CameraPiviot)

        pygame.display.flip();



if __name__ == '__main__':
    main()
    pygame.quit()
    sys.exit()
