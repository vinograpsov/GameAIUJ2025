import time
import random

from transforms import *
import game_object
import physics
import collisions
import enums
import singletons
import events
import rendering
import bots

class Weapon():

	def __init__(self, owner, cooldown, ammo, damage, projectileSpeed, projectileScale, firingSoundRadius):
		self.gameObject = None
		self.owner = owner
		self.cooldown = cooldown
		self.lastTimeShot = 0
		self.ammo = ammo
		self.damage = damage
		self.projectileSpeed = projectileSpeed
		self.projectileScale = projectileScale
		self.firingSoundRadius = firingSoundRadius

		self.debugFlag = enums.WeaponDebug(0)
		pass

	def Destroy(self):
		self.owner = None
		#self.owner = None

	def TryShoot(self):
		if self.ammo <= 0 or (self.lastTimeShot + self.cooldown) > time.time():
			return False
		self.ammo -= 1
		self.lastTimeShot = time.time()
		return True
		#print("pif paf you have shizofrenia")

	'''returns rotation that the weapon should be fired at'''
	def Aim(self, target, inaccuracy):
		self.gameObject.transform.SynchGlobals()
		return self.gameObject.transform.rot

	def Debug(self):

		#now version for debugging
		trans = self.gameObject.transform
		trans.SynchGlobals()

		if enums.WeaponDebug.LINEPOINTER in self.debugFlag:

			#first limit ray to nearest obstacle
			endPoint = collisions.Raycast.CastRay(trans, None, singletons.MapObjects)[1]

			#endPoint = trans.Reposition(Vector([8, 0])) #4096
			col = singletons.DebugPositiveCol
			if collisions.Raycast.CheckRay(trans, endPoint, singletons.Bots):
				col = singletons.DebugNegativeCol
			singletons.MainCamera.RenderRawLine(trans.pos, endPoint, col, 1)


class Railgun(Weapon):

	def __init__(self, owner, cooldown, ammo, damage, firingSoundRadius):
		super().__init__(owner, cooldown, ammo, damage, 0, Vector([0, 0]), firingSoundRadius)

	def TryShoot(self, obstacleObjects, botObjects):
		if not super(Railgun, self).TryShoot():
			return False
		#actual railgun logic
		trans = self.gameObject.transform
		trans.SynchGlobals()

		#first limit ray to nearest obstacle
		endPoint = collisions.Raycast.CastRay(trans, None, obstacleObjects)[1]

		#deal damage to all bots in ray (but not the owner)
		hittedObjects = collisions.Raycast.CollectRay(trans, endPoint, botObjects)
		
		for hittedObject in hittedObjects:
			hittedBot = hittedObject.GetComp(bots.Bot)
			if hittedBot:
				if hittedObject == self.owner:
					continue
				hittedBot.DealDamage(self.damage, self.owner)

		#TO DO
		#make visual clues appear for longer then just one frame
		
		#TO DO change this to be more optimal by using line primitive
		events.SpawnVisualEffect(trans.pos, Vector.ToRotation(endPoint - trans.pos), Vector([Vector.Dist(trans.pos, endPoint), Vector.Dist(trans.pos, endPoint)]), rendering.Model('Assets\Line.obj', singletons.ProjectileColor, enums.RenderMode.WIREFRAME), 0.5)

		#TO DO
		#add sound at the weapon's owner (yes, weapon owner, not weapon) origin
		ownerTrans = self.owner.transform
		ownerTrans.SynchGlobals()
		SpawnSound(ownerTrans.pos, self.firingSoundRadius, self.owner)
		#debug sound visibility
		if enums.WeaponDebug.FIRESOUND in self.debugFlag:
			singletons.MainCamera.RenderRawCircle(ownerTrans.pos, singletons.DebugCol, self.firingSoundRadius, 1)
		return True

	def Aim(self, target, inaccuracy):
		ownerTrans = self.owner.transform
		ownerTrans.SynchGlobals()
		targetTrans = target.transform
		targetTrans.SynchGlobals()

		aimRot = (targetTrans.pos - ownerTrans.pos).ToRotation()
		#here add inacurracy
		aimRot += (random.random() * inaccuracy * 2) - inaccuracy
		return aimRot, targetTrans.pos

