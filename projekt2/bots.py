import time
import math #used only in one line, in FOV check
import gc

import game_object
from transforms import *
import singletons
import random
import enums
import rendering
import events
import collisions

'''memory fragment does NOT has it's own object, it is a component of bot's object'''
class MemoryRecord():

    #as it is done in the book initialization fills with garbage data
    #yes, this fills with garbage data because oherwise every other logic in the book falls apart
    def __init__(self, source):
        self.source = source
        self.sensedPos = None #yup, this is stupid
        self.lastTimeSensed = -1024 #garbage data, initializing and leaving memory with such data will make the source activily remembered by just running application for long enough 
        self.timeBecameVisible = -1024 #garbage data
        self.lastTimeVisible = 0 #garbage data
        self.isWithinFOV = False
        self.isInLineOfSight = False
        #bot is considered visible when both in FOV and line of sight are trues

    def Destroy(self):
        self.source = None

    #BOOK REQUIREMENT
    #MEMORY FRAGMENT IS NOT DESTROYED WHEN PASSING TIME THRESHOLD, IT STAYS IN SENSORY MEMORY FOREVER!!!

    '''this returns for how long bot is currently visible, returns 0 if is not visible or just became visible (current frame)'''
    def GetCurVisibilityPeriod(self):
        #There is no mechanism preventing one from getting this time when object is not visible, giving false results
        #yes, of course I did not added one because there is non such thing in the book
        return time.time() - self.timeBecameVisible

    '''returns for how long bot is NOT visible, returns 0 if bot is currently visible'''
    def GetCurInvisibilityPeriod(self):
        #important!
        #description is not entirely true, if called mid frame this will in fact return some value when bot is currently visible
        #why is it not made correctly, because THIS is how it is made in the book
        return time.time() - self.lastTimeVisible

#BOOK REQUIERMENT!!!
#EACH BOT CAN BE REGISTERED ONLY **ONCE** IN SENSORY MEMORY
#THAT MEANS IF ALREADY REGISTERED BOT IS REGISTERED AGAIN IN ANY WAY HE REPLACES EXISTING MEMORY OF ITSELF (WHATEVER THAT WAS)

