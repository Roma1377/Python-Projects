import random
from collections import deque

MAP_WIDTH = 80
MAP_HEIGHT = 25

WALL = 0
FLOOR = 1
CORRIDOR = 2
DOOR = 3


class Room:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def center(self):
        return self.x + self.width // 2, self.y + self.height // 2

    def intersects(self, other, padding=1):
        return (self.x - padding < other.x + other.width and
                self.x + self.width + padding > other.x and
                self.y - padding < other.y + other.height and
                self.y + self.height + padding > other.y)

    def cells(self):
        for x in range(self.x, self.x + self.width):
            for y in range(self.y, self.y + self.height):
                yield x, y

    def inner_cells(self):
        for x in range(self.x + 1, self.x + self.width - 1):
            for y in range(self.y + 1, self.y + self.height - 1):
                yield x, y

    def is_inside(self, x, y):
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height


class Corridor:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.cells = self._compute_cells()

    def _compute_cells(self):
        x1, y1 = self.start
        x2, y2 = self.end
        cells = []
        if random.random() < 0.5:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                cells.append((x, y1))
            for y in range(min(y1, y2), max(y1, y2) + 1):
                cells.append((x2, y))
        else:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                cells.append((x1, y))
            for x in range(min(x1, x2), max(x1, x2) + 1):
                cells.append((x, y2))
        return cells


