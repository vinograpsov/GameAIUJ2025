import game_object
from transforms import *
import random
import enums
import rendering
import sys

class Bot():

    def __init__(self):
        self.gameObject = None
        self.transform = None

        self.debugFlag = enums.BotDebug(0)


    #this function is used to render debug objects based on the debug flag
    def Debug(self):
        if enums.BotDebug.DIRECTION in self.debugFlag:
            pass

    def DealDamage(self, damage):
        pass

    #HERE COMES WHOLE AI MUMBO JUMBO (state machine included)