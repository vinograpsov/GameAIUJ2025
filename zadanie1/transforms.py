'''this module held mostly functions used for operating on 2d space coordinates
this means scalling, rotating etc.
usually takes vectors as arguments and outputs also vectors'''

#BASIC TRANSFORMATIONS
#mostly conversion, used later in complex transformations

import math

def RadToDeg(radians):
    return radians * 180 / math.pi

def DegToRad(degrees):
    return degrees * math.pi / 180

'''returns min ignoring - values and returns them without changing their original sign'''
def AbsMin(v1, v2):
    if abs(v1) < abs(v2):
        return v1
    return v2

class Vector:

    def __init__(self, data):
        self.data = data
    
    
    def x(self):
        return self.data[0]

    def y(self):
        return self.data[1]

    def z(self):
        return self.data[2]

    def w(self):
        return self.data[3]
    

    #OPERATORS OVERLOADING
    #------------------------------------------------------------------------

    def __neg__(self):
        result = []
        for i in range(0, len(self.data)):
            result.append(-self.data[i])
        return Vector(result.copy());

    def __add__(self, other):
        result = []
        if type(other) != type(self): #if addition by a number
            for i in range(0, len(self.data)):
                result.append(self.data[i] + other)
            return Vector(result)
        for i in range(0, len(self.data)): #if addition by a vector
            result.append(self.data[i] + other.data[i])
        return Vector(result.copy());

    def __sub__(self, other):
        result = []
        if type(other) != type(self): #if subtraction by a number
            for i in range(0, len(self.data)):
                result.append(self.data[i] - other)
            return Vector(result)
        for i in range(0, len(self.data)): #if subtraction by a vector
            result.append(self.data[i] - other.data[i])
        return Vector(result.copy());

    def __mul__(self, other):
        result = []
        if type(other) != type(self): #if scaled by a number
            for i in range(0, len(self.data)):
                result.append(self.data[i] * other)
            return Vector(result)
        for i in range(0, len(self.data)): #if scaled by a vector
            result.append(self.data[i] * other.data[i])
        return Vector(result.copy());

    def __truediv__(self, other):
        result = []
        if type(other) != type(self): #if division by a number
            for i in range(0, len(self.data)):
                result.append(self.data[i] / other)
            return Vector(result)
        for i in range(0, len(self.data)): #if division by a vector
            result.append(self.data[i] / other.data[i])
        return Vector(result.copy());

    #Assignment operators

    def __iadd__(self, other):
        result = []
        if type(other) != type(self): #if addition by a number
            for i in range(0, len(self.data)):
                result.append(self.data[i] + other)
            self.data = result
            return self
        for i in range(0, len(self.data)): #if addition by a vector
            result.append(self.data[i] + other.data[i])
        self.data = result
        return self

    def __isub__(self, other):
        result = []
        if type(other)  != type(self): #if subtraction by a number
            for i in range(0, len(self.data)):
                result.append(self.data[i] - other)
            self.data = result
            return self
        for i in range(0, len(self.data)): #if subtraction by a vector
            result.append(self.data[i] - other.data[i])
        self.data = result
        return self

    def __imul__(self, other):
        result = []
        if type(other) != type(self): #if scaled by a number
            for i in range(0, len(self.data)):
                result.append(self.data[i] * other)
            self.data = result
            return self
        for i in range(0, len(self.data)): #if scaled by a vector
            result.append(self.data[i] * other.data[i])
        self.data = result
        return self

    def __itruediv__(self, other):
        result = []
        if type(other) != type(self): #if divided by a number
            for i in range(0, len(self.data)):
                result.append(self.data[i] / other)
            self.data = result
            return self
        for i in range(0, len(self.data)): #if divided by a vector
            result.append(self.data[i] / other.data[i])
        self.data = result
        return self

    #comparison operators

    def __eq__(self, other):
        if len(self.data) != len(other.data):
            return False
        for i in range(0, len(self.data)):
            if self.data[i] != other.data[i]:
                return False
        return True

    #STATIC METHODS
    @staticmethod
    def Dist(vect1, vect2):
        return (vect1 - vect2).Length()

    @staticmethod
    def Zero(vect1):
        result = []
        for i in range(0, len(vect1.data)): #if scaled by a vector
            result.append(0)
        return Vector(result);

    @staticmethod
    def Dot(vect1, vect2):
        result = 0
        for i in range(0, len(vect1.data)):
            result += vect1.data[i] * vect2.data[i]
        return result

    '''returns projected part of other vector relative to this vector'''
    @staticmethod
    def Proj(vect1, vect2):
        dot2 = Vector.Dot(vect2, vect2)
        if dot2 == 0:
            return Vector.Zero(vect1)
        return vect2 * Vector.Dot(vect1, vect2) / dot2

    '''returns perpendicular part of other vector relative this vector'''
    @staticmethod
    def Perp(vect1, vect2):
        return vect2 - Proj(vect1, vect2)

    @staticmethod
    def AreOpposite(vect1, vect2):
        for i in range(0, len(vect1.data)):
            if (vect1.data[i] > 0 and vect2.data[i] > 0) or (vect1.data[i] < 0 and vect2.data[i] < 0):
                return False #all vector segment must be of different sign for them to be fully opposite
        return True

    '''returns min ignoring - values and returns them without changing their original sign
    @staticmethod
    def AbsMin(v1, v2):
        if abs(v1) < abs(v2):
            return v1
        return v2
    '''

    '''constructs a normalized vector based on rotation in radians'''
    @staticmethod
    def RotToVect(rot):
        result = Vector([1, 0])
        return result.Rotate(rot)

    #REGULAR METHODS

    def Length(self):
        result = 0;
        for comp in self.data:
            result += comp * comp
        return math.sqrt(result);

    '''normalizes vector''' #does not work for some reason (returns vector of vector idk)
    def Normalize(self):
        length = self.Length()
        if length == 0:
            return self
        self.data = self / length
        return self

    '''returns normalized version of the vector without changing original reference'''
    def Normalized(self):
        length = self.Length()
        if length == 0:
            return self
        return self / length

    '''capps vector so that it's magnitude is no bigger then threshold'''
    def Truncate(self, threshold):
        length = self.Length()
        if length <= threshold:
            return self #do nothing
        self.data = ((self / length) * threshold).data
        return self

    '''return truncated version of vector without changing the original'''
    def Truncated(self, threshold):
        length = self.Length()
        if length <= threshold:
            return self #do nothing
        return (self / length) * threshold

    '''despite name returns max axis value from one vector'''
    def MaxComponent(self):
        return max(self.data)

    #works only in 2D!!!
    def ToRotationDegrees(self):
        specialDeg = math.atan2(self.y(), self.x()) * 180 / math.pi
        return specialDeg + 180
    
    def ToRotation(self):
        return math.atan2(self.y(), self.x())

    #works only in 2D
    '''rotates vector'''
    def Rotate(self, rot):
        result = [self.x(), self.y()]
        result[0] = self.x() * math.cos(rot) - self.y() * math.sin(rot)
        result[1] = self.x() * math.sin(rot) + self.y() * math.cos(rot)
        self.data = result
        return self

    def RotateByVect(self, vect):
        self.Rotate(vect.ToRotation())
        return self