class RocketLauncher(Weapon):

	def __init__(self, owner, cooldown, ammo, damage, projectileSpeed, projectileScale, firingSoundRadius, blastRadius):
		super().__init__(owner, cooldown, ammo, damage, projectileSpeed, projectileScale, firingSoundRadius)
		self.blastRadius = blastRadius

	def TryShoot(self, obstacleObjects, botObjects):
		if not super(RocketLauncher, self).TryShoot():
			return False
		#actual rocket launcher logic
		trans = self.gameObject.transform
		trans.SynchGlobals()
		ownerTrans = self.owner.transform
		ownerTrans.SynchGlobals()
		#spawn projectile
		newProj = ExplosiveProjectile(self.owner, self.damage, Vector.RotToVect(trans.rot) * 8192, 0.8, self.projectileSpeed, self.blastRadius)
		newRend = rendering.Model('Assets\Rocket.obj', singletons.ProjectileColor, enums.RenderMode.WIREFRAME)
		SpawnProjectile(newProj, newRend, ownerTrans.pos, trans.rot, self.projectileScale, Vector([0, 0]))
		del(newProj)
		del(newRend)

		#add sound

		SpawnSound(ownerTrans.pos, self.firingSoundRadius, self.owner)
		#debug sound visibility
		if enums.WeaponDebug.FIRESOUND in self.debugFlag:
			singletons.MainCamera.RenderRawCircle(ownerTrans.pos, singletons.DebugCol, self.firingSoundRadius, 1)
		return True

	def Aim(self, target, inaccuracy):
		ownerTrans = self.owner.transform
		ownerTrans.SynchGlobals()
		targetTrans = target.transform
		targetTrans.SynchGlobals()

		#predict future target position
		ToEnemy = targetTrans.pos - ownerTrans.pos

		#BOOK DIFFERENT
		#book uses here max speed for target, I use speed as bot's may move at speed lower then max
		LookAheadTime = ToEnemy.Length() / (self.projectileSpeed + target.GetComp(physics.PhysicObject).vel.Length())

		aimPos = targetTrans.pos + self.owner.GetComp(physics.PhysicObject).vel * LookAheadTime
		aimRot = (aimPos - ownerTrans.pos).ToRotation()

		#singletons.MainCamera.RenderRawCircle(aimPos, [0, 255, 0], 5, 1)

		#here add inacurracy
		aimRot += (random.random() * inaccuracy * 2) - inaccuracy
		return aimRot, aimPos

class Projectile(events.Trigger):
	
	def __init__(self, source, damage): #source is bot that shoot it, not weapon
		super().__init__()
		self.source = source
		self.damage = damage
		self.collider = None
		self.physicObject = None

	def Destroy(self):
		singletons.Projectiles.remove(self.gameObject)
		self.source = None
		self.collider = None
		self.physicObject = None

	#unimplemented
	#def TriggeredEvent(self, triggeredObject):
	#	pass

	#unimplemented
	def UpdatePhysics(self):
		pass

