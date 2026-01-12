'''this module server purpose to give access to global objects (references) to other modules
(objects declared here are defined in main in start section)'''

MainCamera = None

GeneralDebugFlag = None

ProjectileColor = [255, 255, 0]

DebugCol = [255, 0, 255]
DebugNegativeCol = [255, 0, 153]
DebugPositiveCol = [153, 0, 255]

'''list off all game objects existing in program'''
GlobalObjects = [] #game objects

'''objects with a component for rendering'''
RenderObjects = [] #render object class

'''list of map objects'''
MapObjects = []

'''list of objects that require destroying after some time'''
Timers = []

'''list of triggers'''
Triggers = []

'''list of sound triggers'''
Sounds = [] #sound trigger component

'''list of bot objects'''
Bots = [] #gameobject