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
                pass

            #sphere collision with world border
            if other.type == enums.ColliderType.LINE:
                #technically by the book line collider needs to use normal vector
                lineRelativePos = targetTrans.GlobalToLocal(trans.pos, True)
                separation = math.max(0, -lineRelativePos.y() + trans.scale.MaxComponent()) #last is sphere radius

                collisionNormal = targetTrans.Forward()
                #position correction
                trans.lpos += collisionNormal * separation
                trans.Desynch()
                #velocity correction
                projVelocity = Vector.Proj(collisionNormal, phys.vel)
                if AreOpposite(projVelocity, collisionNormal):
                    phys.vel += -projVelocity * (1 + phys.restitution)