import game_object
import random
import enums
import rendering
from transforms import *

class Enemy():

    def __init__(self):
        self.gameObject = None
        self.transform = None
        self.phys = None
        self.playerTransform = None
        self.playerPhys = None
        self.minObstacleAvoidanceLength = 0
        self.breakMultiplier = 0.2
        self.directionChangeThreshold = 0.001953125
        self.wanderCircleDebug = None #transform
        self.wanderTarget = None #transform
        self.wanderJitter = 0.1 * math.pi #placeholder value
        self.wanderDistance = 1 #placeholder value
        self.wanderRadius = 15 #placeholder value
        self.wanderPoint = Vector([1, 0])
        self.debugFlag = enums.DebugFlag(0)
        self.debugCol = (255, 0, 255)

    def Start(self, playerTransform, playerPhysic):
        self.transform = self.gameObject.transform
        self.phys = self.gameObject.GetComp('PhysicObject')
        self.playerTransform = playerTransform
        self.playerPhys = playerPhysic

        #debug objects:
        self.wanderCircleDebug = game_object.GameObject(Transform(Vector([0, 0]), 0, Vector([1, 1])), [], self.gameObject)
        self.wanderCircleDebug.transform.lpos = Vector([self.wanderDistance, 0])
        self.wanderCircleDebug.transform.lscale = Vector([self.wanderRadius, self.wanderRadius])
        self.wanderCircleDebug.AddComp(rendering.Primitive(enums.PrimitiveType.CIRCLE, self.debugCol, 1))
        
        #initialize local values:


    def Debug(self, MainCamera):
        self.transform.SynchGlobals()

        if enums.DebugFlag.DIRECTION in self.debugFlag:
            MainCamera.RenderRawLine(self.transform.pos, self.transform.LocalToGlobal(Vector([1, 0]), True), self.debugCol, 1)
        if enums.DebugFlag.VELOCITY in self.debugFlag:
            MainCamera.RenderRawLine(self.transform.pos, self.transform.pos + self.phys.vel, self.debugCol, 1)
        if enums.DebugFlag.WANDER in self.debugFlag:
            resultPoint = self.wanderPoint + Vector([self.wanderDistance, 0])

            #position correctly and render debug cicrle
            self.wanderCircleDebug.transform.lpos = Vector([self.wanderDistance, 0]) / self.transform.lscale.MaxComponent()
            self.wanderCircleDebug.transform.lscale = Vector([self.wanderRadius, self.wanderRadius]) / self.transform.lscale
            
            self.wanderCircleDebug.transform.SynchGlobals()
            MainCamera.RenderPrimitive(self.wanderCircleDebug.GetComp('Primitive'))

            #render line towards end point
            MainCamera.RenderRawLine(self.transform.pos, self.transform.LocalToGlobal(resultPoint, True), self.debugCol, 1)


    #corrects object transform, so that it always faces the direction it is going (by velocity)
    def UpdateForwardDirection(self):
        if self.phys.vel.Length() > self.directionChangeThreshold:
            self.transform.lrot = self.phys.vel.ToRotation()
            self.transform.Desynch()
    

    def Seek(self):
        self.transform.SynchGlobals()
        self.playerTransform.SynchGlobals()
        desiredVelocity = (self.playerTransform.pos - self.transform.pos) * self.phys.maxVel
        #applying force
        self.phys.TryAccumulateForce(desiredVelocity - self.phys.vel)

    #wander works mostly by using already existing game objects structure
    def Wander(self):
        self.transform.SynchGlobals()
        print(self.wanderPoint.data)
        self.wanderPoint += Vector([random.uniform(-self.wanderJitter, self.wanderJitter), random.uniform(-self.wanderJitter, self.wanderJitter)])
        print(self.wanderPoint.data)
        #snap target point to land exacly at the border of a circle located at the player
        self.wanderPoint = self.wanderPoint.Normalized() * self.wanderRadius
        print(self.wanderPoint.data)
        #here we no longer use wander point to do not disrupt it's future behaviour
        resultPoint = self.wanderPoint + Vector([self.wanderDistance, 0])
        print(self.wanderPoint.data)

        #calculate resulting force
        resultForce = self.transform.LocalToGlobal(resultPoint, True) - self.transform.pos
        self.phys.TryAccumulateForce(resultForce)
        print(self.wanderPoint.data)
    '''
    def Wander(self):
        #wander radius is circle scale
        #wander distance is circle local x position
        
        #okay, the whole method is balantly stupid, instead of rotating point around perimeter, it moves it in global space and then "snaps" to circle boundary, like WTF
        self.wanderCircle.SynchGlobals()
        self.wanderTarget.SynchGlobals()
        wanderRadius = self.wanderCircle.scale.MaxComponent()
        wanderTargetPoint = self.wanderTarget.pos
        #randomize target position in a stupid way
        wanderTargetPoint += Vector([random(-wanderJitter, wanderJitter), random(-wanderJitter, wanderJitter)])
        #snap target point to land exacly at the border of a circle
        wanderTargetPoint = self.wanderCircle.pos + (wanderTargetPoint - self.wanderCircle.pos).Truncate(wanderRadius)
        #self.wanderCircle.lrot += 
		pass
    '''


    def ObstacleAvoidance(self, sceneObstacles): #checkout range is same as this object collision bounding box (which is it's scale)
        result = None
        self.transform.SynchGlobals()
        castWidth = self.transform.scale.MaxComponent()
        self.minObstacleAvoidanceLength = castWidth
        castLength = self.minObstacleAvoidanceLength + (self.phys.vel.Length() / self.phys.maxVel) * self.minObstacleAvoidanceLength
        hit = self.minObstacleAvoidanceLength * 2 + 1 #max obstacle avoidance + epsilon to be out of range
        hitObjectLocalPos = Vector([0, 0])
        hitColliderRadius = 0
        #updating debug objects

        #
        for Object in sceneObstacles:
            for collider in Object.GetComps('Collider'):
                if collider.type != enums.ColliderType.SPHERE:
                    continue
                colliderTrans = collider.gameObject.transform
                colliderTrans.SynchGlobals()
                #1. check if outside of range (yes, check happens BEFORE convertion to local space)
                colliderRadius = colliderTrans.scale.MaxComponent()
                if Vector.Dist(self.transform.pos, colliderTrans.pos) > (castLength + colliderRadius):
                    continue
                #2. convert to local space
                localColliderPos = self.transform.GlobalToLocal(colliderTrans.pos, True)
                #3. discard objects behind ray (yes, also objects that eventually clip into ray)
                if localColliderPos.x() < 0:
                    continue
                #4. check if collision occurs (broad collision case)

                if abs(localColliderPos.y()) - colliderRadius - castWidth > 0:
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
                    hitObjectLocalPos = localColliderPos
                    hitColliderRadius = colliderRadius
                    result = collider.gameObject
            
        #calculating steering force
        #possible bug, must ask for it, object may have it's x dist outside of cast length while still properly recording cast collision   
        forceMult = 1.0 + (castLength - hitObjectLocalPos.x()) / castLength
        steeringForce = [0, 0]
        steeringForce[1] = (hitColliderRadius - hitObjectLocalPos.y()) * forceMult
        steeringForce[0] = (hitColliderRadius - hitObjectLocalPos.x()) * breakMultiplier


        #convert and aplly final result
        self.phys.TryAccumulateForce(self.transform.LocalToGlobal(Vector(steeringForce), True))

    def WallAvoidance(self, sceneBorder):
        pass