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
        if True: #THERE IS NO DIFFERENCE BETWEEN COLLIDING WITH STATIC AND DYNAMIC OBJECT (YES NOT DIFFERENCIATING THIS IS AN ACTUAL REQUIREMENT FROM THE BOOK)
        #if targetPhys is None: #collision with static collider

            #only possible collision shapes are sphere <-> sphere sphere <-> border
            if other.type == enums.ColliderType.SPHERE:

                separation = Vector.Dist(trans.pos, targetTrans.pos) - trans.scale.MaxComponent() - targetTrans.scale.MaxComponent()

                #is collision happening
                if separation < 0:
                    collisionNormal = (trans.pos - targetTrans.pos).Normalized()
                    #position correction
                    trans.lpos += collisionNormal * -separation
                    trans.Desynch()
                    #THE BOOK FORBIDS AFFECTING VELOCITY DURING COLLISIONS IN ANY WAY!!!
                    #velocity correction
                    #projVelocity = Vector.Proj(phys.vel, collisionNormal)
                    #if Vector.AreOpposite(projVelocity, collisionNormal):
                    #    phys.vel += -projVelocity * (1 + phys.restitution)

            #sphere collision with world border
            if other.type == enums.ColliderType.LINE:
                #technically by the book line collider needs to use normal vector
                lineRelativePos = targetTrans.GlobalToLocal(trans.pos, True)
                separation = lineRelativePos.x() - trans.scale.MaxComponent() #last is sphere radius

                #is collision happening
                if separation < 0:
                    #print(lineRelativePos.data)
                    #print("collision happened")
                    collisionNormal = targetTrans.Forward()
                    #position correction
                    trans.lpos += collisionNormal * -separation
                    trans.Desynch()
                    #THE BOOK FORBIDS AFFECTING VELOCITY DURING COLLISIONS IN ANY WAY!!!
                    #velocity correction
                    #projVelocity = Vector.Proj(phys.vel, collisionNormal)
                    #if Vector.AreOpposite(projVelocity, collisionNormal):
                    #    phys.vel += -projVelocity * (1 + phys.restitution)

        else: #colision between 2 physic objects (both must be sphere)

            if other.type == enums.ColliderType.SPHERE:
                pass



#raycast is actually just a special case of obstacle avoidance algorithm
#it works the same, but has inifinite range and 0 width
class Raycast():

    #ray is always casted in the forward direction of a transform
    #by the book raycast will ignore collider when it starts inside it, that means that raycast by default will not trigger on the caster (player)
    @staticmethod
    def CastRay(transPivot, sceneObjects):
        result = None
        hit = 100000 #some arbitrary high number as ray highest range
        transPivot.SynchGlobals()
        for Object in sceneObjects:
            for collider in Object.GetComps('Collider'):
                if collider.type != enums.ColliderType.SPHERE:
                    continue
                colliderTrans = collider.gameObject.transform
                colliderTrans.SynchGlobals()
                #1. check if outside of range (skip)
                #2. convert to local space
                localColliderPos = transPivot.GlobalToLocal(colliderTrans.pos, True)
                #3. discard objects behind ray (yes, also objects that eventually clip into ray)
                if localColliderPos.x() < 0:
                    continue
                #4. check if collision occurs (broad collision case)
                colliderRadius = colliderTrans.scale.MaxComponent()
                if abs(localColliderPos.y()) - colliderRadius > 0:
                    continue
                #5. calculate contact point (narrow collision case)
                sqrtPart = math.sqrt(colliderRadius * colliderRadius - localColliderPos.y() * localColliderPos.y())
                contactPoint = localColliderPos.x() - sqrtPart
                if contactPoint <= 0: #closer contact point behind ray, calculate further contact instead
                    contactPoint = localColliderPos.x() + sqrtPart
                #6. compare contact point to old contact point
                #also update contact point to closest and returning object
                if contactPoint < hit:
                    hit = contactPoint
                    result = collider.gameObject
        return result, transPivot.LocalToGlobal(Vector([hit, 0]), True) #reposition also scales, possible bug