#in book rockets have 1.5 reload time and 10 damage (equals along whole explosion radius)
class ExplosiveProjectile(Projectile):

	#max projectile speed is located in physicObject and truncates physics every frame (like in the book)
	def __init__(self, source, damage, targetPos, targetRadius, projectileSpeed, blastRadius):
		super().__init__(source, damage)
		self.projectileSpeed = projectileSpeed
		self.blastRadius = blastRadius
		self.targetPos = targetPos
		self.targetRadius = targetRadius

	def UpdatePhysics(self):
		#BOOK REQUIREMENT
		#this is stupid, every frame we calculate the same value for velocity, we could just only set up this at the start
		self.physicObject.vel = Vector.RotToVect(self.gameObject.transform.rot) * self.projectileSpeed

	#okay, so every trigger works inverse, but this one works normally, ehhhhh
	def CheckIfTriggered(self, botObjects, mapObjects):

		if not self.isActive:
			return False

		hasImpacted = False

		#BOOK REQUIREMENT
		#this function returns incorrect results, because it compares object ORIGINS and not their contact points with ray
		#so if contact with object is far along ray, but it's origin is close, it will prioretize this object against others
		#it would have been extremely easy to fix it by just using normal raycast instead
		trans = self.gameObject.transform
		curPos = trans.pos.copy()
		curLpos = trans.lpos.copy()
		trans.lpos = trans.lpos - self.physicObject.vel
		trans.Desynch()

		botObjectsWithoutSource = botObjects.copy()
		botObjectsWithoutSource.remove(self.source)
		#if I understood this function correctly in the book it retruns closest origin to projectile origin, what in such use case (which is book's use case) will return closest bot to the END of line, not start
		closestObject = collisions.Raycast.GetClosestOriginAlongRay(trans, curPos, curPos, botObjectsWithoutSource)

		#collision with bot
		if (closestObject):
			closestBot = closestObject.GetComp(bots.Bot)

			hasImpacted = True
			#BOOK REQUIREMENT?
			#OR JUST AN OVERSIGHT THAT WE SHOULD NOT FOLLOW?
			#here in the book we send info to bot that has been hit, but just after that we send same info to all bots in area
			#including also closest bot, so closest bot gets damaged 2 times!!!
			closestBot.DealDamage(self.damage, self.source)

			#deal explosion damage
			self.TriggeredEvent(botObjects, mapObjects)

			#BOOK REQUIREMENT?
			#OR JUST AN OVERSIGHT THAT WE SHOULD NOT FOLLOW?
			#here should be return, but it is not present in the book
			#lack of return causes the rocket to explode 2 times in same game tick
			#if it happens to collide with bot and map at the same time



		isMapCollision, mapContactPoint = collisions.Raycast.CastRay(trans, curPos, mapObjects)
		#singletons.MainCamera.RenderRawLine(trans.pos, curPos, singletons.DebugCol, 8)

		trans.lpos = curLpos.copy()
		trans.Desynch()
		del(curPos)
		del(curLpos)

		#collision with map
		if isMapCollision:
			hasImpacted = True

			self.TriggeredEvent(botObjects, mapObjects)
			#BOOK REQUIREMENT
			#setting projectile position to contact point makes sense, but NOT AFTER we already dealt the damage, WTF?
			trans.lpos = mapContactPoint.copy()
			trans.SynchGlobals()

			self.gameObject.Destroy()
			return

		#reached (somwheat) target destination
		targetDiff = trans.pos - self.targetPos
		if Vector.Dot(targetDiff, targetDiff) < self.targetRadius * self.targetRadius:
			hasImpacted = True
			self.TriggeredEvent(botObjects, mapObjects)

		if hasImpacted:
			print("trying to del projectile")
			self.gameObject.Destroy()

	def TriggeredEvent(self, botObjects, mapObjects):
		trans = self.gameObject.transform
		trans.SynchGlobals()

		events.SpawnVisualEffect(trans.pos, 0, Vector([self.blastRadius, self.blastRadius]), rendering.Primitive(enums.PrimitiveType.SPHERE, singletons.ProjectileColor, 1), 0.3)

		for object in botObjects:
			bot = object.GetComp(bots.Bot)
			botTrans = bot.gameObject.transform
			botTrans.SynchGlobals()
			if bot:
				#BOOK REQUIREMENT
				#in the book we only check if inside collider, we do not check line of sight
				#that means explosion deals damage THROUGH WALLS!!!
				#okay, also why in other places we calculate dist^2 to gain performance, but not here???
				if Vector.Dist(trans.pos, botTrans.pos) < self.blastRadius + botTrans.scale.MaxComponent():
					bot.DealDamage(self.damage, self.source) #yes, explosion deals equal damage anywhere in the range

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

'''does not initiates projectile, but sets up new projectile to be fully functional'''
def SpawnProjectile(newProj, newRenderer, pos, rot, scale, initialVelocity):
	object = game_object.GameObject(Transform(pos.copy(), rot, scale.copy()), [], None)
	if newRenderer:
		object.AddComp(newRenderer)
	else:
		object.AddComp(rendering.Primitive(enums.PrimitiveType.SPHERE, singletons.ProjectileColor, 0))
	#okay this is slightly cursed, but it is elegant under the hood (it creates and assignes component to another component in same line)
	projectile = object.AddComp(newProj)
	projectile.collider = object.AddComp(collisions.Collider(enums.ColliderType.SPHERE))

	projectilePhysics = object.AddComp(physics.PhysicObject(1))
	projectilePhysics.vel = initialVelocity
	projectile.physicObject = projectilePhysics

	singletons.Projectiles.append(object)

	return object