class Bot():

    def __init__(self, memorySpan, maxHealth, fov, accuracy, reactionTime, aimingPersistance):
        self.gameObject = None
        self.weapon = None
        self.memories = [] #list of memory records
        self.memorySpan = memorySpan
        self.maxHealth = maxHealth
        self.health = maxHealth
        self.fov = fov

        #bot aiming inaccuracy
        self.accuracy = accuracy
        self.reactionTime = reactionTime
        self.aimingPersistance = aimingPersistance #the time bot will continue to aim at target after target already dissapeared
        self.lastTimeReacted = time.time()

        self.debugFlag = enums.BotDebug(0)

    def Destroy(self):
        singletons.Bots.remove(self.gameObject)
        self.memories = None
        self.weapon = None

        for botObject in singletons.Bots:
            botObject.GetComp(Bot).RemoveFromMemory(self.gameObject)

    #this function is used to render debug objects based on the debug flag
    def Debug(self):
        trans = self.gameObject.transform
        trans.SynchGlobals()
        #text debugs
        if enums.BotDebug.HEALTH in self.debugFlag:
            print(self.health)
        if enums.BotDebug.DIRECTION in self.debugFlag:
            pass
        if enums.BotDebug.FIELDOFVIEW in self.debugFlag:
            fovDebugMult = 3 #used for displaying fov above player size when debugging

            lowBound = trans.rot - self.fov / 2
            highBound = trans.rot + self.fov / 2
            maxScale = trans.scale.MaxComponent()
            singletons.MainCamera.RenderRawLine(trans.pos, trans.pos + Vector.RotToVect(lowBound) * maxScale * fovDebugMult, singletons.DebugCol, 1)
            singletons.MainCamera.RenderRawLine(trans.pos, trans.pos + Vector.RotToVect(highBound) * maxScale * fovDebugMult, singletons.DebugCol, 1)
            singletons.MainCamera.RenderRawArc(trans.pos, singletons.DebugCol, trans.scale * fovDebugMult, lowBound, highBound, 1)

        if enums.BotDebug.MEMORYPOSITIONS in self.debugFlag:
            
            #this is the same as getting "valid" memories, but is copied to showcase also invalid
            curTime = time.time()
            for memory in self.memories:
                if curTime - memory.lastTimeSensed <= self.memorySpan:
                    singletons.MainCamera.RenderRawPoint(memory.sensedPos, singletons.DebugPositiveCol, 5)
                else:
                    if memory.sensedPos: #if position was ever initialized
                        singletons.MainCamera.RenderRawPoint(memory.sensedPos, singletons.DebugNegativeCol, 5)
    
    '''this function is equivalent of tergeting system from book'''
    def GetClosestValiableMemory(self):
        memories = self.GetValidMemoryRecords()
        if len(memories) <= 0:
            return None
        result = memories[0]
        trans = self.gameObject.transform
        trans.SynchGlobals()
        targetTrans = memories[0].source.gameObject.transform
        targetTrans.SynchGlobals()
        minDist = Vector.DistSquared(trans.pos, targetTrans.pos)

        for memory in memories:
            #do not return memory of itself
            if memory.source == self:
                continue
            targetTrans = memory.source.gameObject.transform
            targetTrans.SynchGlobals()
            curDist = Vector.DistSquared(trans.pos, targetTrans.pos)
            if curDist < minDist:
                minDist = curDist
                result = memory
        return result

    def TryAimAndShoot(self, mapObjects):
        possibleTargetMemory = self.GetClosestValiableMemory()

        if not possibleTargetMemory:
            return

        #aim only if there is line of sight or last sensed lower the persistance
        if possibleTargetMemory.isInLineOfSight or time.time() - possibleTargetMemory.lastTimeVisible < self.aimingPersistance:

            trans = self.gameObject.transform
            trans.SynchGlobals()
            targetTrans = possibleTargetMemory.source.gameObject.transform
            targetTrans.SynchGlobals()

            #in the book it uses actual bot position, not source pos created by sensory memory
            #shootingRot = self.weapon.Aim(possibleTargetMemory.sourcePos, self.accuracy)
            #BOOK REUIREMENT?
            #OR JUST AN OVERSIGHT THAT WE SHOULD NOT FOLLOW?
            #BOOK USES HERE POSITION OF THE BOT, **NOT** SAVED POSITION WHEN BOT WAS LAST SENSED
            #THAT MEANS THAT WHEN WE AIM AT ALREADY NOT VISIBLE ENEMY THE BOT WILL FOLLOW HIM WITH XRAY VISION
            shootingRot = (targetTrans.pos - trans.pos).ToRotation()

            #set bot rotation to visually show that he is looking at the opponent
            #this is not his shooting direction btw
            trans.lrot = shootingRot
            trans.Desynch()

            #also to actually shoot target must be visible (not memory of target)
            #and it must be visibe for some time
            if not collisions.Raycast.CheckRay(trans, targetTrans.pos, mapObjects) and time.time() - possibleTargetMemory.timeBecameVisible > self.reactionTime:
                
                #perform actual aiming algorithm
                shootingRot = self.weapon.Aim(possibleTargetMemory.source.gameObject, self.accuracy)
                #rotate again to face shooting direction
                #BOOK OVERSIGHT?
                #Yes, that means that bot will briefly look at exacly where he is shooting when TRYING to shoot, not when actually shooting
                trans.lrot = shootingRot
                trans.Desynch()

                self.weapon.TryShoot(singletons.MapObjects, singletons.Bots)

    def Kill(self):
        self.gameObject.Destroy()
                        
    def Heal(self, damage):
        self.health = min(self.health + damage, self.maxHealth)

    def DealDamage(self, damage, source):

        #TO DO
        #bot is being informed about by whom he was shot, but by other means then memory
        #(I yet need to read that one)
        
        #if source is not null then add source to memory
        #if source:
            #curMemory = self.TryCreateMemory(source)
            #curMemory.lastTimeSensed = time.time()

        print("damage dealt")
        
        self.health -= damage
        if self.health < 0:
            self.Kill()

    '''returns true if given point is within field of view, FOV is always set to 90deg'''
    def CheckFieldOfView(self, point):
        trans = self.gameObject.transform
        trans.SynchGlobals()

        facingDir = Vector.RotToVect(trans.rot)

        if Vector.Dot(facingDir, (point - trans.pos).Normalized()) >= math.cos(self.fov / 2.0):
            return True
        return False

    #SENSORY MEMORY

    def RemoveFromMemory(self, source):
        for memory in self.memories:
            if memory.source == source:
                self.memories.remove(memory)
                memory.Destroy()
                return
        print("trying to remove unexisting memory")
    
    '''this function creates memory if not existing and returns it, when already existing returns existing'''
    def TryCreateMemory(self, source):
        memory = self.FindMemoryOfSpecificSource(source)
        #memory of source not existing, create new memory
        if not memory:
            memory = self.gameObject.AddComp(MemoryRecord(source))
            self.memories.append(memory)
        return memory

    #BOOK REQUIREMENT
    #for some reason all outside game logic uses only this as an entry point
    #just like with triggers it works in reverse, so that we first fetch specific bot and only them makes calculations on him, why idk"
    def FindMemoryOfSpecificSource(self, source):
        for memory in self.memories:
            if memory.source == source:
                return memory
        #debugging
        print("requested bot not in memory")
        return None

    '''returns list of memories that did not exceeded memorySpan (it does not mean their data is actually correct)'''
    def GetValidMemoryRecords(self):
        result = []
        curTime = time.time()

        for memory in self.memories:
            if curTime - memory.lastTimeSensed <= self.memorySpan:
                result.append(memory)

        return result

    #in book vision is located in sensory memory, but since we can have our own structure I decided to place it in bot
    def UpdateVision(self, sourceObjects, mapObjects):
        
        for object in sourceObjects:
            sourceBot = object.GetComp(Bot)
            #do not check visibility whith itself
            if sourceBot == self:
                continue
            
            #straight up create bot's memory record, right now it contains garbage data and is volatile
            curMemory = self.TryCreateMemory(sourceBot)

            #vision checks from CENTER of both owner and source
            trans = self.gameObject.transform
            trans.SynchGlobals()
            sourceTrans = sourceBot.gameObject.transform
            sourceTrans.SynchGlobals()
            #bots are visible if there is no collision with MAP objects, this check ignores other bots
            if not collisions.Raycast.CheckRay(trans, sourceTrans.pos, mapObjects):
                
                if enums.BotDebug.VISION in self.debugFlag:
                    singletons.MainCamera.RenderRawLine(trans.pos, sourceTrans.pos, singletons.DebugPositiveCol, 1)

                curMemory.isInLineOfSight = True

                if self.CheckFieldOfView(sourceTrans.pos):
                    curMemory.lastTimeSensed = time.time()
                    curMemory.sensedPos = sourceTrans.pos.copy()
                    curMemory.lastTimeVisible = time.time()

                    #when source just started being visible
                    if curMemory.isWithinFOV == False:
                        curMemory.isWithinFOV = True
                        curMemory.timeBecameVisible = curMemory.lastTimeSensed #why out of all times this time it is last sensed and not time.time() I have no idea

                else: #when within line of sight, but not wihin fov
                    curMemory.isWithinFOV = False
                    #POSITION OF MEMORY HAS NOT BEEN UPDATED, IT CONTAINS INCORRECT DATA!!!

            else: #when source not in line of sight (then we also sets within fov as failed)
                
                if enums.BotDebug.VISION in self.debugFlag:
                    singletons.MainCamera.RenderRawLine(trans.pos, sourceTrans.pos, singletons.DebugNegativeCol, 1)
                
                curMemory.isInLineOfSight = False
                curMemory.isWithinFOV = False
                #WARNING! IN THIS SCENARIO WE NEVER SETTED UP ANY TIMERS NOR POSITION, SO MEMORY RECORD MAY CONTAIN OUTDATED OR STRAIGHT UP NOT INITIALIZED DATA
                #Also, why do we do this? why do we add object that is not visible and ONLY sets it info that it is not visible, without initializing anything other


    #slightly different than in the book, bot searches for sound triggers, not gets notified by trigger manager (because there is no trigger manager)
    def UpdateHearing(self, soundTriggers, mapObjects):
        
        #actual logic regarding sensory memory located in sound trigger class
        for trigger in soundTriggers:
            trigger.CheckIfTriggered(self.gameObject.GetComp(collisions.Collider), mapObjects)

    #HERE COMES WHOLE AI MUMBO JUMBO (state machine included)


'''this class limits certain bot updates to only happen from time to time'''
class BotUpdateLimiter(events.FPSTimer):
    
    def __init__(self, gameObject, visionLimit, anotherLimit):
        self.gameObject = gameObject
        #self.gameObject.AddComp()

    def UpdateTimer(self):
        self.timer += 1
        if self.timer >= self.threshold:
            self.TimedEvent()
            self.timer = 0