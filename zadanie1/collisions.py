import game_object
from transforms import *
import enums

class Collider():
    def __init__(self, type): #type is collider type enum, size is vect2
        self.gameObject = None
        self.type = type
        self.size = 1 #size is unused (complicates too much)

    def CheckCollision(self, other):
        trans = self.gameObject.transform
        target = other.gameObject.transform
        trans.SynchGlobals()
        target.SynchGlobals()
        
        #only possible collision shapes are sphere <-> sphere sphere <-> border

        if other.type == enums.ColliderType.SPHERE:
            if trans.Distance(target) < MaxVect(trans.scale) * self.size + MaxVect(target.scale) * other.size:
                return true

        #no longer working
        if other.type == enums.ColliderType.LINE:
            firstScaledSize = trans.scale * self.size
            secondScaledSize = target.scale * other.size
            posFromCenter = abs(trans.pos - target.pos);
            if posFromCenter[0] + scaledSize > target.scale[0] * other.size:
                return True
            if posFromCenter[1]+ scaledSize > target.scale[1] * other.size:
                return True

    #can properly handle only one collider per physic object
    def ResolveCollision(self, other):
        trans = self.gameObject.transform
        targetTrans = other.gameObject.transform
        trans.SynchGlobals()
        targetTrans.SynchGlobals()

        phys = self.gameObject.GetComp('PhysicObject')
        if phys is None:
            print("LogWarning: " + "Cannot resolve collision for a static collider")
            return
        targetPhys = other.gameObject.GetComp('PhysicObject')
        if targetPhys is None: #collision with static collider

            #only possible collision shapes are sphere <-> sphere sphere <-> border
            if other.type == enums.ColliderType.SPHERE:

                separation = Vector.Dist(trans.pos, targetTrans.pos) - trans.scale.MaxComponent() - targetTrans.scale.MaxComponent()

                #is collision happening
                if separation < 0:
                    collisionNormal = (trans.pos - targetTrans.pos).Normalized()
                    #position correction
                    trans.lpos += collisionNormal * -separation
                    trans.Desynch()
                    #velocity correction
                    projVelocity = Vector.Proj(phys.vel, collisionNormal)
                    if Vector.AreOpposite(projVelocity, collisionNormal):
                        phys.vel += -projVelocity * (1 + phys.restitution)

            #sphere collision with world border
            if other.type == enums.ColliderType.LINE:
                #technically by the book line collider needs to use normal vector
                lineRelativePos = targetTrans.GlobalToLocal(trans.pos, True)
                separation = lineRelativePos.y() - trans.scale.MaxComponent() #last is sphere radius

                #is collision happening
                if separation < 0:
                    #print(lineRelativePos.data)
                    #print("collision happened")
                    collisionNormal = targetTrans.Forward()
                    #position correction
                    trans.lpos += collisionNormal * -separation
                    trans.Desynch()
                    #velocity correction
                    projVelocity = Vector.Proj(phys.vel, collisionNormal)
                    if Vector.AreOpposite(projVelocity, collisionNormal):
                        phys.vel += -projVelocity * (1 + phys.restitution)

        else: #colision between 2 physic objects (both must be sphere)

            if other.type == enums.ColliderType.SPHERE:
                pass
