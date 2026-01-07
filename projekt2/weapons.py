from datetime import time
from transforms import *
import physics
import collisions
import rendering

class Weapon():

	def __init__(self, cooldown, ammo):
		self.gameObject = None
		self.cooldown = cooldown
		self.lastTimeShot = 0
		self.ammo = ammo
		#self.canShoot = True
		pass

	def TryShoot(self):
		if self.ammo <= 0 and self.lastTimeShot + self.cooldown < datetime.datetime.now:
			return False
		self.ammo -= 1
		self.lastTimeShot = datetime.datetime.now
		print("pif paf you have shizofrenia")


class Railgun(Weapon):

	#it also has raw line renderer and
	def __init__(self, cooldown, ammo):
		super().__init__(cooldown, ammo)

	def TryShoot(self):
		return super(Railgun, self).TryShoot()

	def ShowLinePointer(self, Camera, sceneObjects):
		
		#now version for debugging
		trans = self.gameObject.transform
		trans.SynchGlobals()
		endPoint = trans.Reposition(Vector([8, 0])) #4096
		col = [255, 0, 0]
		if collisions.Raycast.CheckRay(trans, endPoint, sceneObjects):
			col = [0, 255, 0]
		Camera.RenderRawLine(trans.pos, endPoint, col, 1)


class ExplosiveProjectile():
	pass