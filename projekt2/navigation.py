import pygame 
from transforms import Vector, Transform
import enums
import collisions
import game_object
import events
import rendering 
import heapq 


class GraphNode:
    def __init__(self, position):
        self.pos = position
        self.neighbors = []
        self.parent = None

        self.g = 0
        self.h = 0
        self.f = 0

        self.extra_info = None


    def addNeighbor(self, node):
        if node not in self.neighbors:
            self.neighbors.append(node)

    def __lt__(self, other):
        return self.f < other.f

class NavigationGraph:
    def __init__(self, step_size, bot_radius, MAX_WIDTH = 800, MAX_HEIGHT = 600, MARGIN = 20):
        self.nodes = []
        self.step_size = step_size
        self.bot_radius = bot_radius
        self.node_map = {}
        self.MAX_WIDTH = MAX_WIDTH
        self.MAX_HEIGHT = MAX_HEIGHT
        self.MARGIN = MARGIN

        self.show_debug = False

    def toggle_debug(self):
        self.show_debug = not self.show_debug
        print(f"Navigation Graph Debug: {self.show_debug}")

    def _pos_to_key(self, position):
        return (int(round(position.x())), int(round(position.y())))

    def register_pickup(self, pickup_obj):
        min_dist = float('inf')
        closest_node = None

        for node in self.nodes:
            dist = (node.pos - pickup_obj.transform.pos).LengthSquared()
            if dist < min_dist:
                min_dist = dist
                closest_node = node

        if closest_node and min_dist < (self.step_size * self.step_size):
            closest_node.extra_info = pickup_obj 
            # !!!!!!!!!!!!!!! pickup_obj.transform.pos = closest_node.pos
            #Show to adam and ask if this is ok
            pickup_obj.transform.lpos = closest_node.pos
            pickup_obj.transform.Desynch()
            print(f"Pickup registered to node at {closest_node.pos.data}")

    def generateFloodFill(self, start_pos, obstacles_list):
        start_time = pygame.time.get_ticks()

        # probe_transform = Transform(start_pos, 0 , Vector([self.bot_radius, self.bot_radius]))
        # probe_obj = game_object.GameObject(probe_transform, [], None)
        # probe_collider = collisions.Collider(enums.ColliderType.SPHERE)
        # probe_obj.AddComp(probe_collider)

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

        safe_radius_sq = (self.bot_radius * 1.5) ** 2

        while len(open_list) > 0:
            current_pos = open_list.pop(0)
            current_key = self._pos_to_key(current_pos)
            current_node = self.node_map[current_key]

            if current_key not in self.node_map:
                continue

            for direction in directions: 
                next_pos = current_pos + direction * self.step_size
                next_key = self._pos_to_key(next_pos)

                # if (next_pos.x() < self.MARGIN or next_pos.x() > self.MAX_WIDTH - self.MARGIN or 
                #     next_pos.y() < self.MARGIN or next_pos.y() > self.MAX_HEIGHT - self.MARGIN):
                #     continue

                if next_key in self.node_map: 
                    neighbor_node = self.node_map[next_key]
                    current_node.addNeighbor(neighbor_node)
                    neighbor_node.addNeighbor(current_node)
                    continue


                if next_key in processed_keys:
                    continue
                
                processed_keys.add(next_key)
                # probe_obj.transform.pos = next_pos
                # probe_obj.transform.SynchGlobals()

                is_colliding = False

                for obj in obstacles_list:

                    obj_colliders = obj.GetComps(collisions.Collider)
                    poly_colliders = obj.GetComps(collisions.PolygonCollider)
                    if poly_colliders:
                        obj_colliders.extend(poly_colliders)


                    for collider in obj_colliders:
                        collider_trans = collider.gameObject.transform
                        collider_trans.SynchGlobals()

                        if collider.type == enums.ColliderType.POLYGON:
                            for connection in collider.edges: 
                                p1 = collider_trans.Reposition(Vector(collider.verts[connection[0] - 1]))
                                p2 = collider_trans.Reposition(Vector(collider.verts[connection[1] - 1]))

                                if collisions.CollisionSolver.LineIntersection2DCheck(current_pos, next_pos, p1, p2):
                                    is_colliding = True
                                    break

                                dist_sq = collisions.CollisionSolver.LinePointDistSquared(p1, p2, next_pos)
                                if dist_sq < safe_radius_sq:
                                    is_colliding = True
                                    break


                        elif collider.type == enums.ColliderType.SPHERE:
                            dist_to_sphere = (collider_trans.pos - next_pos).LengthSquared()
                            min_dist = (collider_trans.scale.MaxComponent() + self.bot_radius) ** 2
                            # if collisions.CollisionSolver.LineSphereIntersectionCheck(current_pos, next_pos, collider_trans.pos, collider_trans.scale.MaxComponent()):
                            if dist_to_sphere < min_dist:
                                is_colliding = True
                                break

                    if is_colliding:
                        break 

                if not is_colliding: 
                    # processed_keys.add(next_key)
                    new_node = GraphNode(next_pos)
                    self.nodes.append(new_node)
                    self.node_map[next_key] = new_node
                    current_node.addNeighbor(new_node)
                    new_node.addNeighbor(current_node)
                    open_list.append(next_pos)
                    print("Node added at", next_pos.x(), " ", next_pos.y())

        print(len(self.nodes), "nodes generated in", pygame.time.get_ticks() - start_time, "ms")


    def debugDraw(self, camera):

        if not self.show_debug:
            return 

        surface = pygame.display.get_surface()

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
                                 