class Transform:
    def __init__(self, lpos, lrot, lscale):
        self.gameObject = None
        self.isSynch = False
        self.pos = lpos
        self.rot = lrot
        self.scale = lscale
        self.lpos = lpos
        self.lrot = lrot
        self.lscale = lscale

    '''returns a forward vector representing this transform facing dir'''
    def Forward(self):
        self.SynchGlobals()
        return Vector.RotToVect(self.rot)

    def ApplyLocals(self):
        self.pos.data = self.lpos.data
        self.lrot %= math.pi * 2
        self.rot = self.lrot
        self.scale.data = self.lscale.data

    '''does the same thing as reposition, but ignores scale'''
    def LocalToGlobal(self, point, ignoreScale):
        if ignoreScale is False:
            return (point * self.scale).Rotate(self.rot) + self.pos
        return point.Rotate(self.rot) + self.pos

    '''returns coordinates of a given point in transform local space'''
    def GlobalToLocal(self, point, ignoreScale):
        result = (point - self.pos).Rotate(-self.rot)
        if ignoreScale is False:
            result /= self.scale
        return result

    '''locally scales, rotates and positions given vector as a relative to transform'''
    '''actually what it does is it calculates global position of a point as if it would be child of this transform'''
    def Reposition(self, vect):
        return (vect * self.scale).Rotate(self.rot) + self.pos
        #return AddVect(RotateVect(ScaleVect(vect, transform.scale), transform.rot), transform.pos)

    def Retransform(self, other):
        #position
        self.pos = other.Reposition(self.lpos)
        #rotation
        self.rot = self.lrot + other.rot
        self.rot %= math.pi * 2
        #scale
        self.scale = self.lscale * other.scale

    '''Synchronizes global values so that they become accurate while calculating'''
    def SynchGlobals(self):
        if self.isSynch == True: #this allows to only try to synchronize
            return
        if self.gameObject.parent == None:
            self.ApplyLocals()
        else:
            self.gameObject.parent.transform.SynchGlobals()
            self.Retransform(self.gameObject.parent.transform) #using retransform foces program to wait
        self.isSynch = True

    '''marks transform and it's children as desynchronised'''
    def Desynch(self):
        self.isSynch = False
        for child in self.gameObject.childs:
            child.transform.Desynch()

    '''immediately faces one object to another tranform(position)'''
    def FaceTowards(self, other):
        #First update both object's globals
        self.SynchGlobals()
        other.SynchGlobals()

        TargetRot = (other.pos - self.pos).ToRotation() #calculates direction and converts to rot
        self.lrot = TargetRot

        self.Desynch()

    '''rotates one object so that it faces another tranform(position) with a certain speed'''
    def RotateTowards(self, other, strength):
        #First update both object's globals
        self.SynchGlobals()
        other.SynchGlobals()

        TargetRot = (other.pos - self.pos).ToRotation() #calculates direction and converts to rot 
        idealTarget = AbsMin(TargetRot - self.lrot, (math.pi + TargetRot) % (math.pi * 2) - (math.pi + self.lrot) % (math.pi * 2))
        
        self.lrot += min(abs(idealTarget), strength) * math.copysign(1, idealTarget)
        self.lrot %= math.pi * 2
        
        #TargetRot = VectToDeg(SubVect(other.pos, self.pos)) #calculates direction and converts to rot
        #idealTarget = absMin(TargetRot - self.lrot, (180 + TargetRot) % 360 - (180 + self.lrot) % 360)

        #self.lrot += min(abs(idealTarget), strength) * math.copysign(1, idealTarget)
        #self.lrot %= 360
 
        self.Desynch()

