import time

import game_object
from transforms import *
import singletons
import enums
import collisions
import rendering

class Timer():

	def __init__(self, threshold):
		self.gameObject = None
		self.threshold = threshold
		singletons.Timers.append(self)

	def Destroy(self):
		singletons.Timers.remove(self)

	def ResetTimer(self):
		pass
	
	def UpdateTimer(self):
		pass

	def TimedEvent(self):
		pass

class FPSTimer(Timer):

	def __init__(self, threshold):
		super().__init__(threshold)
		self.ResetTimer()

	def ResetTimer(self):
		self.timer = 0

	#should fpstimers be incremented after check or before?
	def UpdateTimer(self):
		self.timer += 1
		if self.timer >= self.threshold:
			self.TimedEvent()
			self.timer = 0

class RealtimeTimer(Timer):

	def __init__(self, threshold):
		super().__init__(threshold) 
		self.ResetTimer()

	def ResetTimer(self):
		self.lastTimedEvent = time.time()

	def UpdateTimer(self):
		if time.time() >= self.lastTimedEvent + self.threshold:
			self.TimedEvent()
			self.lastTimedEvent = time.time()

class DestroyFPSTimer(FPSTimer):

	def TimedEvent(self):
		self.gameObject.Destroy()

class DestroyRealtimeTimer(RealtimeTimer):

	def TimedEvent(self):
		self.gameObject.Destroy()

class TriggerRespawnFPSTimer(FPSTimer):

	def TimedEvent(self):
		self.gameObject.GetComp(Trigger).isActive = True
		visual = self.gameObject.GetComp(rendering.RenderObject)
		if visual:
			visual.col = singletons.PickupCol

#BOOK REQUIREMENT!!!
#TRIGGER DOES NOT TRIGGERS ANYTHING, IT IS **BEING** TRIGGERED BY OTHER THINGS,
#TO ACTIVATE TRIGGER ONE MUST REQUEST TO CHECK IF THEY ARE IN TRIGGER'S INFLUANCE
#IN EVERY OTHER GAME INFRASTRUCTURE THE TRIGGER IS RESPONSIBLE FOR TRIGGERING, WHY HERE IT HAS TO BE THE OPPOSITE?!?!
'''trigger requires a collider to work, but it is NOT provided in init'''
class Trigger():

	def __init__(self):
		self.gameObject = None
		self.collider = None
		self.isActive = True
		singletons.Triggers.append(self)

	def Destroy(self):
		singletons.Triggers.remove(self)

	def Start(self, isActive):
		self.collider = self.gameObject.GetComp(collisions.Collider)
		self.isActive = isActive

	def CheckIfTriggered(self, collider):
		if self.isActive and collisions.CollisionSolver.CheckCollision(self.collider, collider):
			self.TriggeredEvent(collider.gameObject)

	def TriggeredEvent(self, triggeredObject):
		pass

#import needs to be here to avoid circular imports
import bots

class PickupTrigger(Trigger):
	def __init__(self):
		super().__init__()
		self.type = None

class HealthPickupTrigger(PickupTrigger):
	def __init__(self, health):
		super().__init__()
		self.type = enums.PickupType.HEALTH
		self.givenHealth = health
		singletons.HealthPickups.append(self)

	def Destroy():
		super().Destroy()
		singletons.HealthPickups.remove(self)

	def TriggeredEvent(self, triggeredObject):
		triggeredBot = triggeredObject.GetComp(bots.Bot)
		if triggeredBot:
				triggeredBot.Heal(self.givenHealth)

				#if trigger has visual cue make it invisible by giving same color as background
				visual = self.gameObject.GetComp(rendering.RenderObject)
				if visual:
					visual.col = singletons.BackgroundCol

				#if trigger has any timers associated reset them
				for timer in triggeredObject.GetComps(Timer):
					timer.ResetTimer()
				self.isActive = False

class AmmoPickupTrigger(PickupTrigger):

	def __init__(self, pickupType, weaponType, ammo): #weaponType is type, ammo is int
		super().__init__()
		self.type = pickupType
		self.weaponType = weaponType
		self.givenAmmo = ammo

	def TriggeredEvent(self, triggeredObject):
		triggeredBot = triggeredObject.GetComp(bots.Bot)
		if triggeredBot:
			if triggeredBot.weapon and isinstance(triggeredBot.weapon, self.weaponType):
				triggeredBot.weapon.ammo += self.givenAmmo
				#if trigger has any timers associated reset them
				for timer in triggeredObject.GetComps(Timer):
					timer.ResetTimer()
				self.isActive = False

class SoundTrigger(Trigger):

	def __init__(self, source): #source is by default bot's object that created the sound
		super().__init__()
		self.source = source
		singletons.Sounds.append(self)

	def Destroy(self):
		super().Destroy()
		singletons.Sounds.remove(self)

	#messy spagghetti code because of inverse way triggers works in book
	def CheckIfTriggered(self, collider, mapObjects):
		if self.isActive and collisions.CollisionSolver.CheckCollision(self.collider, collider):
			self.TriggeredEvent(collider.gameObject, mapObjects)

	def TriggeredEvent(self, triggeredObject, mapObjects):
		triggeredBot = triggeredObject.GetComp(bots.Bot)
		sourceBot = self.source.GetComp(bots.Bot)
		#if triggered object and source have bots
		if triggeredBot and sourceBot:

			trans = self.gameObject.transform
			trans.SynchGlobals()
			triggeredTrans = triggeredObject.transform
			triggeredTrans.SynchGlobals()

			curMemory = triggeredBot.TryCreateMemory(sourceBot)
			
			#WHY
			#WTF
			#why are we checking (and setting) if bot is within line of sight? (sound in real live travel through solid, you know? (especially around objects))
			#and why memory only updates it's position when there is line of sight?!?
			if not collisions.Raycast.CheckRay(trans, triggeredTrans.pos, mapObjects):

				curMemory.isInLineOfSight = True
				curMemory.sensedPos = trans.pos.copy()
			else:
				curMemory.isInLineOfSight = False
		
			curMemory.lastTimeSensed = time.time()


'''visual effect is a rendering object that destroys itself after some time'''
def SpawnVisualEffect(pos, rot, size, renderObject, time):
	Effect = game_object.GameObject(Transform(pos, rot, size), [], None)
	Effect.AddComp(renderObject)
	Effect.AddComp(DestroyRealtimeTimer(time))
	return Effect