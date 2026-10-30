
import random


class Entity:
    def __init__(self, x, y, char, name):
        self.x = x
        self.y = y
        self.char = char
        self.name = name


class Backpack:
    def __init__(self):
        self.items = {
            'treasure': [],
            'food': [],
            'elixir': [],
            'scroll': [],
            'weapon': [],
            'key': [],
        }
        self.max_per_type = 9

    def add_item(self, item):
        if item.item_type == 'treasure':
            self.items['treasure'].append(item)
            return True
        if item.item_type == 'key':
            if len(self.items['key']) < self.max_per_type:
                self.items['key'].append(item)
                return True
            return False
        if item.item_type in self.items:
            if len(self.items[item.item_type]) < self.max_per_type:
                self.items[item.item_type].append(item)
                return True
        return False

    def remove_item(self, item_type, index):
        if 0 <= index < len(self.items[item_type]):
            return self.items[item_type].pop(index)
        return None

    def get_items(self, item_type):
        return self.items[item_type]

    def has_key(self, color):
        return any(k.subtype == color for k in self.items['key'])


class Character(Entity):
    def __init__(self, x, y, char, name,
                 max_health, health, agility, strength,
                 weapon=None, backpack=None):
        super().__init__(x, y, char, name)
        self.max_health = max_health
        self.health = health
        self.agility = agility
        self.strength = strength
        self.weapon = weapon
        self.backpack = backpack if backpack else Backpack()
        self.elixir_effects = []


class Player(Character):
    def __init__(self, x, y):
        super().__init__(x, y, '@', 'Player',
                         max_health=100, health=100,
                         agility=10, strength=10)
        self.stat_treasure = 0
        self.stat_enemies_killed = 0
        self.stat_food_eaten = 0
        self.stat_elixirs_drunk = 0
        self.stat_scrolls_read = 0
        self.stat_hits = 0
        self.stat_misses = 0
        self.stat_steps = 0
        self.sleep_counter = 0
        
        self.angle = 0.0


class Enemy(Character):
    def __init__(self, x, y, char, name,
                 max_health, health, agility, strength,
                 hostility, enemy_type):
        super().__init__(x, y, char, name,
                         max_health, health, agility, strength)
        self.hostility = hostility
        self.enemy_type = enemy_type
        self.sleep_counter = 0


class Zombie(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 'z', 'Zombie',
                         max_health=50, health=50,
                         agility=5, strength=10,
                         hostility=5, enemy_type='zombie')


class Vampire(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 'v', 'Vampire',
                         max_health=40, health=40,
                         agility=15, strength=10,
                         hostility=8, enemy_type='vampire')
        self.first_hit = True


class Ghost(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 'g', 'Ghost',
                         max_health=20, health=20,
                         agility=15, strength=5,
                         hostility=3, enemy_type='ghost')
        self.invisible = True


class Ogre(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 'O', 'Ogre',
                         max_health=80, health=80,
                         agility=5, strength=20,
                         hostility=5, enemy_type='ogre')
        self.resting = False
        self.attacked_last_turn = False


class SnakeMage(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 's', 'Snake Mage',
                         max_health=30, health=30,
                         agility=20, strength=8,
                         hostility=10, enemy_type='snake_mage')
        self.diag_dx = 1
        self.diag_dy = 1


class Mimic(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 'm', 'Mimic',
                         max_health=60, health=60,
                         agility=18, strength=5,
                         hostility=2, enemy_type='mimic')
        self.disguised = True


class Item:
    def __init__(self, x, y, char, name, item_type, subtype=None,
                 health=0, max_health=0, agility=0, strength=0, cost=0):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.item_type = item_type
        self.subtype = subtype
        self.health = health
        self.max_health = max_health
        self.agility = agility
        self.strength = strength
        self.cost = cost


class Treasure(Item):
    def __init__(self, x, y, cost):
        super().__init__(x, y, '$', 'Treasure', 'treasure', cost=cost)


class Food(Item):
    def __init__(self, x, y, health):
        super().__init__(x, y, '%', 'Food', 'food', health=health)


class Elixir(Item):
    def __init__(self, x, y, subtype, agility=0, strength=0, max_health=0):
        super().__init__(x, y, '!', 'Elixir', 'elixir', subtype=subtype,
                         agility=agility, strength=strength, max_health=max_health)


class Scroll(Item):
    def __init__(self, x, y, subtype, agility=0, strength=0, max_health=0):
        super().__init__(x, y, '?', 'Scroll', 'scroll', subtype=subtype,
                         agility=agility, strength=strength, max_health=max_health)


class Weapon(Item):
    def __init__(self, x, y, subtype, strength):
        super().__init__(x, y, ')', 'Weapon', 'weapon', subtype=subtype,
                         strength=strength)


class Door(Item):
    def __init__(self, x, y, color):
        super().__init__(x, y, '+', f'{color} Door', 'door', subtype=color)


class Key(Item):
    def __init__(self, x, y, color):
        super().__init__(x, y, '/', f'{color} Key', 'key', subtype=color)