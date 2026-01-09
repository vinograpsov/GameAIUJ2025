'''this module server purpose to give access to global objects (references) to other modules
(objects declared here are defined in main in start section)'''

MainCamera = None

'''list of objects that require destroying after some time'''
Timers = []