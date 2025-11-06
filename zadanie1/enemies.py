import game_object
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

	def Start(self, playerTransform, playerPhysic):
		self.transform = self.gameObject.transform
		self.phys = self.gameObject.GetComp('PhysicObject')
		self.playerTransform = playerTransform
		self.playerPhys = playerPhysic

        #debug objects:

    #corrects object transform, so that it always faces the direction it is going (by velocity)
    def UpdateForwardDirection(self):
        self.transform.lrot = self.phys.vel.ToRotation()
        self.transform.Desynch()

	def Wander(self):
		pass

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
        self.phys.accForce += self.transform.LocalToGlobal(Vector(steeringForce), True)



	def WallAvoidance(self, sceneBorder):
		pass