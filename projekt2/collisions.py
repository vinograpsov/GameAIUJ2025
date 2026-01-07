from functools import singledispatchmethod

import game_object
from rendering import Model
from transforms import *
import enums

class CollisionSolver():

    @staticmethod
    def CheckCollision(collider, other):
        trans = collider.gameObject.transform
        target = other.gameObject.transform
        trans.SynchGlobals()
        target.SynchGlobals()
        
        #only possible collision shapes are sphere <-> sphere sphere <-> line, sphere <-> polygon

        if collider.type == enums.ColliderType.SPHERE:
            if other.type == enums.ColliderType.SPHERE:
                if trans.Distance(target) < MaxVect(trans.scale) * self.size + MaxVect(target.scale) * other.size:
                    return True

            #no longer working
            if other.type == enums.ColliderType.LINE:
                firstScaledSize = trans.scale * self.size
                secondScaledSize = target.scale * other.size
                posFromCenter = abs(trans.pos - target.pos);
                if posFromCenter[0] + scaledSize > target.scale[0] * other.size:
                    return True
                if posFromCenter[1]+ scaledSize > target.scale[1] * other.size:
                    return True

            #POLYGON COLLISION DOES NOT WORK WHEN SPHERE IS FULLY INSIDE A POLYGON, IT WORKS ONLY ON EDGES AND YES THIS IS REQUIREMENT BY THE BOOK
            if other.type == enums.ColliderType.POLYGON:
                for connection in other.edges:
                    end1 = target.Reposition(Vector(other.verts[connection[0] - 1]))
                    end2 = target.Reposition(Vector(other.verts[connection[1] - 1]))
                    #if any of polygon edges collides return true
                    if CollisionSolver.LineSphereIntersectionCheck(end1, end2, trans.pos, trans.scale.MaxComponent()):
                        return True
        return False

    @staticmethod
    def LineSphereIntersectionCheck(LineStart, LineEnd, SphereCenter, SphereSize):
        if CollisionSolver.LinePointDistSquared(LineStart, LineEnd, SphereCenter) < SphereSize * SphereSize:
            return True
        return False

    @staticmethod
    def LinePointDistSquared(LineStart, LineEnd, PointPos):
        AngleToStart = Vector.Dot(PointPos - LineStart, LineEnd - LineStart)

        if AngleToStart <= 0:
            return (PointPos - LineStart).LengthSquared()

        AngleToEnd = Vector.Dot(PointPos - LineEnd, LineStart - LineEnd)

        if AngleToEnd <= 0:
            return (PointPos - LineEnd).LengthSquared()

        #middle
        closestPoint = LineStart + ((LineEnd - LineStart) * AngleToStart) / (AngleToStart + AngleToEnd)
        return (PointPos - closestPoint).LengthSquared()

    #THIS IS A BOOK REQUIREMENT, faster version of the function that only checks
    @staticmethod
    def LineIntersection2DCheck(LineStart1, LineEnd1, LineStart2, LineEnd2):

        rTop = (LineStart1.y()-LineStart2.y())*(LineEnd2.x()-LineStart2.x())-(LineStart1.x()-LineStart2.x())*(LineEnd2.y()-LineStart2.y());
        sTop = (LineStart1.y()-LineStart2.y())*(LineEnd1.x()-LineStart1.x())-(LineStart1.x()-LineStart2.x())*(LineEnd1.y()-LineStart1.y());

        Bot = (LineEnd1.x()-LineStart1.x())*(LineEnd2.y()-LineStart2.y())-(LineEnd1.y()-LineStart1.y())*(LineEnd2.x()-LineStart2.x());

        if (Bot == 0): #parallel
            return False

        r = rTop / Bot;
        s = sTop / Bot;

        if (r > 0) and (r < 1) and (s > 0) and (s < 1):
            #lines intersect
            return True

        #lines do not intersect
        return False
    
    @staticmethod
    def LineIntersection2DPoint(LineStart1, LineEnd1, LineStart2, LineEnd2):

        rTop = (LineStart1.y()-LineStart2.y())*(LineEnd2.x()-LineStart2.x())-(LineStart1.x()-LineStart2.x())*(LineEnd2.y()-LineStart2.y());
        sTop = (LineStart1.y()-LineStart2.y())*(LineEnd1.x()-LineStart1.x())-(LineStart1.x()-LineStart2.x())*(LineEnd1.y()-LineStart1.y());

        Bot = (LineEnd1.x()-LineStart1.x())*(LineEnd2.y()-LineStart2.y())-(LineEnd1.y()-LineStart1.y())*(LineEnd2.x()-LineStart2.x());

        if (Bot == 0): #parallel
            return False, 0, Vector([0, 0])

        r = rTop / Bot;
        s = sTop / Bot;

        if (r > 0) and (r < 1) and (s > 0) and (s < 1):
            #lines intersect
            FirstLineIntersectionDist = Vector.Dist(LineStart1, LineEnd1) * r

            IntersectionPoint = LineStart1 + (LineEnd1 - LineStart1) * r

            return True, FirstLineIntersectionDist, IntersectionPoint

        #lines do not intersect
        FirstLineIntersectionDist = 0
        return False, 0, Vector([0, 0])


    #can properly handle only one collider per physic object
    #UNUSED!!!!!! as project2 does not require nor use any kind of collision response so only checking for collisions is neccesarry
    #still kept in case it might be useful later
    '''
    def ResolveCollision(self, other):
        trans = self.gameObject.transform
        targetTrans = other.gameObject.transform
        trans.SynchGlobals()
        targetTrans.SynchGlobals()

        #does nothing for trigger colliders
        if self.isTrigger or other.isTrigger:
            return

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
    '''