class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.tiles = [[WALL for _ in range(self.width)] for _ in range(self.height)]
        self.rooms = []
        self.corridors = []
        self.doors = []
        self.player_start = None
        self.exit_position = None
        self.enemies = []
        self.items = []
        self.start_room_index = 0
        self.exit_room_index = 8
        self.generate()

    def generate(self):
        self._generate_rooms()
        self._connect_rooms()
        self._carve_tiles()
        self._ensure_connectivity()
        
        self.player_start = self.random_free_cell_in_room(self.rooms[self.start_room_index])
        self.exit_position = self.rooms[self.exit_room_index].center()

    def _generate_rooms(self):
        grid_size = 3
        cell_w = self.width // grid_size
        cell_h = self.height // grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                cell_x = j * cell_w
                cell_y = i * cell_h
                room_w = random.randint(5, min(cell_w - 4, 12))
                room_h = random.randint(4, min(cell_h - 3, 8))
                max_x = cell_x + cell_w - room_w - 2
                max_y = cell_y + cell_h - room_h - 2
                room_x = random.randint(cell_x + 2, max(max_x, cell_x + 2))
                room_y = random.randint(cell_y + 1, max(max_y, cell_y + 1))
                room = Room(room_x, room_y, room_w, room_h)
                if not any(room.intersects(r) for r in self.rooms):
                    self.rooms.append(room)
                else:
                    self.rooms.append(Room(cell_x + 2, cell_y + 1, 5, 4))

        while len(self.rooms) < 9:
            idx = len(self.rooms)
            cx = (idx % 3) * cell_w + 2
            cy = (idx // 3) * cell_h + 1
            self.rooms.append(Room(cx, cy, 5, 4))

    def _connect_rooms(self):
        grid_size = 3
        for i in range(grid_size):
            for j in range(grid_size - 1):
                idx1 = i * grid_size + j
                idx2 = i * grid_size + j + 1
                if idx1 < len(self.rooms) and idx2 < len(self.rooms):
                    self.corridors.append(
                        Corridor(self.rooms[idx1].center(), self.rooms[idx2].center()))
        for i in range(grid_size - 1):
            for j in range(grid_size):
                idx1 = i * grid_size + j
                idx2 = (i + 1) * grid_size + j
                if idx1 < len(self.rooms) and idx2 < len(self.rooms):
                    self.corridors.append(
                        Corridor(self.rooms[idx1].center(), self.rooms[idx2].center()))

    def _carve_tiles(self):
        for room in self.rooms:
            for x, y in room.cells():
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.tiles[y][x] = FLOOR
        for corridor in self.corridors:
            for x, y in corridor.cells:
                if 0 <= x < self.width and 0 <= y < self.height:
                    if self.tiles[y][x] == WALL:
                        self.tiles[y][x] = CORRIDOR

    def _reachable_from(self, start, blocked_doors=True):
        visited = set()
        queue = deque([start])
        visited.add(start)
        while queue:
            x, y = queue.popleft()
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if (nx, ny) in visited:
                    continue
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                tile = self.tiles[ny][nx]
                if blocked_doors and tile == DOOR:
                    continue
                if tile in (FLOOR, CORRIDOR, DOOR):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        return visited

    def _ensure_connectivity(self):
        start = self.rooms[0].center()
        reachable = self._reachable_from(start, blocked_doors=False)
        for room in self.rooms:
            if room.center() not in reachable:
                c = Corridor(start, room.center())
                self.corridors.append(c)
                for x, y in c.cells:
                    if 0 <= x < self.width and 0 <= y < self.height:
                        if self.tiles[y][x] == WALL:
                            self.tiles[y][x] = CORRIDOR
                reachable = self._reachable_from(start, blocked_doors=False)

    def is_walkable(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.tiles[y][x] in (FLOOR, CORRIDOR, DOOR)

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def room_of(self, x, y):
        for room in self.rooms:
            if room.is_inside(x, y):
                return room
        return None

    def is_in_start_room(self, x, y):
        return self.rooms[self.start_room_index].is_inside(x, y)

    def random_free_cell_in_room(self, room, occupied=None):
        occupied = occupied or set()
        candidates = []
        for x, y in room.inner_cells():
            if (x, y) not in occupied:
                candidates.append((x, y))
        if not candidates:
            return room.center()
        return random.choice(candidates)

    def _find_room_entrances(self, room):
        
        entrances = []
        seen = set()
        for corridor in self.corridors:
            
            queue = deque(corridor.cells)
            while queue:
                x, y = queue.popleft()
                if (x, y) in seen:
                    continue
                seen.add((x, y))
                if room.is_inside(x, y):
                    continue
                if self.tiles[y][x] != CORRIDOR:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if room.is_inside(nx, ny) and self.tiles[ny][nx] == FLOOR:
                        entrances.append((x, y))
                        break
        
        uniq = []
        for pos in entrances:
            if pos not in uniq:
                uniq.append(pos)
        return uniq

    def add_door_and_key(self):
        from domain.entities import Door, Key
        colors = ['red', 'blue', 'yellow', 'green']
        color = random.choice(colors)

        exit_room = self.rooms[self.exit_room_index]
        
        junctions = self._find_room_entrances(exit_room)
        if not junctions:
            return

        door_positions = []
        for (x, y) in junctions:
            door = Door(x, y, color)
            self.doors.append(door)
            self.tiles[y][x] = DOOR
            door_positions.append((x, y))

        candidates = [r for i, r in enumerate(self.rooms)
                      if i != self.start_room_index and i != self.exit_room_index]
        if not candidates:
            for (x, y) in door_positions:
                self.tiles[y][x] = CORRIDOR
            self.doors.clear()
            return

        key_room = random.choice(candidates)
        kx, ky = self.random_free_cell_in_room(key_room)
        key = Key(kx, ky, color)
        self.items.append(key)

        
        if self.has_softlock():
            for (x, y) in door_positions:
                self.tiles[y][x] = CORRIDOR
            self.doors.clear()
            self.items = [i for i in self.items if i.item_type != 'key']
            self.add_door_and_key()

    def has_softlock(self):
        if not self.doors:
            return False

        start = self.player_start
        no_door_reach = self._reachable_from(start, blocked_doors=True)

        key_pos = None
        for item in self.items:
            if item.item_type == 'key':
                key_pos = (item.x, item.y)
                break
        if key_pos is None:
            return True
        if key_pos not in no_door_reach:
            return True

        with_door_reach = self._reachable_from(start, blocked_doors=False)
        exit_pos = self.exit_position
        if exit_pos not in with_door_reach:
            return True

        return False