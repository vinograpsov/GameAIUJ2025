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

class BotDebug(Flag):
	DIRECTION = auto()
	#(...)

class ProjectileDebug(Flag):
	DIRECTION = auto()
	VELOCITY = auto()
	#(...)