#COLLISION SYSTEM REQUIRES REWRITING AS POLYGON IS NOT A SPECIFIC COLLIDER BUT A BUNCH OF LINE COLLIDERS
class Collider():
    def __init__(self, type): #type is collider type enum, size is vect2
        self.gameObject = None
        self.type = type
        self.size = 1 #size is unused (complicates too much)
        self.isTrigger = False

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


class PolygonCollider(Collider):

    def __init__(self, type, file): #type is collider type enum
        self.gameObject = None
        self.type = type
        self.size = 1 #size is unused (complicates too much)
        self.isTrigger = False
        #model loading
        self.file = file
        modelData = Model.LoadModel(self.file)
        self.verts = modelData[0]
        self.edges = modelData[1]

#raycast is actually just a special case of obstacle avoidance algorithm
#it works the same, but has inifinite range and 0 width
class Raycast():

    #"ray" functions as line collider with definite start and end
    @staticmethod
    def CheckRay(transPivot, endPoint, sceneObjects): #endpoint is optional type
        transPivot.SynchGlobals()
        #calculate automatic (near infinite) endpoint if not given
        if not endPoint:
            endPoint = transPivot.LocalToGlobal(Vector([8192, 0]), True)
        
        endDist = Vector.Dist(transPivot.pos, endPoint)
        #for now made only with polygons

        for Object in sceneObjects:
            for collider in Object.GetComps(Collider):
                colliderTrans = collider.gameObject.transform
                colliderTrans.SynchGlobals()
                if collider.type == enums.ColliderType.POLYGON:
                    for connection in collider.edges:
                        end1 = colliderTrans.Reposition(Vector(collider.verts[connection[0] - 1]))
                        end2 = colliderTrans.Reposition(Vector(collider.verts[connection[1] - 1]))
                        #if any of polygon edges collides return true
                        if CollisionSolver.LineIntersection2DCheck(transPivot.pos, endPoint, end1, end2):
                            return True
                elif collider.type == enums.ColliderType.SPHERE:
                    #1. check if outside of range (not here)
                    #2. convert to local space
                    localColliderPos = transPivot.GlobalToLocal(colliderTrans.pos, True)
                    #3. discard objects behind ray (yes, also objects that eventually clip into ray)
                    #and objects that are outside of range (this time also taking in account collider size)
                    colliderRadius = colliderTrans.scale.MaxComponent()
                    if localColliderPos.x() < 0 or localColliderPos.x() - colliderRadius > endDist:
                        continue
                    #4. check if collision occurs (broad collision case)
                    if abs(localColliderPos.y()) - colliderRadius <= 0:
                        return True
        return False

    '''returns a list of all objects that intersects with ray'''
    def CollectRay(transPivot, endPoint, sceneObjects): #endpoint is optional type
        result = []
        transPivot.SynchGlobals()
        #calculate automatic (near infinite) endpoint if not given
        if not endPoint:
            endPoint = transPivot.LocalToGlobal(Vector([8192, 0]), True)
        
        endDist = Vector.Dist(transPivot.pos, endPoint)

        for Object in sceneObjects:
            for collider in Object.GetComps(Collider):
                colliderTrans = collider.gameObject.transform
                colliderTrans.SynchGlobals()
                if collider.type == enums.ColliderType.POLYGON:
                    for connection in collider.edges:
                        end1 = colliderTrans.Reposition(Vector(collider.verts[connection[0] - 1]))
                        end2 = colliderTrans.Reposition(Vector(collider.verts[connection[1] - 1]))
                        #if any of polygon edges collides return true
                        if CollisionSolver.LineIntersection2DCheck(transPivot.pos, endPoint, end1, end2):
                            result.append(collider.gameObject)
                elif collider.type == enums.ColliderType.SPHERE:
                    if LineSphereIntersectionCheck(transPivot.pos, endPoint, colliderTrans.pos, colliderTrans.scale.MaxComponent()):
                        result.append(collider.gameObject)
        return result

    #ray is always casted in the forward direction of a transform
    #by the book raycast will ignore collider when it starts inside it, that means that raycast by default will not trigger on the caster (player)
    @staticmethod
    def CastRay(transPivot, sceneObjects):
        result = None
        hit = 8192.0 #some arbitrary high number as ray highest range
        contactPoint = hit
        #calculate automatic (near infinite) endpoint if not given
        endPoint = transPivot.LocalToGlobal(Vector([8192, 0]), True)

        transPivot.SynchGlobals()
        for Object in sceneObjects:
            for collider in Object.GetComps(Collider):
                colliderTrans = collider.gameObject.transform
                colliderTrans.SynchGlobals()

                contactPoint = hit
                if collider.type == enums.ColliderType.SPHERE:
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

                if collider.type == enums.ColliderType.POLYGON:
                    for connection in collider.edges:
                        end1 = colliderTrans.Reposition(Vector(collider.verts[connection[0] - 1]))
                        end2 = colliderTrans.Reposition(Vector(collider.verts[connection[1] - 1]))

                        doesHit, partialContactPoint = CollisionSolver.LineIntersection2DPoint(transPivot.pos, endPoint, end1, end2)[0:2]
                        if not doesHit:
                            continue
                        if partialContactPoint < contactPoint:
                            contactPoint = partialContactPoint
                    
                #6. compare contact point to old contact point
                #also update contact point to closest and returning object
                if contactPoint < hit:
                    hit = contactPoint
                    result = collider.gameObject

        return result, transPivot.LocalToGlobal(Vector([hit, 0]), True)