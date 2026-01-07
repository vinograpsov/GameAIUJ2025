import time
from transforms import *
import game_object
import physics
import collisions
import rendering

class Weapon():

	def __init__(self, owner, cooldown, ammo, damage, projectileSpeed):
		self.gameObject = None
		self.owner = owner
		self.cooldown = cooldown
		self.lastTimeShot = 0
		self.ammo = ammo
		self.projectileSpeed = projectileSpeed
		pass

	def TryShoot(self):
		if self.ammo <= 0 or (self.lastTimeShot + self.cooldown) > time.time():
			return False
		self.ammo -= 1
		self.lastTimeShot = time.time()
		return True
		#print("pif paf you have shizofrenia")


class Railgun(Weapon):

	def __init__(self, owner, cooldown, ammo, damage):
		super().__init__(owner, cooldown, ammo, damage, Vector([0, 0]))

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
		#create temporal visual effect
		
		rendering.MainCamera.RenderRawPoint(endPoint, [192, 192, 0], 5)
		rendering.MainCamera.RenderRawLine(trans.pos, endPoint, [192, 192, 0], 1)

		#TO DO
		#add sound here
		return True

	def ShowLinePointer(self, obstacleObjects, botObjects):
		
		#now version for debugging
		trans = self.gameObject.transform
		trans.SynchGlobals()

		#first limit ray to nearest obstacle
		endPoint = collisions.Raycast.CastRay(trans, obstacleObjects)[1]

		#endPoint = trans.Reposition(Vector([8, 0])) #4096
		col = [255, 0, 0]
		if collisions.Raycast.CheckRay(trans, endPoint, obstacleObjects):
			col = [0, 255, 0]
		rendering.MainCamera.RenderRawLine(trans.pos, endPoint, col, 1)

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

class Signal():
	pass

'''explosion is a type of signal that deals damage to bots'''
class Explosion(Signal):
	pass

'''sound is type of signal that gets registered in bots sensory memory'''
class Sound(Signal):
	pass