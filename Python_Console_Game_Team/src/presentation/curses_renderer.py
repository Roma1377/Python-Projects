import curses
import math
from domain.level_generator import WALL, FLOOR, CORRIDOR, DOOR

VISIBILITY_RADIUS = 8
FOV = math.pi / 3
MAX_DEPTH = 20


CP_PLAYER = 1
CP_ZOMBIE = 2
CP_VAMPIRE = 3
CP_GHOST = 4
CP_OGRE = 5
CP_SNAKE = 6
CP_MIMIC = 7
CP_TREASURE = 8
CP_FOOD = 9
CP_ELIXIR = 10
CP_SCROLL = 11
CP_WEAPON = 12
CP_KEY_RED = 13
CP_KEY_BLUE = 14
CP_KEY_YELLOW = 15
CP_KEY_GREEN = 16
CP_EXIT = 17

ENEMY_CP = {
    'zombie': CP_ZOMBIE,
    'vampire': CP_VAMPIRE,
    'ghost': CP_GHOST,
    'ogre': CP_OGRE,
    'snake_mage': CP_SNAKE,
    'mimic': CP_MIMIC,
}

ITEM_CP = {
    'treasure': CP_TREASURE,
    'food': CP_FOOD,
    'elixir': CP_ELIXIR,
    'scroll': CP_SCROLL,
    'weapon': CP_WEAPON,
}

KEY_CP = {
    'red': CP_KEY_RED,
    'blue': CP_KEY_BLUE,
    'yellow': CP_KEY_YELLOW,
    'green': CP_KEY_GREEN,
}


class CursesRenderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.level = None
        self.visible = set()
        self.explored = set()
        self.view_mode = '2d'
        self._init_colors()

    def _init_colors(self):
        
        if not curses.has_colors():
            return
        try:
            curses.start_color()
            try:
                curses.use_default_colors()
                bg = -1
            except curses.error:
                bg = curses.COLOR_BLACK
            curses.init_pair(CP_PLAYER, curses.COLOR_CYAN, bg)
            curses.init_pair(CP_ZOMBIE, curses.COLOR_GREEN, bg)
            curses.init_pair(CP_VAMPIRE, curses.COLOR_RED, bg)
            curses.init_pair(CP_GHOST, curses.COLOR_WHITE, bg)
            curses.init_pair(CP_OGRE, curses.COLOR_YELLOW, bg)
            curses.init_pair(CP_SNAKE, curses.COLOR_WHITE, bg)
            curses.init_pair(CP_MIMIC, curses.COLOR_WHITE, bg)
            curses.init_pair(CP_TREASURE, curses.COLOR_YELLOW, bg)
            curses.init_pair(CP_FOOD, curses.COLOR_MAGENTA, bg)
            curses.init_pair(CP_ELIXIR, curses.COLOR_CYAN, bg)
            curses.init_pair(CP_SCROLL, curses.COLOR_MAGENTA, bg)
            curses.init_pair(CP_WEAPON, curses.COLOR_WHITE, bg)
            curses.init_pair(CP_KEY_RED, curses.COLOR_RED, bg)
            curses.init_pair(CP_KEY_BLUE, curses.COLOR_BLUE, bg)
            curses.init_pair(CP_KEY_YELLOW, curses.COLOR_YELLOW, bg)
            curses.init_pair(CP_KEY_GREEN, curses.COLOR_GREEN, bg)
            curses.init_pair(CP_EXIT, curses.COLOR_WHITE, bg)
        except curses.error:
            pass

    def _cp(self, cp_id):
        
        if not cp_id or cp_id <= 0:
            return 0
        try:
            return curses.color_pair(cp_id)
        except curses.error:
            return 0

    def _enemy_attr(self, enemy):
        return self._cp(ENEMY_CP.get(enemy.enemy_type, 0))

    def _item_attr(self, item):
        if item.item_type == 'key':
            return self._cp(KEY_CP.get(item.subtype, 0))
        return self._cp(ITEM_CP.get(item.item_type, 0))

    def set_level(self, level):
        self.level = level
        self.visible = set()
        self.explored = set()

    def render(self, game):
        self.stdscr.clear()
        if game.game_over:
            self._render_game_over(game)
            self.stdscr.refresh()
            return

        self._compute_fov(game)

        if self.view_mode == '3d':
            self._render_3d(game)
            self._render_minimap(game)
        else:
            self._render_map(game)
            self._render_actors(game)

        self._render_status(game)
        self.stdscr.refresh()

    

    def _compute_fov(self, game):
        self.visible = set()
        px, py = game.player.x, game.player.y

        player_room = game.level.room_of(px, py)
        if player_room is not None:
            for x, y in player_room.cells():
                if 0 <= x < game.level.width and 0 <= y < game.level.height:
                    self.visible.add((x, y))

        x_min = max(0, px - VISIBILITY_RADIUS)
        x_max = min(game.level.width, px + VISIBILITY_RADIUS + 1)
        y_min = max(0, py - VISIBILITY_RADIUS)
        y_max = min(game.level.height, py + VISIBILITY_RADIUS + 1)

        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                if (x - px) ** 2 + (y - py) ** 2 > VISIBILITY_RADIUS ** 2:
                    continue
                if self._line_of_sight(game, px, py, x, y):
                    self.visible.add((x, y))

        for pos in self.visible:
            self.explored.add(pos)

    def _line_of_sight(self, game, x0, y0, x1, y1):
        points = self._bresenham(x0, y0, x1, y1)
        for i, (x, y) in enumerate(points):
            if i == 0 or i == len(points) - 1:
                continue
            if not (0 <= x < game.level.width and 0 <= y < game.level.height):
                return False
            if game.level.tiles[y][x] == WALL:
                return False
        return True

    def _bresenham(self, x0, y0, x1, y1):
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return points

    # ---------- 2D ----------

    def _render_map(self, game):
        top_offset = 1
        player_room = game.level.room_of(game.player.x, game.player.y)
        door_at = {(d.x, d.y): d for d in game.level.doors}

        for y in range(game.level.height):
            if y + top_offset >= self.height - 1:
                break
            for x in range(game.level.width):
                if x >= self.width:
                    break
                tile = game.level.tiles[y][x]

                if (x, y) in self.visible:
                    if (x, y) == game.level.exit_position and tile not in (WALL, DOOR):
                        try:
                            self.stdscr.addch(y + top_offset, x, '>',
                                              self._cp(CP_EXIT) | curses.A_BOLD)
                        except curses.error:
                            pass
                    elif tile == DOOR:
                        door = door_at.get((x, y))
                        attr = self._cp(KEY_CP.get(door.subtype, 0)) if door else 0
                        try:
                            self.stdscr.addch(y + top_offset, x, '+', attr)
                        except curses.error:
                            pass
                    else:
                        try:
                            self.stdscr.addch(y + top_offset, x, self._tile_char(tile))
                        except curses.error:
                            pass
                elif (x, y) in self.explored:
                    if tile == WALL:
                        try:
                            self.stdscr.addch(y + top_offset, x, '#')
                        except curses.error:
                            pass
                    elif tile == FLOOR:
                        tile_room = game.level.room_of(x, y)
                        if tile_room is not None and tile_room is not player_room:
                            try:
                                self.stdscr.addch(y + top_offset, x, '#')
                            except curses.error:
                                pass
                        else:
                            try:
                                self.stdscr.addch(y + top_offset, x, ' ')
                            except curses.error:
                                pass
                    else:
                        try:
                            self.stdscr.addch(y + top_offset, x, ' ')
                        except curses.error:
                            pass

    def _tile_char(self, tile):
        if tile == WALL:
            return '#'
        if tile == FLOOR:
            return '.'
        if tile == CORRIDOR:
            return '.'
        if tile == DOOR:
            return '+'
        return ' '

    def _render_actors(self, game):
        top_offset = 1
        for item in game.level.items:
            if (item.x, item.y) in self.visible:
                if item.y + top_offset < self.height - 1 and item.x < self.width:
                    try:
                        self.stdscr.addch(item.y + top_offset, item.x,
                                          item.char, self._item_attr(item))
                    except curses.error:
                        pass

        for enemy in game.level.enemies:
            if (enemy.x, enemy.y) in self.visible:
                if getattr(enemy, 'invisible', False):
                    dist = abs(enemy.x - game.player.x) + abs(enemy.y - game.player.y)
                    if dist > 1:
                        continue
                if getattr(enemy, 'disguised', False):
                    if enemy.y + top_offset < self.height - 1 and enemy.x < self.width:
                        try:
                            self.stdscr.addch(enemy.y + top_offset, enemy.x,
                                              '$', self._cp(CP_TREASURE))
                        except curses.error:
                            pass
                    continue
                if enemy.y + top_offset < self.height - 1 and enemy.x < self.width:
                    try:
                        self.stdscr.addch(enemy.y + top_offset, enemy.x,
                                          enemy.char, self._enemy_attr(enemy))
                    except curses.error:
                        pass

        px, py = game.player.x, game.player.y + top_offset
        if py < self.height - 1 and px < self.width:
            try:
                self.stdscr.addch(py, px, '@', self._cp(CP_PLAYER) | curses.A_BOLD)
            except curses.error:
                pass

    # ---------- 3D ----------

    def _render_3d(self, game):
        top_offset = 1
        map_height = self.height - 2
        if map_height < 3:
            return
        px, py = game.player.x, game.player.y
        player_angle = game.player.angle

        for col in range(self.width):
            ray_angle = player_angle + (col - self.width / 2) / (self.width / 2) * (FOV / 2)
            dist = self._cast_ray(game, px, py, ray_angle)

            if dist <= 0.1:
                dist = 0.1
            if dist > MAX_DEPTH:
                dist = MAX_DEPTH

            wall_height = int(map_height / dist)
            if wall_height < 1:
                wall_height = 1
            if wall_height > map_height:
                wall_height = map_height

            start_y = top_offset + map_height // 2 - wall_height // 2
            end_y = start_y + wall_height

            x_tex = col // 2
            for y in range(max(top_offset, start_y), min(self.height - 1, end_y)):
                char = self._wall_texture(dist, y, x_tex)
                try:
                    self.stdscr.addch(y, col, char)
                except curses.error:
                    pass

    def _cast_ray(self, game, px, py, angle):
        step = 0.05
        dx = math.cos(angle) * step
        dy = math.sin(angle) * step
        x = float(px) + 0.5
        y = float(py) + 0.5
        dist = 0.0
        while dist < MAX_DEPTH:
            x += dx
            y += dy
            dist += step
            ix, iy = int(x), int(y)
            if not (0 <= ix < game.level.width and 0 <= iy < game.level.height):
                return MAX_DEPTH
            if game.level.tiles[iy][ix] == WALL:
                return dist
        return MAX_DEPTH

    def _wall_texture(self, dist, y, x_tex):
        if dist < 2:
            base = ('#', '=')
        elif dist < 4:
            base = ('=', '-')
        elif dist < 6:
            base = ('-', '.')
        else:
            base = ('.', ' ')
        return base[(y + x_tex) % 2]

    def _render_minimap(self, game):
        
        size = 20
        start_x = self.width - size - 1
        start_y = 1

        if start_x < 0:
            return

        px, py = game.player.x, game.player.y
        offset_x = max(0, min(px - size // 2, game.level.width - size))
        offset_y = max(0, min(py - size // 2, game.level.height - size))

        item_at = {(it.x, it.y): it for it in game.level.items}
        enemy_at = {(e.x, e.y): e for e in game.level.enemies}
        door_at = {(d.x, d.y): d for d in game.level.doors}

        for y in range(size):
            for x in range(size):
                mx = offset_x + x
                my = offset_y + y
                if not (0 <= mx < game.level.width and 0 <= my < game.level.height):
                    continue
                scr_x = start_x + x
                scr_y = start_y + y
                if scr_x >= self.width - 1 or scr_y >= self.height - 1:
                    continue

                ch = ' '
                cp_id = 0
                if (mx, my) in self.explored:
                    tile = game.level.tiles[my][mx]
                    if tile == WALL:
                        ch = '#'
                    elif tile == DOOR:
                        ch = '+'
                        door = door_at.get((mx, my))
                        if door:
                            cp_id = KEY_CP.get(door.subtype, 0)
                    elif (mx, my) == game.level.exit_position:
                        ch = '>'
                        cp_id = CP_EXIT
                    else:
                        ch = '.'

                    if (mx, my) in item_at and (mx, my) != (px, py):
                        item = item_at[(mx, my)]
                        ch = item.char
                        if item.item_type == 'key':
                            cp_id = KEY_CP.get(item.subtype, 0)
                        else:
                            cp_id = ITEM_CP.get(item.item_type, 0)

                    if (mx, my) in enemy_at:
                        enemy = enemy_at[(mx, my)]
                        if getattr(enemy, 'invisible', False):
                            d = abs(enemy.x - px) + abs(enemy.y - py)
                            if d <= 1:
                                ch = enemy.char
                                cp_id = ENEMY_CP.get(enemy.enemy_type, 0)
                        elif getattr(enemy, 'disguised', False):
                            ch = '$'
                            cp_id = CP_TREASURE
                        else:
                            ch = enemy.char
                            cp_id = ENEMY_CP.get(enemy.enemy_type, 0)

                if mx == px and my == py:
                    ch = '@'
                    cp_id = CP_PLAYER

                try:
                    self.stdscr.addch(scr_y, scr_x, ch, self._cp(cp_id))
                except curses.error:
                    pass

   

    def _render_status(self, game):
        hp = f"HP {game.player.health}/{game.player.max_health}"
        stats = f"AGI {game.player.agility} | STR {game.player.strength}"
        prog = f"Lvl {game.current_level}/{21} | Turn {game.turn}"
        treasure = f"Treasure {game.player.stat_treasure}"
        mode = f"[{self.view_mode.upper()}]"
        line1 = f" {hp} | {stats} | {prog} | {treasure} {mode} "
        try:
            self.stdscr.addstr(0, 0, line1[:self.width - 1])
        except curses.error:
            pass

        weapon_name = game.player.weapon.name if game.player.weapon else '-'
        backpack = (f"W:{len(game.player.backpack.items['weapon'])} "
                    f"F:{len(game.player.backpack.items['food'])} "
                    f"E:{len(game.player.backpack.items['elixir'])} "
                    f"S:{len(game.player.backpack.items['scroll'])} "
                    f"K:{len(game.player.backpack.items['key'])}")
        line2 = f" Weapon: {weapon_name} | {backpack} | h j k e i l v q "
        try:
            self.stdscr.addstr(self.height - 1, 0, line2[:self.width - 1])
        except curses.error:
            pass

    def _render_game_over(self, game):
        msg = "VICTORY! You escaped the dungeon!" if game.victory else "GAME OVER"
        try:
            self.stdscr.addstr(self.height // 2, max(0, self.width // 2 - len(msg) // 2), msg)
            self.stdscr.addstr(self.height // 2 + 2, 2,
                               f"Treasure: {game.player.stat_treasure}, Level: {game.current_level}")
            self.stdscr.addstr(self.height // 2 + 3, 2, "Press any key...")
        except curses.error:
            pass

    def get_key(self):
        return self.stdscr.getkey()

    def show_item_menu(self, item_type, items, allow_unequip=False):
        self.stdscr.clear()
        header = f"Select {item_type} (1-{len(items)})"
        if allow_unequip:
            header += " | 0 - unequip"
        try:
            self.stdscr.addstr(0, 0, header)
            for i, item in enumerate(items, 1):
                label = item.name
                if item.subtype:
                    label += f" [{item.subtype}]"
                self.stdscr.addstr(i, 0, f"{i}. {label}")
            self.stdscr.addstr(len(items) + 2, 0, "Press key 0-9 or other to cancel")
            self.stdscr.refresh()
        except curses.error:
            pass

    def show_inventory(self, player):
        self.stdscr.clear()
        try:
            self.stdscr.addstr(0, 0, "=== INVENTORY ===")
            row = 2
            for item_type in ('weapon', 'food', 'elixir', 'scroll', 'key'):
                items = player.backpack.get_items(item_type)
                self.stdscr.addstr(row, 0, f"{item_type.upper()} ({len(items)}):")
                row += 1
                for i, item in enumerate(items, 1):
                    label = item.name
                    if item.subtype:
                        label += f" [{item.subtype}]"
                    self.stdscr.addstr(row, 4, f"{i}. {label}")
                    row += 1
            self.stdscr.addstr(row + 1, 0,
                               f"Treasure count: {len(player.backpack.items['treasure'])} | Total: {player.stat_treasure}")
            self.stdscr.addstr(row + 3, 0, "Press any key...")
            self.stdscr.refresh()
        except curses.error:
            pass
        self.stdscr.getkey()

    def show_leaderboard(self, stats_manager):
        self.stdscr.clear()
        try:
            self.stdscr.addstr(0, 0, "=== LEADERBOARD ===")
            leaders = stats_manager.get_leaderboard()
            if not leaders:
                self.stdscr.addstr(2, 0, "No records yet.")
            else:
                header = (f"{'#':<3} {'Tres':<6} {'Lvl':<4} {'Kill':<5} "
                          f"{'Food':<5} {'Elx':<4} {'Scr':<4} {'Hit':<5} {'Miss':<5} {'Step':<5}")
                self.stdscr.addstr(2, 0, header)
                for i, rec in enumerate(leaders[:10], 1):
                    line = (f"{i:<3} {rec.get('treasure',0):<6} {rec.get('level',0):<4} "
                            f"{rec.get('enemies_killed',0):<5} {rec.get('food_eaten',0):<5} "
                            f"{rec.get('elixirs_drunk',0):<4} {rec.get('scrolls_read',0):<4} "
                            f"{rec.get('hits',0):<5} {rec.get('misses',0):<5} "
                            f"{rec.get('steps',0):<5}")
                    self.stdscr.addstr(3 + i, 0, line[:self.width - 1])
            self.stdscr.addstr(self.height - 2, 0, "Press any key...")
            self.stdscr.refresh()
        except curses.error:
            pass
        self.stdscr.getkey()

    def ask_continue(self):
        self.stdscr.clear()
        try:
            self.stdscr.addstr(0, 0, "Save found. Continue? (y/n)")
            self.stdscr.refresh()
        except curses.error:
            pass
        key = self.stdscr.getkey()
        return key.lower() == 'y'