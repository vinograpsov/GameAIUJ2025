import random
import math
import objects_structure
import transforms
import collisions
import physics
import rendering


#maybe special thing for reversed stats?
class stat:

    def __init__(self, base, isInt):
        self.base = base
        self.addons = []
        self.rangeAddons = [] #2 sized vector, for start and end
        self.multipliers = []
        self.rangeMultipliers = [] #2 sized vector, for start and end
        self.isInt = isInt;

        #inners:
        self.value = base
        self.staticAdd = base
        self.staticMult = 1

 
    #static update, most of the times called only when picking up an item
    def PreupdateModifiers(self):
        self.staticAdd = self.base
        self.staticMult = 1
        for ad in self.addons:
            self.staticAdd += ad
        for mult in self.multipliers:
            self.staticMult *= mult

    #dynamic update, used to apply randomization to stats and calculate it's final value
    def UpdateModifiers(self):
        dynAdd = self.staticAdd
        dynMult = self.staticMult
        for radd in self.rangeAddons:
            dynAdd += radd[0] + (radd[1] - radd[0]) * random.random()
        for rmult in self.rangeMultipliers:
            dynMult *= rmult[0] + (rmult[1] - rmult[0]) * random.random()

        self.value = dynAdd * dynMult

        if self.isInt == True:
            self.value = round(self.value)
    
    #unused, currently adding effect to stat is made outside of class, as an Item class function
    def Modify(self, adds, mults, radds, rmults):
        self.addons.extend(adds)
        self.multipliers.extend(mults)
        self.rangeAddons.extend(radds)
        self.rangeMultipliers.extend(rmults)
        #immidately update modifiers since you are changing them
        UpdateModifiers(self)

#requires physic object to work
class Ship():

    def __init__(self, hp, size, speed, breaking, steering):
        self.gameObject = None
        self.maxhp = stat(hp, False)
        self.size = stat(size, False)
        self.speed = stat(speed, False)
        self.brk = stat(breaking, False)
        self.steer = stat(steering, False)

        #internals:
        self.hp = hp

    def ReceiveDamage(self, damage): #damage is the stat class
        damage.UpdateModifiers()
        self.hp -= damage.value
        if self.hp < 0:
            self.gameObject.isRemoved = True
            return
            #destroyObject

    def Move(self, wannaMove, wannaBreak, wannaRotate, rotTarget, deltaTime):
        self.speed.UpdateModifiers()
        self.brk.UpdateModifiers()
        self.steer.UpdateModifiers()
        physObj = self.gameObject.GetComp('PhysicObject')
        trans = self.gameObject.transform
        trans.RotateTowards(rotTarget, wannaRotate * 360 * self.steer.value * deltaTime)
        trans.SynchGlobals()
        physObj.ApplyForce(trans.rot, wannaMove * self.speed.value * deltaTime)
        #breaking here:
        physObj.ReduceForce(wannaBreak * self.brk.value * deltaTime)

