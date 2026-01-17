import enums 
import collisions 
from transforms import Vector 
import rendering 
import game_object


class PickupType(enums.Enum):
    HEALTH = 1
    AMMO_RAILGUN = 2
    AMMO_ROCKET = 3


class Pickup:
    def __init__(self, pickup_type, amaout, respawn_delay=5.0, debugFlag=0):
        self.gameObject = None 
        self.type = pickup_type
        self.amount = amaout
        self.respawn_delay = respawn_delay
        self.is_active = True
        self.time_until_respawn = 0.0
        self.radius_sq = 15*15

        self.debugFlag = debugFlag 

    def update(self, delta_time):
        if not self.is_active:
            self.time_until_respawn -= delta_time
            if self.time_until_respawn <= 0.0:
                self.respawn()

    def respawn(self):
        self.is_active = True
        self.time_until_respawn = 0.0
        self.gameObject.GetComp(rendering.Primitive).enabled = True


    def Collect(self, bot):
        if not self.is_active: 
            return False 
        
        if self.type == PickupType.HEALTH:
            bot.add_health(self.amount)

        else: 
            bot.add_ammo(self.type, self.amount)

        if self.debugFlag:
            print(f"Pickup collected: {self.type}, amount: {self.amount}") 

    def deactivate(self):
        self.active = False 
        self.time_until_respawn = self.respawn_delay
        self.gameObject.GetComp(rendering.Primitive).enabled = False

        