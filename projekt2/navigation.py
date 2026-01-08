import pygame 
from transforms import Vector, Transform
import enums
import collisions
import game_object
import rendering 





class GraphNode:
    def __init__(self, position):
        self.pos = position
        self.neighbors = []

        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0


    def addNeighbor(self, node):
        if node not in self.neighbors:
            self.neighbors.append(node)



class NavigationGraph:
    def __init__(self, step_size, bot_radius):
        self.nodes = []
        self.step_size = step_size
        self.bot_radius = bot_radius
        self.node_map = {}

    def _pos_to_key(self, position):
        return (int(round(position.x())), int(round(position.y())))

    def generateFloodFill(self, start_pos, obstacles_list):
        start_time = pygame.time.get_ticks()

        probe_transform = Transform(start_pos, 0 , Vector([self.bot_radius, self.bot_radius]))
        probe_obj = game_object.GameObject(probe_transform, [], None)

        probe_collider = collisions.Collider(enums.ColliderType.SPHERE)
        probe_obj.AddComp(probe_collider)

        open_list = []
        processed_keys = set()

        start_key = self._pos_to_key(start_pos)
        processed_keys.add(start_key)

        open_list.append(start_pos)

        start_node = GraphNode(start_pos)
        self.nodes.append(start_node)
        self.node_map[start_key] = start_node

        directions = [
            Vector([0, 1]),
            Vector([1, 0]),
            Vector([0, -1]),
            Vector([-1, 0]),
            Vector([1, 1]),
            Vector([1, -1]),
            Vector([-1, 1]),
            Vector([-1, -1])
        ]

        while len(open_list) > 0:
            current_pos = open_list.pop(0)
            current_key = self._pos_to_key(current_pos)
            current_node = self.node_map[current_key]

            for direction in directions: 
                next_pos = current_pos + direction * self.step_size
                next_key = self._pos_to_key(next_pos)

                if next_key in self.node_map: 
                    neighbor_node = self.node_map[next_key]
                    current_node.addNeighbor(neighbor_node)
                    neighbor_node.addNeighbor(current_node)
                    continue


                if next_key in processed_keys:
                    continue

                probe_obj.transform.pos = next_pos
                probe_obj.transform.SynchGlobals()

                is_colliding = False

                for obj in obstacles_list:

                    obj_colliders = obj.GetComps(collisions.Collider)
                    # poly_colliders = obj.GetComps(collisions.PolygonCollider)

                    # if poly_colliders:
                    #     obj_colliders.extend(poly_colliders)

                    for other_collider in obj_colliders:
                        if collisions.CollisionSolver.CheckCollision(probe_collider, other_collider):
                            is_colliding = True
                            break

                    if is_colliding:
                        break

                    if not is_colliding: 
                        new_node = GraphNode(next_pos)
                        self.nodes.append(new_node)
                        self.node_map[next_key] = new_node
                        current_node.addNeighbor(new_node)
                        new_node.addNeighbor(current_node)
                        open_list.append(next_pos)
                        processed_keys.add(next_key)
                        print("Node added at", next_pos)

        print(len(self.nodes), "nodes generated in", pygame.time.get_ticks() - start_time, "ms")


    def debugDraw(self, camera):
        surface = pygame.display.get_surface()
        camera_pos = camera.gameObject.transform.pos


        for node in self.nodes:
            start_screen = self._world_to_screen(node.pos, camera)
            pygame.draw.circle(surface, (0, 0, 255), (int(start_screen[0]), int(start_screen[1])), 2)

            for neighbor in node.neighbors: 
                end_screen = self._world_to_screen(neighbor.pos, camera)
                pygame.draw.line(surface, (0, 255, 0), start_screen, end_screen, 1)




    def _world_to_screen(self, world_pos, camera):  
        cam_pivot = camera.gameObject.transform.pos
        win_size = camera.windowSize
    
        screen_x = world_pos.x() - cam_pivot.x() + win_size[0] / 2
        screen_y = win_size[1] - (world_pos.y() - cam_pivot.y() + win_size[1] / 2)
        
        return [screen_x, screen_y]
                                 


class Pathfinder:
    pass