class DijkstraSearch:
    def __init__(self, start_node, target_node_type):
        self.start_node = start_node
        self.target_node_type = target_node_type

        self.open_list = []
        self.closed_set = set()

        self.start_node.parent = None
        self.start_node.g = 0
        self.start_node.f = 0

        heapq.heappush(self.open_list, start_node)
        self.target_node_found = None 

    def run(self):
        import pickup 

        while len(self.open_list) > 0: 
            current_node = heapq.heappop(self.open_list)
            self.closed_set.add(current_node) 

            if current_node.extra_info is not None:
                pickup_comp = current_node.extra_info.GetComp(events.PickupTrigger)
                if pickup_comp and pickup_comp.isActive and pickup_comp.type == self.target_node_type:
                    self.target_node_found = current_node 
                    return True
                #pickup_comp = current_node.extra_info.GetComp(pickup.Pickup)
                #if pickup_comp and pickup_comp.is_active and pickup_comp.type == self.target_node_type:
                #    self.target_node_found = current_node 
                #    return True

            for neighbor in current_node.neighbors: 
                if neighbor in self.closed_set: 
                    continue

                dist_to_neighbor = (current_node.pos - neighbor.pos).Length()
                tentative_g = current_node.g + dist_to_neighbor

                in_open_list = neighbor in self.open_list

                if tentative_g < neighbor.g or not in_open_list:
                    neighbor.parent = current_node
                    neighbor.g = tentative_g 
                    neighbor.f = tentative_g

                    if not in_open_list:
                        heapq.heappush(self.open_list, neighbor)
                    else: 
                        heapq.heappush(self.open_list, neighbor)

        return False


    def get_path_as_vectors(self):
        if not self.target_node_found:
            return[]
        
        SAFETY_COUNTER = 0
        MAX_LOOPS = 1000

        path = []
        curr = self.target_node_found
        while curr is not None: 
            path.append(curr.pos)
            curr = curr.parent
            if curr == self.start_node:
                break 
            
            SAFETY_COUNTER += 1
            if SAFETY_COUNTER > MAX_LOOPS:
                print("Infinite loop detected")
                break
            
        path.reverse()
        return path

