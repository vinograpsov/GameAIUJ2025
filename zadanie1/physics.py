import game_object
from transforms import *

class PhysicObject():

    def __init__(self, mass):
        self.gameObject = None
        self.mass = mass
        self.restitution = 0
        self.newPos = Vector([0, 0])
        self.vel = Vector([0, 0]) #velocity
        self.accForce = Vector([0, 0]) #accumulated velocity during a frame
        self.res = Vector([0, 0]) #resistance

        #requied by the book
        self.accForceTotalMagnitude = 0
        self.maxVel = 2 #this number is a placeholder
        self.maxForce = 2 #this number is a placeholder
    
    def ApplyForce(self, forceVect):
        self.vel += forceVect / self.mass #* time

    def ApplyForce(self, rot, force):
        forceVect = Vector.RotToVect(rot) * force
        self.vel += forceVect / self.mass #* time

    #def ReduceForce(self, force):
        #self.vel = ApplyDirForce(self.vel, VectToDeg(self.vel), -min(VectToDist(self.vel), force))

    def ApplyArcForce(self, pivot, force): #pivot is a transform
        trans = self.gameObject.transform
        trans.SynchGlobals()
        pivot.SynchGlobals()
        
        newPos = Transform(pivot.pos, force * 3.14, [1, 1]).Reposition(pivot.pos - trans.pos)
        self.vel += newPos - trans.pos
        #newPos = Reposition(SubVect(pivot.pos, trans.pos), Transform(pivot.pos, force * 3.14, [1, 1]))
        #self.vel = AddVect(self.vel, SubVect(newPos, trans.pos))

    #depricated
    def PreupdatePos(self):
        self.vel.Truncate(self.maxVelocity)
        self.newPos = self.gameObject.transform.lpos + self.vel
        #self.newPos = AddVect(self.gameObject.transform.lpos, self.vel)

    def AccumulateForce(self, force):
        self.accForce += force

    #accumulates force only when the TOTAL lenght of each force added before execution does not exeeds maxForce (also returns true false if succesfully added)
    #required by book
    def TryAccumulateForce(self, force):
        addingMagnitude = force.Length()
        remainedMagnitude = self.maxForce - self.accForceTotalMagnitude
        if remainedMagnitude <= 0: #can no longer add forces
            return False
        if  addingMagnitude <= remainedMagnitude: #add normally
            self.accForce += force
            self.accForceTotalMagnitude += addingMagnitude
        else: #there is still room for additional force, but only partiall
            self.accForce += force.Truncate(remainedMagnitude)
            self.accForceTotalMagnitude += remainedMagnitude
        return True

    def UpdateVelocity(self):
        self.ApplyForce(self.accForce.Truncate(self.maxForce))
        #self.vel += self.accForce
        self.accForce = Vector([0, 0])
        self.accForceIterativeMagnitude = 0
        self.vel.Truncate(self.maxVelocity)

    def ExecutePos(self):
        trans = self.gameObject.transform
        trans.lpos = trans.lpos + self.vel #* time
        trans.Desynch()


    '''
    def isClosing(self, target):
        trans = self.gameObject.transform
        trans.SynchGlobals()
        target.SynchGlobals()
        self.PreupdatePos()
        if VectDist(trans.pos, target.pos) >= VectDist(self.newPos, target.pos):
            return True
        return False

    def ClosingDist(self, target):
        trans = self.gameObject.transform
        trans.SynchGlobals()
        target.SynchGlobals()
        self.PreupdatePos()
        return VectDist(self.newPos, target.pos) - VectDist(trans.pos, target.pos)

    def ClosingRot(self, target):
        trans = self.gameObject.transform
        trans.SynchGlobals()
        target.SynchGlobals()
        self.PreupdatePos()
        if CompareVect(self.newPos, trans.pos):
            return 0
        firstRot = VectToDeg(SubVect(target.pos, trans.pos))
        secondRot = VectToDeg(SubVect(self.newPos, trans.pos))
        #print('first ' + str(firstRot))
        #print(secondRot)
        #print abs(firstRot - secondRot)
        return min(abs(firstRot - secondRot), abs((180 + firstRot) % 360 - (180 + secondRot) % 360))
    '''
'''
class Collider():

    def __init__(self, type, size):
        self.gameObject = None
        self.type = type #0 means circle, 1 means square
        self.size = size

    def Collide(self, other): #other is also a collider
        trans = self.gameObject.transform
        target = other.gameObject.transform
        trans.SynchGlobals()
        target.SynchGlobals()

        dist = trans.Distance(target)
        collisionDist = [0, 0]

        calcSize = ScaleVect(self.size, trans.scale)
        calcOtherSize = ScaleVect(other.size, target.scale)

        #is the collision able to occur at all?
        if trans.pos[0] - target.pos[0] - max(calcSize) - max(calcOtherSize) > 0 \
        or trans.pos[1] - target.pos[1] - max(calcSize) - max(calcOtherSize) > 0:
            return False

        #actual collision check
        if self.type == 0:
            collisionDist[0] = dist - max(calcSize)
        elif self.type == 1:
            #here goes SDF for cube:
            collisionDist[0] = CubeSDF(Reposition(SubVect(target.pos, trans.pos), Transform([0,0], -trans.lrot, [1, 1])), ScaleVect(self.size, trans.scale))
        if other.type == 0:
            collisionDist[1] = dist - max(calcOtherSize)
        elif other.type == 1:
            #here goes SDF for cube:
            collisionDist[1] = CubeSDF(Reposition(SubVect(trans.pos, target.pos), Transform([0,0], -target.lrot, [1, 1])), ScaleVect(other.size, target.scale))
        if collisionDist[0] + collisionDist[1] < dist:
            #we have collision
            #print('I hitted')
            return True
        #print(collisionDist[1])
        #print(dist)
        return False

'''
#class Animation():

    #def DefineNextAnimState(self):
        #nextState = self.state
        #return nextState

    #def __init__ (self, keyframes, timestamps):
        #self.keyframes = keyframes #keyframes are lists of transforms, while 2 given it means randomized
        #self.timestamps = timestamps #shows at wich time we schould arrive to next keyframe
        #self.waitTime = 0
        #self.state = 0
        #DefineNextAnimState()

    #def UpdateAnimation(self, deltatime):

