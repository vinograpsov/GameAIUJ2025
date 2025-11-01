from enum import Enum

class PrimitiveType(Enum):
	LINE = 0
	CIRCLE = 1
	SPHERE = 2

class ColliderType(Enum):
	SPHERE = 0
	BORDER = 1 #border is inverse box, but requires special code
