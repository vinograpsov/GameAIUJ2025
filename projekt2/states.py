import math
import random

from transforms import *
import singletons
import enums
import collisions
import bots

class State():

	def __init__(self, bot):
		self.gameObject = None
		self.bot = bot
		self.lockedTarget = None #not sure if will be used

	def Destroy(self):
		self.bot = None

	def OnStateEnter(self):
		pass

	def OnStateUpdate(self):
		pass

	def OnStateExit(self):
		pass

'''does nothing used for debug, mostly for player'''
class NullState(State):
	pass

'''this is the general state that decides what to do if no particular state is ongoing at the time'''
class WhatNowState(State):

	def OnStateEnter(self):
		pass

	def OnStateUpdate(self):

		#if found target proceed to fight
		curTarget = self.bot.GetClosestValiableMemory()
		if curTarget:
			self.bot.ChangeState(FightState(self.bot))
			return

		#if got shot from nowhere look towards the shot

		#if low on hp go heal yourself

		#if nothing else from important stuff then wander randomly
		self.bot.ChangeState(WanderState(self.bot))
		return

'''this state is used when bot is being hit by something while not engaged in a fight'''
class SuprisedState(State):

	def OnStateEnter(self):
		#if you were going somwhere, stop doing it
		self.bot.path = None

	def OnStateUpdate(self):
		#simply look towards from where the shot came from
		pass

		self.bot.ChangeState(WhatNowState(self.bot))
		return

class WanderState(State):

	def OnStateEnter(self):
		trans = self.gameObject.transform
		trans.SynchGlobals()
		#get navMesh and find random spot on the map

		#create random point on the map (for now)
		wanderPoint = Vector([random.random(), random.random()]) * Vector(singletons.MainCamera.windowSize)

		#start going to that point

		self.bot.set_path(singletons.MainPathFinder.create_path_to_position(trans.pos, wanderPoint))

		pass

	def OnStateUpdate(self):

		#TO DO
		#add if got hit

		#if found target proceed to fight
		curTarget = self.bot.GetClosestValiableMemory()
		if curTarget:
			self.bot.ChangeState(FightState(self.bot))
			return

		#check if not already at the point, if so then start thinking again
		if self.bot.path.is_finished():
			self.bot.ChangeState(WhatNowState(self.bot))
			return

	def OnStateExit(self):
		#abandon current path when changing states
		self.bot.path = None

class FindAmmoState(State):

	def OnStateEnter(self):
		#get all ammo across map
		pass

	def OnStateUpdate(self):

		#go towards found ammo

		#if found ammo decide what to do next
		self.bot.ChangeState(WhatNowState(self.bot))
		return

		pass

class FindHPState(State):

	def OnStateEnter(self):
		#get all hp across map
		pass

	def OnStateUpdate(self):

		#go towards found hp

		#if found hp decide what to do next
		self.bot.ChangeState(WhatNowState(self.bot))
		return

		pass

class ChaseState(State):

	def OnStateEnter(self):
		trans = self.gameObject.transform
		trans.SynchGlobals()

		self.ChaseExtensionRange = 1.5 #depends on bot scale

		#POSSIBLE BUG, MAY FOLLOW OTHER BOT NOT ONE RECENTLY ATTACKING
		curTarget = self.bot.GetClosestValiableMemory()

		#if forgot about target do whatever
		if not curTarget:
			self.bot.ChangeState(WhatNowState(self.bot))
			return

		#if target visible proceed to fight
		if curTarget.isInLineOfSight:
			self.bot.ChangeState(FightState(self.bot))
			return
		else:
			futurePath = singletons.MainPathFinder.create_path_to_position(trans.pos, curTarget.sensedPos)

			#if possible set actual endpoint further up towards enemy
			orgPos = trans.lpos
			trans.lpos = futurePath[-1]
			trans.lrot = Vector.ToRotation(futurePath[-1] - orgPos)
			trans.Desynch()
			rayPos = collisions.Raycast.CastRay(trans, trans.LocalToGlobal(Vector([self.ChaseExtensionRange, 0]), False), singletons.MapObjects)[1]
			trans.lpos = orgPos
			trans.Desynch()
			trans.SynchGlobals()

			futurePath = singletons.MainPathFinder.create_path_to_position(trans.pos, rayPos)

			self.bot.set_path(futurePath)

			del futurePath

	def OnStateUpdate(self):

		trans = self.gameObject.transform
		trans.SynchGlobals()

		#POSSIBLE BUG, MAY FOLLOW OTHER BOT NOT ONE RECENTLY ATTACKING
		curTarget = self.bot.GetClosestValiableMemory()

		#if forgot about target do whatever
		if not curTarget:
			self.bot.ChangeState(WhatNowState(self.bot))
			return

		#if target visible proceed to fight
		if curTarget.isInLineOfSight:
			self.bot.ChangeState(FightState(self.bot))
			return

	def OnStateExit(self):
		self.bot.path = None

