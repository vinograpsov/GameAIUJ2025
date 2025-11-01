import game_object
import transforms
import enums

class Collider():

    def __init__(self, type, size): #type is collider type enum, size is vect2
        self.gameObject = None
        self.type = type
        self.size = size

    def CheckCollision(self, other):
        trans = self.gameObject.transform
        target = other.gameObject.transform
        trans.SynchGlobals()
        target.SynchGlobals()
        
        #only possible collision shapes are sphere <-> sphere sphere <-> border

        if other.type == enums.ColliderType.SPHERE:
            if trans.Distance(target) < MaxVect(trans.scale) * self.size + MaxVect(target.scale) * other.size:
                return true

        if other.type == enums.ColliderType.BORDER:
            firstScaledSize = trans.scale * self.size
            secondScaledSize = target.scale * other.size
            posFromCenter = abs(trans.pos - target.pos);
            if posFromCenter[0] + scaledSize > target.scale[0] * other.size:
                return True
            if posFromCenter[1]+ scaledSize > target.scale[1] * other.size:
                return True

    def ReactCollision(self, other):
        pass

class RayCast():
    pass

    '''
class SphereCollider():

    def GetBoundingBox(self):
        trans = self.gameObject.transform;
        trans.SynchGlobals();
        return 

    def CalculateCollisionPoint(self, point):
        normal = point - self.gameObject.transform.position

class Raycast(): #raycast goes by default in the direction of the object defined by rotation



class SphereCollider(Collider):

    def GetBoundingBox(self):



    def DetectCollision(self, other): #other is also a collider
        trans = self.gameObject.transform
        target = other.gameObject.transform
        trans.SynchGlobals()
        target.SynchGlobals()

    '''

    #pre check 
