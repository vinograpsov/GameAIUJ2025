import math
import random

from transforms import *
import singletons
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
		
		#if low on hp go heal yourself


		#if nothing else from important stuff then wander randomly
		self.bot.ChangeState(WanderState(self.bot))


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

		#other special cases if noticed an enemy or if got hit

		#check if not already at the point, if so then start thinking again
		if self.bot.path.is_finished():
			self.bot.ChangeState(WhatNowState(self.bot))
		pass

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

		pass

class FindHPState(State):

	def OnStateEnter(self):
		#get all hp across map
		pass

	def OnStateUpdate(self):

		#go towards found hp

		#if found hp decide what to do next
		self.bot.ChangeState(WhatNowState(self.bot))

		pass

class FleeState(State):

	def OnStateEnter(self):
		#get nav mesh and find some point away from enemy
		pass

	def OnStateUpdate(self):

		#check if not at the point, if so then repeat this state

		#if no targets in field of view and none of them are remembered then stop fleeing and think
		
		#should flee from all enemies, or only from one of them?
		currentMemories = self.bot.GetValidMemoryRecords(self)
		if len(currentMemories) <= 0:
			self.bot.ChangeState(WhatNowState(self.bot))

class ChaseState(State):

	def OnStateEnter(self):
		pass

	def OnStateUpdate(self):

		#go to place where enemy resides in memory

		#after arrival go little bit more further

		pass

class FightState(State):

	def OnStateEnter(self):
		self.bot.debugFlag = self.bot.debugFlag | enums.BotDebug.LOCKSTATE

		trans = self.gameObject.transform
		trans.SynchGlobals(self)

		self.straifeMult = 2 #straife mult is relevant to object scale
		self.HealthFleeRequirement = 0.4
		self.AmmoThreshold = 4

	def OnStateUpdate(self):
		trans = self.gameObject.transform
		trans.SynchGlobals(self)

		curTarget = self.bot.GetClosestValiableMemory(self)

		#if no target we killed it and proceed to whatever
		if not curTarget:
			self.bot.ChangeState(WhatNowState(self.bot))

		#if target no longer visible that means we need to pursuit
		if not curTarget.isInLineOfSight:
			self.bot.ChangeState(ChaseState(self.bot))
		#here perform check if not need to flee
		if self.bot.health / self.bot.maxHealth < self.HealthFleeRequirement:
			self.bot.ChangeState(FleeState(self.bot))
		if self.bot.weapon.ammo < AmmoThreshold:
			self.bot.ChangeState(FleeState(self.bot))

		#actual fight logic

		#of course try shoot enemy
		self.bot.TryAimAndShoot(singletons.MapObjects)

		straifeEndPoint = Vector([0, self.straifeMult]) #make it random 1 or -1
		straifeEndPoint = trans.LocalToGlobal(straifeEndPoint, False)

		#if there is free space then straife, if no then go towards target
		if not collisions.Raycast.CheckRay(self.gameObject.transform, straifeEndPoint, singletons.MapObjects):
			#as navMesh to go to the side
			pass
		else:
			#ask navMesh to go to target position
			pass


'''fights until dead or kills the target'''
class FightHardState(State):

	def OnStateEnter(self):
		pass

	def OnStateUpdate(self):
		
		curTarget = self.bot.GetClosestValiableMemory(self)

		#if no target we killed it and proceed to whatever
		if not curTarget:
			self.bot.ChangeState(WhatNowState(self.bot))

		self.bot.TryAimAndShoot(singletons.MapObjects)

		#if no longer has ammo then there is no salvation, just give up on life