import time
import math #used only in one line, in FOV check

import game_object
from transforms import *
import singletons
import random
import enums
import rendering
import sys
from navigation import Path 
import physics
import pickup
import pygame
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

    def __init__(self, maxHealth, memorySpan, fov, rocket_ammo=10, railgun_ammo=10):
        self.gameObject = None
        self.memories = [] #list of memory records
        self.memorySpan = memorySpan
        self.maxHealth = maxHealth
        self.health = maxHealth
        self.rocket_ammo = rocket_ammo
        self.railgun_ammo = railgun_ammo


        self.path = None
        self.waypoint_seek_dist_sq = 20 * 20 
        self.max_speed = 2.0 
        self.velocity = Vector([0, 0]) 
        self.mass = 1.0
        self.fov = fov

        self.debugFlag = enums.BotDebug(0)

        self.transform = None

    def set_path(self, vector_list): 
        self.path = Path(vector_list)

    def seek(self, target_pos):
        desired_velocity = (target_pos - self.transform.pos).Normalize() * self.max_speed
        return desired_velocity - self.velocity 


    def arrive(self, target_pos, deceleration=3.0):
        to_target = target_pos - self.transform.pos
        dist = to_target.Length()
        if dist > 0:
            speed = dist / deceleration
            speed = min(speed, self.max_speed)
            desired_velocity = to_target * (speed / dist)
            return desired_velocity - self.velocity
        
        return Vector([0, 0])
    

    def follow_path(self):
        if self.path is None or not self.path.waypoints: 
            return Vector([0, 0])
        
        current_target = self.path.current_waypoint()
        dist_sq = (current_target - self.transform.pos).LengthSquared()

        if dist_sq < self.waypoint_seek_dist_sq:
            self.path.set_next_waypoint()
        
        if not self.path.is_finished():
            return self.seek(self.path.current_waypoint())
        else:
            return self.arrive(self.path.current_waypoint())
        

    def update(self):

        if self.gameObject is None:
            return
        
        if self.transform is None:
            self.transform = self.gameObject.transform

        phys_comp = self.gameObject.GetComp(physics.PhysicObject)
        if phys_comp is None:
            return

        steering_force = self.follow_path()
        acceleration = steering_force / self.mass 
        phys_comp.vel += acceleration

        if phys_comp.vel.LengthSquared() > self.max_speed**2:
            phys_comp.vel = phys_comp.vel.Normalize() * self.max_speed

        if phys_comp.vel.LengthSquared() > 0.001:
            self.transform.FaceTowards(self.transform.pos + phys_comp.vel)


    def add_ammo(self, weapon_type, amount):
        if weapon_type == pickup.PickupType.AMMO_ROCKET:
            self.rocket_ammo += amount
        elif weapon_type == pickup.PickupType.AMMO_RAILGUN:
            self.railgun_ammo += amount

    def add_health(self, amount):
        self.health = min(self.health + amount, self.maxHealth)


    def toggle_debug_path(self):
        if enums.BotDebug.PATH in self.debugFlag:
            self.debugFlag &= ~enums.BotDebug.PATH
        else:
            self.debugFlag |= enums.BotDebug.PATH
        print(f"Bot Path Debug: {self.debugFlag}")



    def _world_to_screen(self, world_pos, camera):
        cam_pivot = camera.gameObject.transform.pos
        win_size = camera.windowSize
        screen_x = world_pos.x() - cam_pivot.x() + win_size[0] / 2
        screen_y = win_size[1] - (world_pos.y() - cam_pivot.y() + win_size[1] / 2)
        return [screen_x, screen_y]
    

    #this function is used to render debug objects based on the debug flag
    def Debug(self, camera):
        surface = pygame.display.get_surface()
        trans = self.gameObject.transform
        trans.SynchGlobals()


        if enums.BotDebug.DIRECTION in self.debugFlag:
            start_pos = self._world_to_screen(self.transform.pos, camera)
            end_pos = self._world_to_screen(self.transform.pos + self.transform.Forward() * 30, camera)
            pygame.draw.line(surface, (255,0,0), start_pos, end_pos, 2)

        if self.path and self.path.waypoints and enums.BotDebug.PATH in self.debugFlag:
            screen_points = [] 
            screen_points.append(self._world_to_screen(self.transform.pos, camera))

            for i in range(self.path.cur_waypoint_idx, len(self.path.waypoints)):
                screen_points.append(self._world_to_screen(self.path.waypoints[i], camera))
            
            if len(screen_points) > 1: 
                pygame.draw.lines(surface, (255,255,255), False, screen_points, 2)

                for p in screen_points: 
                    pygame.draw.circle(surface, (255,255,255), (int(p[0]), int(p[1])), 5)


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


    def Heal(self, damage):
        self.health = min(self.health + damage, self.maxHealth)

    def DealDamage(self, damage):
        pass

    '''returns true if given point is within field of view, FOV is always set to 90deg'''
    def CheckFieldOfView(self, point):
        trans = self.gameObject.transform
        trans.SynchGlobals()

        facingDir = Vector.RotToVect(trans.rot)

        if Vector.Dot(facingDir, (point - trans.pos).Normalize()) >= math.cos(self.fov / 2.0):
            return True
        return False

    #SENSORY MEMORY
    
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
            #do not check visibility whit itself
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