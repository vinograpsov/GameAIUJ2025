from enum import Enum
from enum import Flag, auto

class RenderMode(Enum):
	VERTICES = 0
	WIREFRAME = 1
	POLYGON = 2

class PrimitiveType(Enum):
	LINE = 0
	CIRCLE = 1
	SPHERE = 2

class ColliderType(Enum):
	EMPTY = 0
	SPHERE = 1
	LINE = 2 #border is inverse box, but requires special code
	POLYGON = 3 #polygon is in reality a container of line colliders

class PickupType(Enum):
    HEALTH = 1
    AMMO_RAILGUN = 2
    AMMO_ROCKET = 3

class GeneralDebug(Flag):
	SPAWNPLAYER = auto() #player is bot controlled by player input
	SPAWNDUMMY = auto() #dummy is bot that is not acting

class BotDebug(Flag):
	PATH = auto()
	DIRECTION = auto() #unused
	FIELDOFVIEW = auto() #unused
	VISION = auto()
	MEMORYPOSITIONS = auto()
	HEALTH = auto()
	LOCKSTATE = auto() #this one is special, it will prevent any states from changing
	SHOWSTATE = auto()
	#(...)

class WeaponDebug(Flag):
	LINEPOINTER = auto()
	FIRESOUND = auto()
	HITSOUND = auto()

class ProjectileDebug(Flag):
	DIRECTION = auto()
	VELOCITY = auto()
	#(...)