#-------------------------------------------------------------------------------------------------

#DEPRICATED

#unused
'''despite name returns max axis value from one vector'''
def MaxVect(vect):
    return max(vect)

'''adds vectors'''
def AddVect(vect1, vect2):
    result = []
    for i in range(0, len(vect1)):
        result.append(vect1[i] + vect2[i])
    return result;

'''subtracts v2 from v1'''
def SubVect(vect1, vect2):
    result = []
    for i in range(0, len(vect1)):
        result.append(vect1[i] - vect2[i])
    return result

'''scales vector by number or by other vector'''
def ScaleVect(vect, scale):
    result = []
    if type(scale) != type([]): #if scaled by a number
        for i in range(0, len(vect)):
            result.append(vect[i] * scale)
        return result
    for i in range(0, len(vect)): #if scaled by a vector
        result.append(vect[i] * scale[i])
    return result;

'''This one limits vector, well wrong naming'''
def RangeVect(vect, limit):
    result = []
    if type(limit) != type(vect): #limited by number
        for i in range(0, len(vect)):
            if vect[i] > 0:
                result.append(min(limit, vect[i]))
            else:
                result.append(max(-limit, vect[i]))
    return result

'''Loops vector within certain range: 0 +range''' 
def LimitVect(vect, limit):
    result = []
    if type(limit) != type(vect): #limited by number
        for i in range(0, len(vect)):
            result.append((limit + vect[i] % limit) % limit)
        return result
    else:
        for i in range(0, len(vect)):
            result.append((limit[i] + vect[i] % limit[i]) % limit[i])
            # (b + a % b) % b
    return result

'''returns true if both vectors are the same'''
def CompareVect(vect1, vect2):
    for i in range(0, len(vect1)):
        if vect1[i] != vect2[i]:
            return False
    return True

'''returns distance of the vector from central point'''
def VectToDist(vect):
    result = 0;
    for axis in vect:
        result = math.sqrt(result * result + axis * axis)
    return result

'''converts vector to it's directional form'''
def VectToDir(vect):
    #abs for lists:
    absVect = []
    for axis in vect:
        absVect.append(abs(axis))

    maxAxis = max(absVect)
    #maxAxis = max(vect)
    if vect[0] == 0 and vect[1] == 0:
        #print("LogWarning: cannot take dir from " + str(vect))
        return [0, 1]
    result = []
    for axis in vect:
        result.append(axis / maxAxis)
    return result

'''converts vector position to it's rotation (in deegres) relative to the central point '''
def VectToDeg(vect):
    DirVect = VectToDir(vect)
    specialDeg = math.atan2(DirVect[1], DirVect[0]) * 180 / math.pi
    return specialDeg + 180

'''converts rotation to vector directional form'''
def DegToDir(Deg):
    radians = Deg * math.pi / 180
    return [math.cos(radians), math.sin(radians)]

