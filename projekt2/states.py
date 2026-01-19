import math

from transforms import *
import singletons
import collisions
import bots

class State():

	def __init__(self, bot):
		self.bot = bot
		self.lockedTarget = None #not sure if will be used

	def Destroy():
		self.bot = None

	def OnStateEnter():
		pass

	def OnStateUpdate():
		pass

	def OnStateExit():
		pass


'''this is the general state that decides what to do if no particular state is ongoing at the time'''
class WhatNowState(State):
	pass

class WanderState(State):

	def OnStateEnter():
		#get navMesh and find random spot on the map
		#start going to that point
		pass

	def OnStateUpdate():

		#other special cases if noticed an enemy or if got hit

		#check if not already at the point, if so then start thinking again
		pass

class FleeState(State):

	def OnStateEnter():
		#get nav mesh and find some point away from enemy
		pass

	def OnStateUpdate():

		#check if not at the point, if so then repeat this state

		#if no targets in field of view and none of them are remembered then stop fleeing and think
		
		#should flee from all enemies, or only from one of them?
		currentMemories = self.bot.GetValidMemoryRecords()
		if len(currentMemories) <= 0:
			self.bot.ChangeState(WhatNowState(self.bot))

class ChaseState(Satte):

	def OnStateEnter():
		pass

	def OnStateUpdate():
		pass

class FightState(State):

	def OnStateEnter():
		trans = self.gameObject.transform
		trans.SynchGlobals()

		self.straifeMult = 2 #straife mult is relevant to object scale
		self.HealthFleeRequirement = 0.4
		self.AmmoThreshold = 4

	def OnStateUpdate():
		trans = self.gameObject.transform
		trans.SynchGlobals()

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

class FightHardState(State):

	def OnStateEnter():
		pass

	def OnStateUpdate():
		pass