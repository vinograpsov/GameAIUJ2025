import game_object
from transforms import *

#Made as for collision detection
'''SDF comparing to [0, 0] point, original formula'''
def CubeSDF(point, size):
    outside = [abs(point[0]) - size[0], abs(point[1]) - size[1]]
    #first part calculates the leftover distance from cube, other part gives the inside distance in the cube (if we are inside)
    return VectToDist([max(outside[0], 0), max(outside[1], 0)]) + min(max(outside[0], outside[1]), 0)

#unused, old code for colliding with boundaries
def ReflectDeg(orgDeg, surfDim):
    surfChange = 0
    if surfDim >= 2:
        surfChange = 180
    return ((360 - orgDeg) + surfChange) % 360
#unused, old code for colliding with boundaries
def BoundBounce(Bounds, EndPos, EndVel):
    BouncedPos = list(EndPos)
    if EndPos[0] < Bounds[0][0]: #left
        BouncedPos[0] = Bounds[0][0] + (Bounds[0][0] - EndPos[0])
        EndVel[0] = -EndVel[0]
    if EndPos[0] > Bounds[0][1]: #right
        BouncedPos[0] = Bounds[0][1] - (EndPos[0] - Bounds[0][1])
        EndVel[0] = -EndVel[0]
    if EndPos[1] > Bounds[1][1]: #down
        BouncedPos[1] = Bounds[1][1] - (EndPos[1] - Bounds[1][1])
        EndVel[1] = -EndVel[1]
    if EndPos[1] < Bounds[1][0]: #up
        BouncedPos[1] = Bounds[1][0] + (Bounds[1][0] - EndPos[1])
        EndVel[1] = -EndVel[1]
    return BouncedPos, EndVel

class PhysicObject():

    def __init__(self, vel, acc, res):
        self.gameObject = None
        self.newPos = [0, 0]
        self.vel = vel #velocity
        self.acc = acc #acceleration
        self.res = res #resistance
    
    def ApplyForce(self, rot, force):
        self.vel = ApplyDirForce(self.vel, rot, force)

    def ReduceForce(self, force):
        self.vel = ApplyDirForce(self.vel, VectToDeg(self.vel), -min(VectToDist(self.vel), force))

    def ApplyArcForce(self, piviot, force): #piviot is a transform
        trans = self.gameObject.transform
        trans.SynchGlobals()
        piviot.SynchGlobals()
        
        newPos = Reposition(SubVect(piviot.pos, trans.pos), Transform(piviot.pos, force * 3.14, [1, 1]))
        self.vel = AddVect(self.vel, SubVect(newPos, trans.pos))

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

    def UpdateVel(self):
        self.vel = ScaleVect(AddVect(self.vel, self.acc), self.res)

    def PreupdatePos(self):
        #return transformations.AddVect(Transform.pos, self.vel)
        #self.newPos = AddVect(ScaleVect(self.gameObject.transform.lpos, deltaTime * 10), self.vel)
        self.newPos = AddVect(self.gameObject.transform.lpos, self.vel)

    def ExecutePos(self):
        self.gameObject.transform.lpos = self.newPos
        self.gameObject.transform.Desynch()

class Projectile():

    def __init__(self, range, lifeTime):
        self.gameObject = None
        self.range = range
        self.lifeTime = lifeTime
        self.dist = 0
        self.time = 0
        self.toDest = False
        self.physicObjTemplate = PhysicObject([0, 0], [0, 0], 0)

    def UpdateProj(self, deltaTime):
        if self.toDest == True:
            self.gameObject.isRemoved = True
            return

        physicObj = self.gameObject.GetComp('PhysicObject')
        #physicObj = self.gameObject.transform
        #print(self.physicObjTemplate)
        #print(physicObj)
        #print(self.gameObject.GetComp(self.physicObjTemplate))
        distChange = VectToDist(physicObj.vel)
        self.dist += distChange
        self.time += deltaTime

        #return
        if self.dist > self.range:
            #extrapolating end of life point
            lastDist = self.dist - self.range
            physicObj.vel = SubVect(physicObj.vel, ScaleVect(physicObj.vel, lastDist / distChange))
            self.toDest = True
        if self.time > self.lifeTime:
            #extrapolating end of life point
            lastTime = self.time - self.lifeTime
            physicObj.vel = SubVect(physicObj.vel, ScaleVect(physicObj.vel, lastTime / deltaTime))
            self.toDest = True

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