'''dissects given value with rotation into it's corresponding vector change'''
def DirForceToVect(rot, dist):
    VectorDir = DegToDir(rot)
    return ScaleVect(VectorDir, dist / VectToDist(VectorDir))

'''rotates vector'''
def RotateVect(vect, rot):
    #gets distance and original rotation of the vector 
    VectorDist = VectToDist(vect)
    OriginalRot = VectToDeg(vect)
    #forms entirely new vector from combinig both rotations and adjusting distance from center
    return ScaleVect(DegToDir(OriginalRot + rot), VectorDist)

#COMPLEX TRANSFORMATIONS
#more useful in case of other modules
#uses basic tranformations

'''locally scales, rotates and positions original vector as a relative to another transform'''
def Reposition(vect, transform):
    return AddVect(RotateVect(ScaleVect(vect, transform.scale), transform.rot), transform.pos)

#for later use that type
def ApplyDirForce(origin, rot, force):
    return AddVect(origin, DirForceToVect(rot, -force))

'''returns distance beetween two points in space'''
def VectDist(vect1, vect2):
        return VectToDist(SubVect(vect1, vect2))

#unused I made a wrong func
def RotDiff(vect1, vect2):
    return (VectToDeg(vect1) - VectToDeg(vect2)) % 360

class TransformOld:

    def __init__(self, lpos, lrot, lscale):
        self.gameObject = None
        self.isSynch = False #unsure
        self.pos = lpos
        self.rot = lrot
        self.scale = lscale
        self.lpos = lpos
        self.lrot = lrot
        self.lscale = lscale

    def LocalToGlobal(self):
        self.pos = self.lpos
        self.lrot %= 360
        self.rot = self.lrot
        self.scale = self.lscale

    def Retransform(self, other):
        #position
        self.pos = Reposition(self.lpos, other)
        #rotation
        self.rot = self.lrot + other.rot
        self.rot %= 360
        #scale
        self.scale = ScaleVect(self.lscale, other.scale)

    '''Synchronizes global values so that they become accurate while calculating'''
    def SynchGlobals(self):
        if self.isSynch == True: #this allows to only try to synchronize
            return
        if self.gameObject.parent == None:
            self.LocalToGlobal()
        else:
            self.gameObject.parent.transform.SynchGlobals()
            self.Retransform(self.gameObject.parent.transform) #using retransform foces program to wait
        self.isSynch = True

    '''marks transform and it's children as desynchronised'''
    def Desynch(self):
        self.isSynch = False
        for child in self.gameObject.GetObjsInChilds(self.gameObject):
            child.transform.isSynch = False

    def LimitByTransform(self, target, limit):
        #self.lpos = [self.lpos[0] % (border * 2) - border ]
        target.SynchGlobals()
        piviot = SubVect(target.pos, ScaleVect(limit, 0.5))
        self.lpos = SubVect(self.lpos, piviot)
        self.lpos = AddVect(LimitVect(self.lpos, limit), piviot)
        self.Desynch()

    '''immediately faces one obejct to another tranform(position)'''
    def FaceTowards(self, other):
        #First update both object's globals
        self.SynchGlobals()
        other.SynchGlobals()
        #First update both object's globals
        TargetRot = VectToDeg(SubVect(other.pos, self.pos)) #calculates direction and converts to rot
        self.lrot = TargetRot

        self.Desynch()

    '''rotates one object so that it faces another tranform(position) within a slope'''
    def RotateTowards(self, other, strength):
        #First update both object's globals
        self.SynchGlobals()
        other.SynchGlobals()

        TargetRot = VectToDeg(SubVect(other.pos, self.pos)) #calculates direction and converts to rot
        idealTarget = AbsMin(TargetRot - self.lrot, (180 + TargetRot) % 360 - (180 + self.lrot) % 360)

        self.lrot += min(abs(idealTarget), strength) * math.copysign(1, idealTarget)
        self.lrot %= 360
 
        self.Desynch()

    '''shows the diffrence in angles between one transform rotation and other transform position'''
    def RotateDiff(self, other):
        #First update both object's globals
        self.SynchGlobals()
        other.SynchGlobals()

        TargetRot = VectToDeg(SubVect(other.pos, self.pos))
        return abs(AbsMin(TargetRot - self.lrot, (180 + TargetRot) % 360 - (180 + self.lrot) % 360))

    '''returns distance between two transforms'''
    def Distance(self, other):
        self.SynchGlobals()
        other.SynchGlobals()

        return VectToDist(SubVect(self.pos, other.pos))