class AStarSearch: 
    def __init__(self, start_node, target_node):
        self.start_node = start_node
        self.target_node = target_node

        self.open_list = []
        self.closed_set = set()
        self.came_from = {}

        self.start_node.parent = None

        start_node.g = 0
        start_node.h = self._heuristic(start_node.pos, target_node.pos)
        start_node.f = start_node.g + start_node.h

        heapq.heappush(self.open_list, start_node)
        self.path_found = False 

    def _heuristic(self, pos1, pos2):
        diff = pos1 - pos2
        return diff.Length()
    
    def run(self):
        while len(self.open_list) > 0: 
            current_node = heapq.heappop(self.open_list)

            if current_node == self.target_node:
                self.path_found = True 
                return True 
            
            self.closed_set.add(current_node) 

            for neighbor in current_node.neighbors: 
                if neighbor in self.closed_set: 
                    continue

                dist_to_neighbor = self._heuristic(current_node.pos, neighbor.pos)
                tentative_g = current_node.g + dist_to_neighbor

                in_open_list = neighbor in self.open_list

                if tentative_g < neighbor.g or not in_open_list:
                    neighbor.parent = current_node
                    neighbor.g = tentative_g 
                    neighbor.h = self._heuristic(neighbor.pos, self.target_node.pos)
                    neighbor.f = neighbor.g + neighbor.h

                    if not in_open_list:
                        heapq.heappush(self.open_list, neighbor)
                    else: 
                        heapq.heappush(self.open_list, neighbor)

        return False


    def get_path_as_vectors(self):
        if not self.path_found:
            return[]
        
        SAFETY_COUNTER = 0
        MAX_LOOPS = 1000

        path = []
        curr = self.target_node
        while curr is not None: 
            path.append(curr.pos)
            curr = curr.parent
            if curr == self.start_node:
                break 
            
            SAFETY_COUNTER += 1
            if SAFETY_COUNTER > MAX_LOOPS:
                print("Infinite loop detected")
                break
            
        path.reverse()
        return path 
    

class Pathfinder:
    def __init__(self, nav_graph):
        self.nav_graph = nav_graph 
        self.current_search = None 


    def get_closest_node(self, position):
        key = self.nav_graph._pos_to_key(position)

        if key in self.nav_graph.node_map:
            return self.nav_graph.node_map[key]
        
        closest_node = None 
        min_dist_sq = float('inf')
        
        for node in self.nav_graph.nodes:
            dist_sq = (node.pos - position).LengthSquared()
            if dist_sq < min_dist_sq: 
                min_dist_sq  = dist_sq 
                closest_node = node

        return closest_node
    

    def create_path_to_position(self, start_pos, target_pos):
        start_node = self.get_closest_node(start_pos)
        target_node = self.get_closest_node(target_pos)

        if start_node is None or target_node is None: 
            print("Pathfinder: out of bounds")
            return []
        

        self.current_search = AStarSearch(start_node, target_node)
        success = self.current_search.run()

        if success: 
            path = self.current_search.get_path_as_vectors()
            return path
        else: 
            print("Pathfinder: no path")
            return []


    def create_path_to_pickup(self, start_pos, pickup_type):
        start_node = self.get_closest_node(start_pos)

        if start_node is None: return []
        self.current_search = DijkstraSearch(start_node, pickup_type)
        if self.current_search.run():
            path = self.current_search.get_path_as_vectors()
            return path

        print(f"No active pickup of type {pickup_type} found")
        return []
    

class Path: 
    def __init__(self, waypoints):
        self.waypoints = waypoints
        self.cur_waypoint_idx = 0
        self.looped = False 
        self.finished = False
    
    def current_waypoint(self):
        if self.cur_waypoint_idx < len(self.waypoints):
            return self.waypoints[self.cur_waypoint_idx]
        return self.waypoints[-1]
    
    def set_next_waypoint(self):
        if len(self.waypoints) == 0: 
            return 
        
        if self.cur_waypoint_idx < len(self.waypoints) - 1: 
            self.cur_waypoint_idx += 1
        else: 
            self.finished = True 
    
    def is_finished(self):
        return self.finished