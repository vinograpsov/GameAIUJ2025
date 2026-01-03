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
        self.maxVelocity = 32768 #this number is a placeholder (it is supposed to be infinity by default)
        self.maxForce = 32768 #this number is a placeholder (it is supposed to be infinity by default)
    
    def ApplyForce(self, forceVect):
        self.vel += forceVect / self.mass #* time

    #BOOK CONTAINS NO DRAG SO WE CANNOT TOO
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

    def AccumulateForce(self, force):
        self.accForce += force

    #UNUSED!!!!!
    #won't be needed in 2 project, but no reason to remove this function as book uses physics from project 1 so we should too
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
        self.accForceTotalMagnitude = 0
        self.vel.Truncate(self.maxVelocity)

    def ExecutePos(self):
        trans = self.gameObject.transform
        trans.SynchGlobals()
        trans.lpos = trans.lpos + self.vel #* time
        trans.Desynch()

