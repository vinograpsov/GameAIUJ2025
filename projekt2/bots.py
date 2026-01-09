import game_object
from transforms import *
import random
import enums
import rendering
import sys

class SensoryMemory():

    #BOOK REQUIERMENT!!!
    #EACH BOT CAN BE REGISTERED ONLY **ONCE** IN SENSORY MEMORY
    #THAT MEANS IF ALREADY REGISTERED BOT IS REGISTERED AGAIN IN ANY WAY HE REPLACES EXISTING MEMORY OF ITSELF (WHATEVER THAT WAS)

    def __init__():
        pass

class Bot():

    def __init__(self, maxHealth):
        self.gameObject = None
        self.SensoryMemory = None
        self.maxHealth = maxHealth
        self.health = maxHealth

        self.debugFlag = enums.BotDebug(0)


    #this function is used to render debug objects based on the debug flag
    def Debug(self):
        if enums.BotDebug.DIRECTION in self.debugFlag:
            pass

    def Heal(self, damage):
        self.health = min(self.health + damage, self.maxHealth)

    def DealDamage(self, damage):
        pass

    #HERE COMES WHOLE AI MUMBO JUMBO (state machine included)