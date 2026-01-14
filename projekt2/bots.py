import game_object
from transforms import *
import random
import enums
import rendering
import sys
from navigation import Path 
import physics

class Bot():

    def __init__(self, maxHealth):
        self.gameObject = None
        self.transform = None
        self.maxHealth = maxHealth
        self.health = maxHealth

        self.path = None
        self.waypoint_seek_dist_sq = 20 * 20 
        self.max_speed = 2.0 
        self.velocity = Vector([0, 0]) 
        self.mass = 1.0

        self.debugFlag = enums.BotDebug(0)

    def set_path(self, vector_list): 
        self.path = Path(vector_list)

    def seek(self, target_pos):
        desired_velocity = (target_pos - self.transform.pos).Normalize() * self.max_speed
        return desired_velocity - self.velocity 


    def arrive(self, target_pos, deceleration=3.0):
        to_target = target_pos - self.transform.pos
        dist = to_target.Length()
        if dist > 0:
            speed = dist / deceleration
            speed = min(speed, self.max_speed)
            desired_velocity = to_target * (speed / dist)
            return desired_velocity - self.velocity
        
        return Vector([0, 0])
    

    def follow_path(self):
        if self.path is None or not self.path.waypoints: 
            return Vector([0, 0])
        
        current_target = self.path.current_waypoint()
        dist_sq = (current_target - self.transform.pos).LengthSquared()

        if dist_sq < self.waypoint_seek_dist_sq:
            self.path.set_next_waypoint()
        
        if not self.path.is_finished():
            return self.seek(self.path.current_waypoint())
        else:
            return self.arrive(self.path.current_waypoint())
        

    def update(self):

        if self.gameObject is None:
            return
        
        if self.transform is None:
            self.transform = self.gameObject.transform

        phys_comp = self.gameObject.GetComp(physics.PhysicObject)
        if phys_comp is None:
            return

        steering_force = self.follow_path()
        acceleration = steering_force / self.mass 
        phys_comp.vel += acceleration

        if phys_comp.vel.LengthSquared() > self.max_speed**2:
            phys_comp.vel = phys_comp.vel.Normalize() * self.max_speed

        if phys_comp.vel.LengthSquared() > 0.001:
            self.transform.FaceTowards(self.transform.pos + phys_comp.vel)














    #this function is used to render debug objects based on the debug flag
    def Debug(self):
        if enums.BotDebug.DIRECTION in self.debugFlag:
            pass

    def Heal(self, damage):
        self.health = min(self.health + damage, self.maxHealth)

    def DealDamage(self, damage):
        pass

    #HERE COMES WHOLE AI MUMBO JUMBO (state machine included)