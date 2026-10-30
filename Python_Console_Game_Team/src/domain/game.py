import random
import math
from domain.entities import (
    Player, Zombie, Vampire, Ghost, Ogre, SnakeMage, Mimic,
    Food, Elixir, Scroll, Weapon, Treasure, Key, Door
)
from domain.level_generator import Level, DOOR
from domain.combat import player_attack, enemy_attack
from domain.items import (
    use_food, use_elixir, use_scroll, use_weapon,
    unequip_weapon, tick_elixir_effects
)

MAX_LEVEL = 21


class Game:
    def __init__(self, renderer, save_manager, stats_manager):
        self.renderer = renderer
        self.save_manager = save_manager
        self.stats_manager = stats_manager
        self.player = None
        self.current_level = 1
        self.level = None
        self.turn = 0
        self.running = False
        self.game_over = False
        self.victory = False
        self.difficulty_multiplier = 1.0
        self.damage_taken_recent = 0
        self.view_mode = '2d'
        self.restart_requested = False

    def start_new_game(self):
        self.current_level = 1
        self.player = Player(0, 0)
        self.turn = 0
        self.difficulty_multiplier = 1.0
        self.damage_taken_recent = 0
        self.game_over = False
        self.victory = False
        self.restart_requested = False
        self._build_level()
        self.running = True

    def _build_level(self):
        self.level = Level(self.current_level)
        self.player.x, self.player.y = self.level.player_start
        self._populate_level()
        if self.current_level >= 3:
            self.level.add_door_and_key()
        self.renderer.set_level(self.level)

    def _enemy_pool_for_depth(self, depth):
        
        if depth <= 3:
            return [Zombie, Zombie, Vampire]
        if depth <= 6:
            return [Zombie, Vampire, Ghost]
        if depth <= 10:
            return [Vampire, Ghost, Mimic]
        if depth <= 14:
            return [Ghost, SnakeMage, Vampire]
        if depth <= 17:
            return [SnakeMage, Ogre, Ghost]
        return [Ogre, SnakeMage, Ogre, SnakeMage]

    def _populate_level(self):
        depth = self.current_level
        base_enemies = 3 + depth // 2
        num_enemies = max(1, int(base_enemies * self.difficulty_multiplier))

        enemy_pool = self._enemy_pool_for_depth(depth)

        occupied = set()
        for _ in range(num_enemies):
            room = random.choice(self.level.rooms[1:])
            x, y = self.level.random_free_cell_in_room(room, occupied)
            occupied.add((x, y))
            enemy_class = random.choice(enemy_pool)
            self.level.add_enemy(enemy_class(x, y))

        num_items = max(1, 6 - depth // 3)
        for _ in range(num_items):
            room = random.choice(self.level.rooms[1:])
            x, y = self.level.random_free_cell_in_room(room, occupied)
            occupied.add((x, y))
            self.level.add_item(self._random_item(x, y))

        
        if self.player.health < self.player.max_health * 0.4 \
                or self.damage_taken_recent > 30:
            for _ in range(3):
                room = random.choice(self.level.rooms[1:])
                x, y = self.level.random_free_cell_in_room(room, occupied)
                occupied.add((x, y))
                self.level.add_item(Food(x, y, random.randint(8, 15)))

        

    def _random_item(self, x, y):
        roll = random.random()
        if roll < 0.45:
            return Food(x, y, random.randint(5, 15))
        if roll < 0.65:
            return Elixir(x, y, random.choice(['agility', 'strength', 'max_health']),
                          agility=2, strength=2, max_health=5)
        if roll < 0.85:
            return Scroll(x, y, random.choice(['agility', 'strength', 'max_health']),
                          agility=1, strength=1, max_health=3)
        return Weapon(x, y, random.choice(['sword', 'axe', 'dagger']), random.randint(2, 6))

    def run(self):
        while self.running:
            if self.game_over:
                self.renderer.render(self)
                self.renderer.get_key()
                if self.restart_requested:
                    self.restart_requested = False
                    self.start_new_game()
                    continue
                else:
                    self.running = False
                    break

            self.renderer.render(self)
            key = self.renderer.get_key()
            turn_consumed = self.handle_input(key)
            if self.game_over or not self.running:
                continue
            if turn_consumed:
                
                self.process_turn()
                if not self.game_over:
                    tick_elixir_effects(self.player)
                    if self.player.health <= 0:
                        self.game_over = True
                        self.restart_requested = True
                        self._finalize()

    def handle_input(self, key):
        
        if getattr(self.player, 'sleep_counter', 0) > 0:
            if key in ('w', 'a', 's', 'd', 'h', 'j', 'k', 'e'):
                self.player.sleep_counter -= 1
                return True

        
        if self.view_mode == '3d':
            if key == 'a':
                self.player.angle -= math.pi / 8
                return True
            elif key == 'd':
                self.player.angle += math.pi / 8
                return True
            elif key == 'w':
                return self.move_player_3d(forward=True)
            elif key == 's':
                return self.move_player_3d(forward=False)
            elif key == 'h':
                return self.use_weapon_menu()
            elif key == 'j':
                return self.use_food_menu()
            elif key == 'k':
                return self.use_elixir_menu()
            elif key == 'e':
                return self.use_scroll_menu()
            elif key == 'i':
                self.renderer.show_inventory(self.player)
                return False
            elif key == 'l':
                self.renderer.show_leaderboard(self.stats_manager)
                return False
            elif key == 'v':
                self.view_mode = '2d'
                self.renderer.view_mode = self.view_mode
                return False
            elif key == 'q':
                self.running = False
                self._finalize()
                return False
            return False

        
        if key in ('w', 'a', 's', 'd'):
            return self.move_player(key)
        elif key == 'h':
            return self.use_weapon_menu()
        elif key == 'j':
            return self.use_food_menu()
        elif key == 'k':
            return self.use_elixir_menu()
        elif key == 'e':
            return self.use_scroll_menu()
        elif key == 'i':
            self.renderer.show_inventory(self.player)
            return False
        elif key == 'l':
            self.renderer.show_leaderboard(self.stats_manager)
            return False
        elif key == 'v':
            self.view_mode = '3d'
            self.renderer.view_mode = self.view_mode
            return False
        elif key == 'q':
            self.running = False
            self._finalize()
            return False
        return False

    def move_player_3d(self, forward):
        
        a = self.player.angle % (2 * math.pi)
        idx = int(round(a / (math.pi / 2))) % 4
        dirs = {0: 'd', 1: 's', 2: 'a', 3: 'w'}  # 0=E, 1=S, 2=W, 3=N
        if forward:
            return self.move_player(dirs[idx])
        return self.move_player(dirs[(idx + 2) % 4])

    def move_player(self, direction):
        dx, dy = {'w': (0, -1), 'a': (-1, 0), 's': (0, 1), 'd': (1, 0)}[direction]
        nx, ny = self.player.x + dx, self.player.y + dy

        if not self.level.is_walkable(nx, ny):
            return False

        enemy = next((e for e in self.level.enemies if e.x == nx and e.y == ny), None)
        if enemy:
            if getattr(enemy, 'disguised', False):
                enemy.disguised = False
            self._player_attacks(enemy)
            return True

        door = next((d for d in self.level.doors if d.x == nx and d.y == ny), None)
        if door:
            if self.player.backpack.has_key(door.subtype):
                self.level.tiles[ny][nx] = 2
                self.level.doors.remove(door)
            else:
                return False

        self.player.x, self.player.y = nx, ny
        self.player.stat_steps += 1

        item = next((i for i in self.level.items if i.x == nx and i.y == ny), None)
        if item:
            if self.player.backpack.add_item(item):
                self.level.remove_item(item)
                if item.item_type == 'treasure':
                    self.player.stat_treasure += item.cost

        if (nx, ny) == self.level.exit_position:
            self.next_level()

        return True

    def _player_attacks(self, enemy):
        if isinstance(enemy, Vampire) and getattr(enemy, 'first_hit', False):
            enemy.first_hit = False
            self.player.stat_misses += 1
            return

        hit, damage = player_attack(self.player, enemy)
        if hit and enemy.health <= 0:
            self.level.remove_enemy(enemy)
            self.player.stat_enemies_killed += 1
            drop = self._treasure_drop(enemy)
            self.level.add_item(Treasure(enemy.x, enemy.y, drop))

    def _treasure_drop(self, enemy):
        base = (enemy.hostility + enemy.strength + enemy.agility + enemy.max_health // 10)
        base = max(3, base)
        
        base += self.current_level
        return random.randint(base // 2, base)

    def process_turn(self):
        self.turn += 1
        for enemy in list(self.level.enemies):
            if self.game_over:
                break
            self._enemy_act(enemy)

    def _enemy_act(self, enemy):
        dist = abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y)

        if dist == 1:
            if isinstance(enemy, Ogre):
                
                if enemy.resting:
                    
                    enemy.resting = False
                    enemy.attacked_last_turn = False
                    damage = enemy.strength
                    self.player.health -= damage
                    self.damage_taken_recent += damage
                    if self.player.health <= 0:
                        self.game_over = True
                        self.restart_requested = True
                        self._finalize()
                    return
                elif enemy.attacked_last_turn:
                    
                    enemy.attacked_last_turn = False
                    enemy.resting = True
                    return
                else:
                    
                    hit, dmg = enemy_attack(enemy, self.player)
                    if hit:
                        self.damage_taken_recent += dmg
                        if self.player.health <= 0:
                            self.game_over = True
                            self.restart_requested = True
                            self._finalize()
                    enemy.attacked_last_turn = True
                    return
            else:
                hit, dmg = enemy_attack(enemy, self.player)
                if hit:
                    self.damage_taken_recent += dmg
                    if self.player.health <= 0:
                        self.game_over = True
                        self.restart_requested = True
                        self._finalize()
                return

        if isinstance(enemy, Ghost):
            if dist <= enemy.hostility:
                if random.random() < 0.4:
                    room = self.level.room_of(enemy.x, enemy.y)
                    if room:
                        enemy.x, enemy.y = self.level.random_free_cell_in_room(room)
                enemy.invisible = False
            else:
                if random.random() < 0.3:
                    room = self.level.room_of(enemy.x, enemy.y)
                    if room:
                        enemy.x, enemy.y = self.level.random_free_cell_in_room(room)
                enemy.invisible = True
            return

        if isinstance(enemy, SnakeMage):
            self._move_diagonal(enemy)
            return

        step = 2 if isinstance(enemy, Ogre) else 1
        if dist <= enemy.hostility:
            self._chase(enemy, step)
        else:
            self._wander(enemy)

    def _chase(self, enemy, step):
        for _ in range(step):
            dx = 0
            dy = 0
            if abs(enemy.x - self.player.x) > abs(enemy.y - self.player.y):
                dx = 1 if self.player.x > enemy.x else -1
            elif abs(enemy.y - self.player.y) > abs(enemy.x - self.player.x):
                dy = 1 if self.player.y > enemy.y else -1
            else:
                if random.random() < 0.5:
                    dx = 1 if self.player.x > enemy.x else -1
                else:
                    dy = 1 if self.player.y > enemy.y else -1
            nx, ny = enemy.x + dx, enemy.y + dy
            if self.level.is_walkable(nx, ny) and not self._occupied(nx, ny, enemy):
                enemy.x, enemy.y = nx, ny
                if abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y) == 1:
                    return
            else:
                break

    def _wander(self, enemy):
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = enemy.x + dx, enemy.y + dy
            if self.level.is_walkable(nx, ny) and not self._occupied(nx, ny, enemy):
                enemy.x, enemy.y = nx, ny
                return

    def _move_diagonal(self, enemy):
        for _ in range(2):
            nx = enemy.x + enemy.diag_dx
            ny = enemy.y + enemy.diag_dy
            if not self.level.is_walkable(nx, ny) or self._occupied(nx, ny, enemy):
                enemy.diag_dx *= -1
                enemy.diag_dy *= -1
                nx = enemy.x + enemy.diag_dx
                ny = enemy.y + enemy.diag_dy
                if not self.level.is_walkable(nx, ny) or self._occupied(nx, ny, enemy):
                    return
            enemy.x, enemy.y = nx, ny

    def _occupied(self, x, y, self_enemy):
        for e in self.level.enemies:
            if e is not self_enemy and e.x == x and e.y == y:
                return True
        if self.player.x == x and self.player.y == y:
            return True
        return False

    def next_level(self):
        self.current_level += 1
        if self.current_level > MAX_LEVEL:
            self.game_over = True
            self.victory = True
            self.restart_requested = False
            self.damage_taken_recent = 0
            self._finalize()
            return
        
        self._adjust_difficulty()
        self.damage_taken_recent = 0
        
        self._build_level()
        self.save_manager.save(self)

    def _adjust_difficulty(self):
        
        if self.player.health > 80 and self.player.stat_treasure > self.current_level * 15:
            self.difficulty_multiplier = min(2.5, self.difficulty_multiplier + 0.2)
        elif self.player.health < 30 or self.damage_taken_recent > 30:
            self.difficulty_multiplier = max(0.7, self.difficulty_multiplier - 0.2)
        else:
            self.difficulty_multiplier = 1.0

    def _finalize(self):
        
        recorded_level = min(self.current_level, MAX_LEVEL)
        self.stats_manager.add_result(
            treasure=self.player.stat_treasure,
            level=recorded_level,
            enemies_killed=self.player.stat_enemies_killed,
            food_eaten=self.player.stat_food_eaten,
            elixirs_drunk=self.player.stat_elixirs_drunk,
            scrolls_read=self.player.stat_scrolls_read,
            hits=self.player.stat_hits,
            misses=self.player.stat_misses,
            steps=self.player.stat_steps
        )
        
        if self.game_over:
            self.save_manager.clear()

    def load_session(self):
        from datalayer.save_manager import deserialize_level, deserialize_player_into
        data = self.save_manager.load()
        if not data:
            return
        self.current_level = data['current_level']
        self.turn = data.get('turn', 0)
        self.difficulty_multiplier = data.get('difficulty_multiplier', 1.0)
        self.damage_taken_recent = data.get('damage_taken_recent', 0)
        self.view_mode = data.get('view_mode', '2d')
        self.renderer.view_mode = self.view_mode

        self.player = Player(0, 0)
        deserialize_player_into(self.player, data['player'])

        self.level = deserialize_level(data['level'])
        self.renderer.set_level(self.level)

        self.running = True
        self.game_over = False
        self.victory = False

    def use_weapon_menu(self):
        weapons = self.player.backpack.get_items('weapon')
        self.renderer.show_item_menu('weapon', weapons, allow_unequip=True)
        choice = self.renderer.get_key()
        if not choice.isdigit():
            return False
        idx = int(choice)
        if idx == 0:
            
            return unequip_weapon(self.player)
        elif 1 <= idx <= len(weapons):
            weapon = self.player.backpack.remove_item('weapon', idx - 1)
            use_weapon(self.player, weapon, self.level)
            return True
        return False

    def use_food_menu(self):
        foods = self.player.backpack.get_items('food')
        self.renderer.show_item_menu('food', foods)
        choice = self.renderer.get_key()
        if not choice.isdigit():
            return False
        idx = int(choice) - 1
        if 0 <= idx < len(foods):
            food = self.player.backpack.remove_item('food', idx)
            use_food(self.player, food)
            return True
        return False

    def use_elixir_menu(self):
        elixirs = self.player.backpack.get_items('elixir')
        self.renderer.show_item_menu('elixir', elixirs)
        choice = self.renderer.get_key()
        if not choice.isdigit():
            return False
        idx = int(choice) - 1
        if 0 <= idx < len(elixirs):
            elixir = self.player.backpack.remove_item('elixir', idx)
            use_elixir(self.player, elixir)
            return True
        return False

    def use_scroll_menu(self):
        scrolls = self.player.backpack.get_items('scroll')
        self.renderer.show_item_menu('scroll', scrolls)
        choice = self.renderer.get_key()
        if not choice.isdigit():
            return False
        idx = int(choice) - 1
        if 0 <= idx < len(scrolls):
            scroll = self.player.backpack.remove_item('scroll', idx)
            use_scroll(self.player, scroll)
            return True
        return False