class FightState(State):

	def OnStateEnter(self):

		trans = self.gameObject.transform
		trans.SynchGlobals()

		self.HealthFleeRequirement = 0.4
		self.AmmoThreshold = 4
		self.straifeMult = 2 #straife mult is relevant to object scale
		self.SwitchStraifeChance = 0.3
		self.StraifeDir = 1
		self.charge = False

	def OnStateUpdate(self):
		trans = self.gameObject.transform
		trans.SynchGlobals()

		curTarget = self.bot.GetClosestValiableMemory()

		#if no target we killed it and proceed to whatever
		if not curTarget:
			self.bot.ChangeState(WhatNowState(self.bot))
			return

		#if target no longer visible that means we need to pursuit
		if not curTarget.isInLineOfSight:
			self.bot.ChangeState(ChaseState(self.bot))
			return
		#here perform check if not need to flee
		if self.bot.health / self.bot.maxHealth < self.HealthFleeRequirement:
			self.bot.ChangeState(FleeState(self.bot))
			return
		if self.bot.weapon.ammo < self.AmmoThreshold:
			self.bot.ChangeState(FleeState(self.bot))
			return

		#actual fight logic

		#of course try shoot enemy
		self.bot.TryAimAndShoot(singletons.MapObjects)
		
		#if not going anywhere straife
		if self.charge or not self.bot.path or self.bot.path.is_finished():
			self.charge = False

			#random chance to straife in different direction
			if random.random() < self.SwitchStraifeChance:
				self.StraifeDir = -self.StraifeDir

			straifeEndPoint = Vector([0, self.straifeMult * self.StraifeDir])
			straifeEndPoint = trans.LocalToGlobal(straifeEndPoint, False)

			#if there is free space then straife, if no then go towards target
			if not collisions.Raycast.CheckRay(self.gameObject.transform, straifeEndPoint, singletons.MapObjects):
				#as navMesh to go to the side
				self.bot.set_path(singletons.MainPathFinder.create_path_to_position(trans.pos, straifeEndPoint))
			elif not self.charge:
				#ask navMesh to go to target position
				self.bot.set_path(singletons.MainPathFinder.create_path_to_position(trans.pos, curTarget.sensedPos))
				self.charge = True

	def OnStateExit(self):
		self.bot.path = None

'''fights until dead or kills the target'''
class FightHardState(State):

	def OnStateEnter(self):
		self.straifeMult = 2 #straife mult is relevant to object scale
		self.SwitchStraifeChance = 0.3
		self.StraifeDir = 1
		self.charge = False

	def OnStateUpdate(self):
		
		curTarget = self.bot.GetClosestValiableMemory(self)

		#if no target we killed it and proceed to whatever
		if not curTarget:
			self.bot.ChangeState(WhatNowState(self.bot))
			return

		#this state does not tries to flee or evade, it just simply fights unless enemy is defeated

		#fight logic, same as during regular fight

		#of course try shoot enemy
		self.bot.TryAimAndShoot(singletons.MapObjects)
		
		#if not going anywhere straife
		if self.charge or not self.bot.path or self.bot.path.is_finished():
			self.charge = False

			#random chance to straife in different direction
			if random.random() < self.SwitchStraifeChance:
				self.StraifeDir = -self.StraifeDir

			straifeEndPoint = Vector([0, self.straifeMult * self.StraifeDir])
			straifeEndPoint = trans.LocalToGlobal(straifeEndPoint, False)

			#if there is free space then straife, if no then go towards target
			if not collisions.Raycast.CheckRay(self.gameObject.transform, straifeEndPoint, singletons.MapObjects):
				#as navMesh to go to the side
				self.bot.set_path(singletons.MainPathFinder.create_path_to_position(trans.pos, straifeEndPoint))
			elif not self.charge:
				#ask navMesh to go to target position
				self.bot.set_path(singletons.MainPathFinder.create_path_to_position(trans.pos, curTarget.sensedPos))
				self.charge = True


