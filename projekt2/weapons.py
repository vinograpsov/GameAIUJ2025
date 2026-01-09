import time
from transforms import *
import game_object
import physics
import collisions
import enums
import singletons
import events
import rendering

class Weapon():

	def __init__(self, owner, cooldown, ammo, damage, projectileSpeed, firingSoundRadius, projectileHitSoundRadius):
		self.gameObject = None
		self.owner = owner
		self.cooldown = cooldown
		self.lastTimeShot = 0
		self.ammo = ammo
		self.projectileSpeed = projectileSpeed
		self.firingSoundRadius = firingSoundRadius
		self.projectileHitSoundRadius = projectileHitSoundRadius

		self.debugFlag = enums.WeaponDebug(0)
		pass

	def TryShoot(self):
		if self.ammo <= 0 or (self.lastTimeShot + self.cooldown) > time.time():
			return False
		self.ammo -= 1
		self.lastTimeShot = time.time()
		return True
		#print("pif paf you have shizofrenia")

	'''debug function'''
	def ShowLinePointer(self, obstacleObjects, botObjects):
		
		#now version for debugging
		trans = self.gameObject.transform
		trans.SynchGlobals()

		#first limit ray to nearest obstacle
		endPoint = collisions.Raycast.CastRay(trans, obstacleObjects)[1]

		#endPoint = trans.Reposition(Vector([8, 0])) #4096
		col = singletons.DebugPositiveCol
		if collisions.Raycast.CheckRay(trans, endPoint, botObjects):
			col = singletons.DebugNegativeCol
		singletons.MainCamera.RenderRawLine(trans.pos, endPoint, col, 1)


class Railgun(Weapon):

	def __init__(self, owner, cooldown, ammo, damage, firingSoundRadius, HitSoundRadius):
		super().__init__(owner, cooldown, ammo, damage, Vector([0, 0]), firingSoundRadius, HitSoundRadius)

	def TryShoot(self, obstacleObjects, botObjects):
		if not super(Railgun, self).TryShoot():
			return False
		#actual railgun logic
		trans = self.gameObject.transform
		trans.SynchGlobals()

		#first limit ray to nearest obstacle
		endPoint = collisions.Raycast.CastRay(trans, obstacleObjects)[1]

		#deal damage to all bots in ray (but not the owner)
		hittedBots = collisions.Raycast.CollectRay(trans, endPoint, botObjects)
		
		for hittedBot in hittedBots:
			if hittedBot == self.owner:
				continue
			hittedBot.DealDamage(self.damage)

		#TO DO
		#make visual clues appear for longer then just one frame
		
		#TO DO change this to be more optimal by using line primitive
		events.SpawnVisualEffect(trans.pos, Vector.ToRotation(endPoint - trans.pos), Vector([Vector.Dist(trans.pos, endPoint), Vector.Dist(trans.pos, endPoint)]), rendering.Model('Assets\Line.obj', [255, 255, 0], enums.RenderMode.WIREFRAME), 0.5)
		#singletons.MainCamera.RenderRawPoint(endPoint, [255, 255, 0], 5)
		#singletons.MainCamera.RenderRawLine(trans.pos, endPoint, [255, 255, 0], 1)

		#TO DO
		#add sound at the weapon's owner (yes, weapon owner, not weapon) origin
		ownerTrans = self.owner.transform
		ownerTrans.SynchGlobals()
		SpawnSound(ownerTrans.pos, self.firingSoundRadius, self.owner)
		#debug sound visibility
		if enums.WeaponDebug.FIRESOUND in self.debugFlag:
			singletons.MainCamera.RenderRawCircle(ownerTrans.pos, singletons.DebugCol, self.firingSoundRadius, 1)
		return True

class RocketLauncher(Weapon):

	def __init__(self, owner, cooldown, ammo, damage, projectileSpeed):
		super().__init__(owner, cooldown, ammo, damage, projectileSpeed)

	def TryShoot(self):
		if not super(RocketLauncher, self).TryShoot():
			return False
		#actual rocket launcher logic
		trans = self.gameObject.transform
		trans.SynchGlobals()
		SpawnProjectile(ExplosiveProjectile(self.owner), trans.pos, trans.rot, Vector([5, 5]), Vector.RotToVect(trans.rot) * self.projectileSpeed)
		#TO DO
		#create temporal visual effect

		#TO DO
		#add sound here
		return True

'''returns fully functional projectile as an object'''
def SpawnProjectile(newProj, pos, rot, scale, initialVelocity):
	object = game_object.GameObject(Transform(pos, rot, scale), [], None)
	object.AddComp(rendering.Primitive(enums.PrimitiveType.SPHERE, [255, 255, 0], 0))
	#okay this is slightly cursed, but it is elegant under the hood (it creates and assignes component to another component in same line)
	projectile = object.AddComp(newProj)
	projectile.collider = object.AddComp(collisions.Collider(enums.ColliderType.SPHERE))

	projectilePhysics = projectile.AddComp(physics.PhysicObject(1))
	projectilePhysics.vel = initialVelocity

	return projectile

class Projectile():
	
	def __init__(self, source): #source is bot that shoot it, not weapon
		self.gameObject = None
		self.source = source
		self.collider = None

	def CheckIfTriggered():
		pass

class ExplosiveProjectile():
	pass

'''this function correctly sets up sound object according to book requirements'''
def SpawnSound(pos, radius, source):
	Sound = game_object.GameObject(Transform(pos, 0, Vector([radius, radius])), [], None)
	Sound.AddComp(collisions.Collider(enums.ColliderType.SPHERE))
	#BOOK REQUIREMENT!!!
	#SOUND MUST BE ACTIVE ONLY DURING ONE FRAME!
	Sound.AddComp(events.DestroyFPSTimer(1))
	triggerComp = Sound.AddComp(events.SoundTrigger(source))
	triggerComp.Start(True)
	return Sound