#actually it is enemy AI
class Enemy():

    def __init__(self, rangePrec, accPrec, rechargePrec, haltPrec, closingPrec):
        self.gameObject = None
        #for weapons:
        self.rangePrec = rangePrec
        self.accPrec = accPrec
        self.rechargePrec = rechargePrec
        #for ship
        self.haltPrec = haltPrec
        self.closingPrec = closingPrec

    def UpdateAI(self, deltaTime, target):
        isMoving = [0, 0, 1] #0 is accelerating, 1 is breaking, 2 is rotating
        isShooting = [0, 0] #0 means shooting, 1 means recharging
        ship = self.gameObject.GetComp('Ship')
        guns = self.gameObject.GetCompsInChilds('Gun')
        physicObj = self.gameObject.GetComp('PhysicObject')
        trans = self.gameObject.transform

        distToTarget = trans.Distance(target)
        ship.brk.UpdateModifiers()

        #shooting handling
        for gun in guns:
           gun.acc.UpdateModifiers()
           gun.range.UpdateModifiers()
           #gun.UpdateModifiers()
           #is taget in accurency range?
           if trans.RotateDiff(target) - 180 / (gun.acc.value * self.accPrec) < 0 \
           and distToTarget <= gun.range.value * 100 / self.rangePrec: #is target withing range?
               isShooting[0] = 1
           if distToTarget >= gun.range.value * 100 * self.rechargePrec:
               isShooting[1] = 1

        velForce = transforms.VectToDist(physicObj.vel)
        closingTime = 1000000

        if velForce != 0:
           closingTime = distToTarget / velForce #amount of seconds needed to reach player within current velocity

        #moving handling
        if physicObj.isClosing(target) != True:
        #if abs(physicObj.ClosingRot(target)) > 180 / (self.closingPrec / ship.steering): #is enemy getting closer to target?
        #if physicObj.ClosingDist(target) > 100 / self.closingPrec:
            #print('not going to you')
            isMoving[1] = 1
        elif velForce - (closingTime - 1) * ship.brk.value >= -distToTarget * self.haltPrec: #checking if enemy can safely break before reaching player
        #elif target.gameObject.GetComp("PhysicObject").isClosing(trans) == True:
            isMoving[1] = 1

        elif distToTarget <= gun.range.value * 100 * self.closingPrec: #so to make enemies not try to crash directly into player
            isMoving[1] = 1
        else:
            #print('I am going')
            isMoving[0] = 1

        ship.Move(isMoving[0], isMoving[1], isMoving[2], target, deltaTime)
        for gun in guns:
           gun.UpdateShootingState(deltaTime, isShooting[0], isShooting[1])


