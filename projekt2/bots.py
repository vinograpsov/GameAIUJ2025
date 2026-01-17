import game_object
from transforms import *
import random
import enums
import rendering
import sys
from navigation import Path 
import physics
import pickup
import pygame

class Bot():

    def __init__(self, maxHealth, rocket_ammo=10, railgun_ammo=10):
        self.gameObject = None
        self.transform = None
        self.maxHealth = maxHealth
        self.health = maxHealth
        self.rocket_ammo = rocket_ammo
        self.railgun_ammo = railgun_ammo


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


    def add_ammo(self, weapon_type, amount):
        if weapon_type == pickup.PickupType.AMMO_ROCKET:
            self.rocket_ammo += amount
        elif weapon_type == pickup.PickupType.AMMO_RAILGUN:
            self.railgun_ammo += amount

    def add_health(self, amount):
        self.health = min(self.health + amount, self.maxHealth)


    def toggle_debug_path(self):
        if enums.BotDebug.PATH in self.debugFlag:
            self.debugFlag &= ~enums.BotDebug.PATH
        else:
            self.debugFlag |= enums.BotDebug.PATH
        print(f"Bot Path Debug: {self.debugFlag}")



    def _world_to_screen(self, world_pos, camera):
        cam_pivot = camera.gameObject.transform.pos
        win_size = camera.windowSize
        screen_x = world_pos.x() - cam_pivot.x() + win_size[0] / 2
        screen_y = win_size[1] - (world_pos.y() - cam_pivot.y() + win_size[1] / 2)
        return [screen_x, screen_y]
    

    #this function is used to render debug objects based on the debug flag
    def Debug(self, camera):
        surface = pygame.display.get_surface()

        if enums.BotDebug.DIRECTION in self.debugFlag:
            start_pos = self._world_to_screen(self.transform.pos, camera)
            end_pos = self._world_to_screen(self.transform.pos + self.transform.Forward() * 30, camera)
            pygame.draw.line(surface, (255,0,0), start_pos, end_pos, 2)



        if self.path and self.path.waypoints and enums.BotDebug.PATH:
            screen_points = [] 
            screen_points.append(self._world_to_screen(self.transform.pos, camera))

            for i in range(self.path.cur_waypoint_idx, len(self.path.waypoints)):
                screen_points.append(self._world_to_screen(self.path.waypoints[i], camera))
            
            if len(screen_points) > 1: 
                pygame.draw.lines(surface, (255,255,255), False, screen_points, 2)

                for p in screen_points: 
                    pygame.draw.circle(surface, (255,255,255), (int(p[0]), int(p[1])), 5)


    def Heal(self, damage):
        self.health = min(self.health + damage, self.maxHealth)

    def DealDamage(self, damage):
        pass

    #HERE COMES WHOLE AI MUMBO JUMBO (state machine included)