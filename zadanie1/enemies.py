import game_object
import random
import enums
import rendering
from collisions import LineIntersection2D
from transforms import *

class Enemy():

    def __init__(self):
        self.gameObject = None
        self.transform = None
        self.phys = None
        self.playerTransform = None
        self.playerPhys = None
        #general
        self.directionChangeThreshold = 0.001953125
        #obstacle avoidance
        self.minObstacleAvoidanceLength = 0
        self.breakMultiplier = 0.2
        #wander
        self.wanderJitter = 0.1 * math.pi #placeholder value
        self.wanderDistance = 1 #placeholder value
        self.wanderRadius = 15 #placeholder value
        self.wanderTarget = None #transform
        self.wanderPoint = Vector([1, 0])
        #wall avoidance
        self.wallDetectionRange = 1 # placeholder value
        #debug
        self.debugFlag = enums.DebugFlag(0)
        self.debugCol = (255, 0, 255)
        self.wanderCircleDebug = None #transform
        self.obstacleAvoidanceDebug = None #transform

    def Start(self, playerTransform, playerPhysic, mainCamera):
        self.transform = self.gameObject.transform
        self.phys = self.gameObject.GetComp('PhysicObject')
        self.playerTransform = playerTransform
        self.playerPhys = playerPhysic

        #debug objects:
        self.mainCamera = mainCamera
        self.wanderCircleDebug = game_object.GameObject(Transform(Vector([0, 0]), 0, Vector([1, 1])), [], self.gameObject)
        self.wanderCircleDebug.transform.lpos = Vector([self.wanderDistance, 0])
        self.wanderCircleDebug.transform.lscale = Vector([self.wanderRadius, self.wanderRadius])
        self.wanderCircleDebug.AddComp(rendering.Primitive(enums.PrimitiveType.CIRCLE, self.debugCol, 1))
        
        self.obstacleAvoidanceDebug = game_object.GameObject(Transform(Vector([0, 0]), 0, Vector([1, 1])), [], self.gameObject)
        self.obstacleAvoidanceDebug.AddComp(rendering.Model('Assets\ObstacleAvoidanceDebug.obj', self.debugCol, enums.RenderMode.WIREFRAME))
        #initialize local values:


    def Debug(self):
        self.transform.SynchGlobals()

        if enums.DebugFlag.DIRECTION in self.debugFlag:
            self.mainCamera.RenderRawLine(self.transform.pos, self.transform.LocalToGlobal(Vector([1, 0]), True), self.debugCol, 1)
        if enums.DebugFlag.VELOCITY in self.debugFlag:
            self.mainCamera.RenderRawLine(self.transform.pos, self.transform.pos + self.phys.vel, self.debugCol, 1)
        if enums.DebugFlag.WANDER in self.debugFlag:
            resultPoint = self.wanderPoint + Vector([self.wanderDistance, 0])

            #position correctly and render debug cicrle
            self.wanderCircleDebug.transform.lpos = Vector([self.wanderDistance, 0]) / self.transform.lscale.MaxComponent()
            self.wanderCircleDebug.transform.lscale = Vector([self.wanderRadius, self.wanderRadius]) / self.transform.lscale
            
            self.wanderCircleDebug.transform.SynchGlobals()
            self.mainCamera.RenderPrimitive(self.wanderCircleDebug.GetComp('Primitive'))

            #render line towards end point
            self.mainCamera.RenderRawLine(self.transform.pos, self.transform.LocalToGlobal(resultPoint, True), self.debugCol, 1)
        if enums.DebugFlag.OBSTACLE in self.debugFlag:
            self.mainCamera.RenderWireframe(self.obstacleAvoidanceDebug.GetComp('Model'))
        
        '''
        if enums.DebugFlag.WALL in self.debugFlag:
            mainFeeler = Vector([1, 0]) * self.wallDetectionRange
            #main feeler
            self.mainCamera.RenderRawLine(self.transform.pos, self.transform.LocalToGlobal(mainFeeler, True), self.debugCol, 1)
            #side feelers
            mainFeeler = Vector([mainFeeler.x() / 2, mainFeeler.y()])
            #print(Vector([15, 0]).Rotate(DegToRad(45)).data)
            self.mainCamera.RenderRawLine(self.transform.pos, self.transform.LocalToGlobal(mainFeeler.Rotated(DegToRad(45)), True), self.debugCol, 1)
            self.mainCamera.RenderRawLine(self.transform.pos, self.transform.LocalToGlobal(mainFeeler.Rotated(DegToRad(-45)), True), self.debugCol, 1)
        '''

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
        self.wanderPoint += Vector([random.uniform(-self.wanderJitter, self.wanderJitter), random.uniform(-self.wanderJitter, self.wanderJitter)])
        #snap target point to land exacly at the border of a circle located at the player
        self.wanderPoint = self.wanderPoint.Normalized() * self.wanderRadius
        #here we no longer use wander point to do not disrupt it's future behaviour
        resultPoint = self.wanderPoint + Vector([self.wanderDistance, 0])

        #calculate resulting force
        resultForce = self.transform.LocalToGlobal(resultPoint, True) - self.transform.pos
        self.phys.TryAccumulateForce(resultForce)


    def ObstacleAvoidance(self, sceneObstacles): #checkout range is same as this object collision bounding box (which is it's scale)
        result = None
        self.transform.SynchGlobals()
        castWidth = self.transform.scale.MaxComponent()
        self.minObstacleAvoidanceLength = castWidth
        castLength = self.minObstacleAvoidanceLength + (self.phys.vel.Length() / self.phys.maxVelocity) * self.minObstacleAvoidanceLength
        hit = self.minObstacleAvoidanceLength * 2 + 1 #max obstacle avoidance + epsilon to be out of range
        hitObjectLocalPos = Vector([0, 0])
        hitColliderRadius = 0
        
        if enums.DebugFlag.OBSTACLE in self.debugFlag:
            self.obstacleAvoidanceDebug.transform.lscale = Vector([castLength, castWidth]) / self.transform.lscale;
            self.obstacleAvoidanceDebug.transform.Desynch()

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
                extendedColliderRadius = colliderRadius + castWidth
                if abs(localColliderPos.y()) - extendedColliderRadius > 0:
                    continue
                #5. calculate contact point (narrow collision case)
                sqrtPart = math.sqrt(extendedColliderRadius * extendedColliderRadius - localColliderPos.y() * localColliderPos.y())
                contactPoint = localColliderPos.x() - sqrtPart
                if contactPoint <= 0: #closer contact point is behind ray, calculate further contact instead
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
        steeringForce[0] = (hitColliderRadius - hitObjectLocalPos.x()) * self.breakMultiplier
        
        #print(steeringForce)
        #print(self.phys.vel.data)
        #convert and aplly final result
        self.phys.TryAccumulateForce(Vector(steeringForce).Rotate(self.transform.rot))
        
        
    def WallAvoidance(self, sceneBorders):

        self.transform.SynchGlobals()
        #create feelers
        #one in front of the object
        #other 2 45deg to left and right from the front
        feelers = []
        mainFeeler = Vector([1, 0]) * self.wallDetectionRange
        
        #calculate global position of each feeler
        #yes the book also calculates global positions here, but in other manner
        feelers.append(self.transform.LocalToGlobal(mainFeeler, True))
        mainFeeler /= 2
        feelers.append(self.transform.LocalToGlobal(mainFeeler.Rotated(DegToRad(45)), True))
        feelers.append(self.transform.LocalToGlobal(mainFeeler.Rotated(DegToRad(-45)), True))

        #DEBUGGING
        if enums.DebugFlag.WALL in self.debugFlag:
            self.mainCamera.RenderRawLine(self.transform.pos, feelers[0], self.debugCol, 1)
            self.mainCamera.RenderRawLine(self.transform.pos, feelers[1], self.debugCol, 1)
            self.mainCamera.RenderRawLine(self.transform.pos, feelers[2], self.debugCol, 1)

        #defining variables
        closestIntersectionDist = 8192
        closestWallIndex = -1
        closestIntersectionPoint = Vector([0, 0])
        steeringForce = Vector([0, 0])

        for feeler in feelers:
            for i in range(0, len(sceneBorders)):
                sceneBorders[i].transform.SynchGlobals()

                curIntersectionDist = closestIntersectionDist
                intersectionPoint = Vector([0, 0])
                #define line left and right ends
                lineEndEpsilon = 800 #8192
                lineLeftEnd = sceneBorders[i].transform.LocalToGlobal(Vector([0, -lineEndEpsilon]), True)
                lineRightEnd = sceneBorders[i].transform.LocalToGlobal(Vector([0, lineEndEpsilon]), True)
                #print(sceneBorders[i].transform.pos.data)
                #print(lineLeftEnd.data)
                #print(lineRightEnd.data)

                hasIntersection, curIntersectionDist, intersectionPoint = LineIntersection2D(self.transform.pos, feeler, lineLeftEnd, lineRightEnd, curIntersectionDist, intersectionPoint)
                if hasIntersection:
                    #print(curIntersectionDist)
                    if curIntersectionDist < closestIntersectionDist:
                        #print('found closer intersection')
                        closestIntersectionDist = curIntersectionDist
                        closestWallIndex = i
                        closestIntersectionPoint = intersectionPoint.copy()


            #YES, THIS GOES SEPARATELY FOR EACH FEELER, BUT CONNECTIVELY BY EACH WALL
            #SO EACH FEELER CAN GENERATE IT'S OWN FORCE SIMULTANOUSLY IN ONE FRAME, BUT WALLS CAN'T
            #EXCUSE ME, IT IS EVEN WORSE, AS EVERY NEXT FEELER WILL SIMPLY OVERRIDE EARLIER ONES, RESSETING THEIR RESULTS
            #if intersection exists, create reaction force
            if closestWallIndex >= 0:
                Overshoot = feeler - closestIntersectionPoint

                steeringForce = sceneBorders[closestWallIndex].transform.Forward() * Overshoot.Length()

        #print(steeringForce.data)
        self.phys.TryAccumulateForce(steeringForce)