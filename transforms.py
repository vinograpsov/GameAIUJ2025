'''this module held mostly functions used for operating on 2d space coordinates
this means scalling, rotating etc.
usually takes vectors as arguments and outputs also vectors'''

#BASIC TRANSFORMATIONS
#mostly conversion, used later in complex transformations

import math

'''returns min ignoring - values and returns them without changing their original sign'''
def absMin(v1, v2):
    if abs(v1) < abs(v2):
        return v1
    return v2

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


class Transform:

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

    '''rotates one object so that it faces another tranform(position) withing a slope'''
    def RotateTowards(self, other, strength):
        #First update both object's globals
        self.SynchGlobals()
        other.SynchGlobals()

        TargetRot = VectToDeg(SubVect(other.pos, self.pos)) #calculates direction and converts to rot
        idealTarget = absMin(TargetRot - self.lrot, (180 + TargetRot) % 360 - (180 + self.lrot) % 360)

        self.lrot += min(abs(idealTarget), strength) * math.copysign(1, idealTarget)
        self.lrot %= 360
 
        self.Desynch()

    '''shows the diffrence in angles between one transform rotation and other transform position'''
    def RotateDiff(self, other):
        #First update both object's globals
        self.SynchGlobals()
        other.SynchGlobals()

        TargetRot = VectToDeg(SubVect(other.pos, self.pos))
        return abs(absMin(TargetRot - self.lrot, (180 + TargetRot) % 360 - (180 + self.lrot) % 360))

    '''returns distance between two transforms'''
    def Distance(self, other):
        self.SynchGlobals()
        other.SynchGlobals()

        return VectToDist(SubVect(self.pos, other.pos))