#weapons stats (every element is a stat class)
#(Transform, acc, recoil, vel, dmg, multishot, delay, recharge, ammo)
#also has this:
#(bullets[], target)
class Gun:

    def __init__(self, col, acc, recoil, vel, size, dmg, range, delay, recharge, multishot, ammo):
        self.gameObject = None
        self.Bullets = []
        self.col = col #not a stat, just a determiner for bullet color
        self.acc = stat(acc, False)
        self.recoil = stat(recoil, False)
        self.vel = stat(vel, False)
        self.size = stat(size, True)
        self.dmg = stat(dmg, False)
        self.range = stat(range, False)
        self.waitTime = float(0) #inner stat, tells weather to shoot or not
        self.delay = stat(delay, False)
        self.doesRecharge = False #inner stat, tells if gun is recharging
        self.recharge = stat(recharge, False)
        self.magazine = ammo #inner stat, tells how much ammo is left
        self.multishot = stat(multishot, True)
        self.ammo = stat(ammo, True)

        #self.physicObjTemp = physics.PhysicObject([0, 0], [0, 0], 0)
        #self.projectileTemp = physics.Projectile(1, 1)
        #self.modelTemp = rendering.Model('Cursor.obj', [0, 0, 0])
        #self.primitiveTemp = rendering.Primitive('line', [0, 0, 0])

    def UpdateBullets(self, deltaTime):
        for bullet in self.Bullets:
            if bullet.isRemoved == True: #removing old bullets
                self.Bullets.remove(bullet)
                continue
            #print("bulletPos = " + str(bullet.transform.lpos))
            physicObj = bullet.GetComp('PhysicObject')
            physicObj.UpdateVel()
            proj = bullet.GetComp('Projectile')
            proj.UpdateProj(deltaTime)

            physicObj.PreupdatePos()
            physicObj.ExecutePos()

    def RenderBullets(self, screen, windowSize, cameraPiviot):
        for bullet in self.Bullets:
            model = bullet.GetComp('Model')
            if model != None:
                model.Render(screen, windowSize, cameraPiviot)
                #print('rendered bullet')
            primitive = bullet.GetComp('Primitive')
            if primitive != None:
                primitive.Render(screen, windowSize, cameraPiviot)

    def UpdateStats(self): #yup, this is the only way for now
        self.acc.UpdateModifiers()
        self.recoil.UpdateModifiers()
        self.vel.UpdateModifiers()
        self.size.UpdateModifiers()
        self.dmg.UpdateModifiers()
        self.range.UpdateModifiers()
        self.delay.UpdateModifiers()
        self.recharge.UpdateModifiers()
        self.multishot.UpdateModifiers()
        self.ammo.UpdateModifiers()

    def Shoot(self, deltaTime):
        self.UpdateStats()
        self.gameObject.transform.SynchGlobals()
        trans = self.gameObject.transform
        #trans.SynchGlobals()
        self.magazine -= 1
        #instantiate bullet:
        calcAcc = trans.rot + (random.random() - 0.5) * 360 / max(1, self.acc.value)
        calcSize = max(1, self.size.value)
        Bullet = objects_structure.GameObject(transforms.Transform(trans.pos, calcAcc, [10 + calcSize, calcSize]), [], None)
        Bullet.transform.pos = transforms.ApplyDirForce(trans.pos, calcAcc, (calcSize + 10) / 2 * 10) #repositions bullets based on size
        calcVel = transforms.ApplyDirForce([0, 0], calcAcc, self.vel.value * 100 * deltaTime)
        Bullet.AddComp(physics.PhysicObject(calcVel, [0, 0], 1))
        calcRange = self.range.value * 100
        Bullet.AddComp(physics.Projectile(calcRange, 10)) #lifetime mainly added for garbage collector

        Bullet.AddComp(rendering.Primitive(0, self.col))
        #recoil on gun
        calcRec = -self.recoil.value * math.copysign(1, self.vel.value) * deltaTime #we multiplies by vel, so negative vel will give negative recoil
        self.gameObject.parent.GetComp('PhysicObject').ApplyForce(calcAcc, calcRec)
        #to be made

        #collisionDetectionForBullets:
        #Bullet.AddComp(physics.Collider(0, [1, 1]))
        Bullet.AddComp(physics.Collider(1, [1, 0.1]))

        self.Bullets.append(Bullet)
        #print('shooted')
    
    def TryToShoot(self, deltaTime):
        if self.magazine == 0: #end of magazine
            self.doesRecharge = True
            return False
        elif (self.magazine - self.multishot.value) <= 0: #last possible fire
            #print("end of magazine")
            self.doesRecharge = True
            for shots in range(0, self.magazine):
                self.Shoot(deltaTime)
            return False
        else: #normal fire
            for shots in range(0, self.multishot.value):
                self.Shoot(deltaTime)
            return True

    def UpdateShootingState(self, deltaTime, wannaShoot, wannaRecharge):
        self.waitTime += deltaTime
        #print(self.waitTime)

        #recharging
        if wannaRecharge == 1:
            self.doesRecharge = True
        if self.doesRecharge == True:
            if 1 / self.recharge.value <= self.waitTime:
                self.waitTime -= 1 / self.recharge.value
                self.ammo.UpdateModifiers()
                self.magazine = self.ammo.value
                self.doesRecharge = False
            else:
                return #can't shoot while recharging, obviously

        #delay handling
        if wannaShoot != 1:
            #This makes sure that timer won't go over the next bullet
            self.waitTime = min(self.waitTime, 1 / self.delay.value)
            return

        #possible error, range(1, 0) when not enough for delay
        for timesToShoot in range(0, int(self.waitTime / (1 / self.delay.value))): #The number of times we surpassed delay
            self.waitTime -= (1 / self.delay.value)
            self.multishot.UpdateModifiers()
            if (self.TryToShoot(deltaTime) != True): #true is if we can continue shooting
                doesRecharge = True
                self.UpdateShootingState(0, wannaShoot, wannaRecharge) #can I?
                break #We do not want to still shoot if we reached end of magazine
                #question: should recharge always terminate our waiting check?