class FleeState(State):

	def OnStateEnter(self):
		#get nav mesh and find some point away from enemy
		trans = self.gameObject.transform
		trans.SynchGlobals()

		#this is used to determine if candidate path is "safe" safe paths are ones that do not go near enemy
		self.coverPenetration = 1.2 * trans.scale.MaxComponent() #scales with bot scale
		self.minEscapeDit = 2 * trans.scale.MaxComponent() # scales with bot scale
		self.enemySafeDist = 0.7
		self.candidatePathDistribution = math.pi / 4

		#create candidate path 

		curTarget = self.bot.GetClosestValiableMemory()
		#this technically should never happen but you never know
		if not curTarget:
			self.bot.ChangeState(WhatNowState(self.bot))
			return

		#search for cover left or right from enemy
		pivotTrans = Transform(curTarget.sensedPos.copy, Vector.ToRotation(trans.pos - curTarget.sensedPos), trans.scale.copy())

		#direction of first check chosen at random
		candidateCoverDir = 1
		if bool(random.getrandbits(1)):
			candidateCoverDir = -1
		pivotTrans.lrot = pivotTrans.lrot + self.candidatePathDistribution * candidateCoverDir
		pivotTrans.Desynch()
		
		#create first candidate cover
		coverPos = collisions.Raycast.CastRay(pivotTrans, None, singletons.MapObjects)[1]

		coverPos += pivotTrans.Forward() * coverPenetration

		#check if path to candidate cover is long enough and does not passes near enemy
		#candidatePath = singletons.MainPathFinder.create_path_to_position(trans.pos, coverPos)
		#if Vector.Distance(trans.pos, candidatePath[-1]) > self.minEscapeDist:
		#	for waypoint in candidatePath:
		#		if 



	def OnStateUpdate(self):

		#check if not at the point, if so then repeat this state

		#if no targets in field of view and none of them are remembered then stop fleeing and think
		
		#should flee from all enemies, or only from one of them?
		curTarget = self.bot.GetClosestValiableMemory()
		if not curTarget:
			self.bot.ChangeState(WhatNowState(self.bot))
			return
		else:
			#fight back, bot can still fight when fleeing
			pass

'''unused old flee state

class FleeState(State):

	def OnStateEnter(self):
		#get nav mesh and find some point away from enemy
		trans = self.gameObject.transform
		trans.SynchGlobals()

		#this is used to determine if candidate path is "safe" safe paths are ones that do not go near enemy
		self.coverPenetration = 1.2 * trans.scale.MaxComponent() #scales with bot scale
		self.minEscapeDit = 2 * trans.scale.MaxComponent() # scales with bot scale
		self.enemySafeDist = 0.7
		self.candidatePathDistribution = math.pi / 4

		#create candidate path 

		curTarget = self.bot.GetClosestValiableMemory()
		#this technically should never happen but you never know
		if not curTarget:
			self.bot.ChangeState(WhatNowState(self.bot))
			return

		#search for cover left or right from enemy
		pivotTrans = Transform(curTarget.sensedPos.copy, Vector.ToRotation(trans.pos - curTarget.sensedPos), trans.scale.copy())

		#direction of first check chosen at random
		candidateCoverDir = 1
		if bool(random.getrandbits(1)):
			candidateCoverDir = -1
		pivotTrans.lrot = pivotTrans.lrot + self.candidatePathDistribution * candidateCoverDir
		pivotTrans.Desynch()
		
		#create first candidate cover
		coverPos = collisions.Raycast.CastRay(pivotTrans, None, singletons.MapObjects)[1]

		coverPos += pivotTrans.Forward() * coverPenetration

		#check if path to candidate cover is long enough and does not passes near enemy
		candidatePath = singletons.MainPathFinder.create_path_to_position(trans.pos, coverPos)
		if Vector.Distance(trans.pos, candidatePath[-1]) > self.minEscapeDist:
			for waypoint in candidatePath:
				if 


'''