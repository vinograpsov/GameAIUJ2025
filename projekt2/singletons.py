'''this module server purpose to give access to global objects (references) to other modules
(objects declared here are defined in main in start section)'''

MainCamera = None

DebugCol = [255, 0, 255]
DebugNegativeCol = [153, 0, 255]
DebugPositiveCol = [255, 0, 153]

'''objects with a component for rendering'''
RenderObjects = []

'''list of objects that require destroying after some time'''
Timers = []

'''list of triggers'''
Triggers = []