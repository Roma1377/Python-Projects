import json
import os

from domain.entities import (
    Player, Zombie, Vampire, Ghost, Ogre, SnakeMage, Mimic,
    Food, Elixir, Scroll, Weapon, Treasure, Key, Door, Backpack
)
from domain.level_generator import Level, Room, Corridor

SAVE_FILE = "save.json"

ENEMY_CLASSES = {
    'zombie': Zombie,
    'vampire': Vampire,
    'ghost': Ghost,
    'ogre': Ogre,
    'snake_mage': SnakeMage,
    'mimic': Mimic,
}


def serialize_item(item):
    data = {'item_type': item.item_type, 'x': item.x, 'y': item.y}
    if item.item_type == 'treasure':
        data['cost'] = item.cost
    elif item.item_type == 'food':
        data['health'] = item.health
    elif item.item_type in ('elixir', 'scroll'):
        data['subtype'] = item.subtype
        data['agility'] = item.agility
        data['strength'] = item.strength
        data['max_health'] = item.max_health
    elif item.item_type == 'weapon':
        data['subtype'] = item.subtype
        data['strength'] = item.strength
    elif item.item_type == 'key':
        data['subtype'] = item.subtype
    return data


def deserialize_item(data):
    t = data.get('item_type')
    x, y = data['x'], data['y']
    if t == 'treasure':
        return Treasure(x, y, data['cost'])
    if t == 'food':
        return Food(x, y, data['health'])
    if t == 'elixir':
        return Elixir(x, y, data['subtype'],
                      data.get('agility', 0), data.get('strength', 0), data.get('max_health', 0))
    if t == 'scroll':
        return Scroll(x, y, data['subtype'],
                      data.get('agility', 0), data.get('strength', 0), data.get('max_health', 0))
    if t == 'weapon':
        return Weapon(x, y, data['subtype'], data['strength'])
    if t == 'key':
        return Key(x, y, data['subtype'])
    return None


def serialize_enemy(enemy):
    data = {
        'enemy_type': enemy.enemy_type,
        'x': enemy.x, 'y': enemy.y,
        'health': enemy.health,
        'max_health': enemy.max_health,
        'agility': enemy.agility,
        'strength': enemy.strength,
        'hostility': enemy.hostility,
    }
    if enemy.enemy_type == 'vampire':
        data['first_hit'] = enemy.first_hit
    elif enemy.enemy_type == 'ghost':
        data['invisible'] = enemy.invisible
    elif enemy.enemy_type == 'ogre':
        data['resting'] = enemy.resting
        data['attacked_last_turn'] = enemy.attacked_last_turn
    elif enemy.enemy_type == 'snake_mage':
        data['diag_dx'] = enemy.diag_dx
        data['diag_dy'] = enemy.diag_dy
    elif enemy.enemy_type == 'mimic':
        data['disguised'] = enemy.disguised
    return data


def deserialize_enemy(data):
    cls = ENEMY_CLASSES.get(data['enemy_type'])
    if cls is None:
        return None
    e = cls(data['x'], data['y'])
    e.health = data['health']
    e.max_health = data['max_health']
    e.agility = data['agility']
    e.strength = data['strength']
    e.hostility = data['hostility']
    if 'first_hit' in data:
        e.first_hit = data['first_hit']
    if 'invisible' in data:
        e.invisible = data['invisible']
    if 'resting' in data:
        e.resting = data['resting']
    if 'attacked_last_turn' in data:
        e.attacked_last_turn = data['attacked_last_turn']
    if 'diag_dx' in data:
        e.diag_dx = data['diag_dx']
    if 'diag_dy' in data:
        e.diag_dy = data['diag_dy']
    if 'disguised' in data:
        e.disguised = data['disguised']
    return e


def serialize_level(level):
    return {
        'level_number': level.level_number,
        'width': level.width,
        'height': level.height,
        'tiles': level.tiles,
        'rooms': [{'x': r.x, 'y': r.y, 'width': r.width, 'height': r.height}
                  for r in level.rooms],
        'corridors': [{'start': list(c.start), 'end': list(c.end),
                       'cells': [list(cell) for cell in c.cells]}
                      for c in level.corridors],
        'doors': [{'x': d.x, 'y': d.y, 'color': d.subtype} for d in level.doors],
        'player_start': list(level.player_start),
        'exit_position': list(level.exit_position),
        'start_room_index': level.start_room_index,
        'exit_room_index': level.exit_room_index,
        'enemies': [serialize_enemy(e) for e in level.enemies],
        'items': [serialize_item(i) for i in level.items],
    }


def deserialize_level(data):
    lv = Level.__new__(Level)
    lv.level_number = data['level_number']
    lv.width = data['width']
    lv.height = data['height']
    lv.tiles = data['tiles']
    lv.rooms = [Room(r['x'], r['y'], r['width'], r['height']) for r in data['rooms']]
    lv.corridors = []
    for c in data['corridors']:
        corr = Corridor.__new__(Corridor)
        corr.start = tuple(c['start'])
        corr.end = tuple(c['end'])
        corr.cells = [tuple(cell) for cell in c['cells']]
        lv.corridors.append(corr)
    lv.doors = [Door(d['x'], d['y'], d['color']) for d in data['doors']]
    lv.player_start = tuple(data['player_start'])
    lv.exit_position = tuple(data['exit_position'])
    lv.start_room_index = data['start_room_index']
    lv.exit_room_index = data['exit_room_index']
    lv.enemies = [e for e in (deserialize_enemy(e) for e in data['enemies']) if e]
    lv.items = [i for i in (deserialize_item(i) for i in data['items']) if i]
    return lv


def serialize_player(player):
    backpack_data = {}
    for k, items in player.backpack.items.items():
        backpack_data[k] = [serialize_item(i) for i in items]

    weapon_data = serialize_item(player.weapon) if player.weapon else None

    return {
        'x': player.x,
        'y': player.y,
        'health': player.health,
        'max_health': player.max_health,
        'agility': player.agility,
        'strength': player.strength,
        'elixir_effects': [list(e) for e in player.elixir_effects],
        'sleep_counter': getattr(player, 'sleep_counter', 0),
        'weapon': weapon_data,
        'backpack': backpack_data,
        'stats': {
            'treasure': player.stat_treasure,
            'enemies_killed': player.stat_enemies_killed,
            'food_eaten': player.stat_food_eaten,
            'elixirs_drunk': player.stat_elixirs_drunk,
            'scrolls_read': player.stat_scrolls_read,
            'hits': player.stat_hits,
            'misses': player.stat_misses,
            'steps': player.stat_steps,
        }
    }


def deserialize_player_into(player, data):
    player.x = data['x']
    player.y = data['y']
    player.health = data['health']
    player.max_health = data['max_health']
    player.agility = data['agility']
    player.strength = data['strength']
    player.elixir_effects = [tuple(e) for e in data.get('elixir_effects', [])]
    player.sleep_counter = data.get('sleep_counter', 0)

    if data.get('weapon'):
        player.weapon = deserialize_item(data['weapon'])
    else:
        player.weapon = None

    player.backpack = Backpack()
    for item_type, items in data.get('backpack', {}).items():
        for item_data in items:
            item = deserialize_item(item_data)
            if item is not None:
                player.backpack.add_item(item)

    stats = data.get('stats', {})
    player.stat_treasure = stats.get('treasure', 0)
    player.stat_enemies_killed = stats.get('enemies_killed', 0)
    player.stat_food_eaten = stats.get('food_eaten', 0)
    player.stat_elixirs_drunk = stats.get('elixirs_drunk', 0)
    player.stat_scrolls_read = stats.get('scrolls_read', 0)
    player.stat_hits = stats.get('hits', 0)
    player.stat_misses = stats.get('misses', 0)
    player.stat_steps = stats.get('steps', 0)


class SaveManager:
    def has_save(self):
        return os.path.exists(SAVE_FILE)

    def save(self, game):
        data = {
            'current_level': game.current_level,
            'turn': game.turn,
            'difficulty_multiplier': game.difficulty_multiplier,
            'damage_taken_recent': game.damage_taken_recent,
            'view_mode': game.view_mode,
            'player': serialize_player(game.player),
            'level': serialize_level(game.level),
        }
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        if not self.has_save():
            return None
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def clear(self):
        if self.has_save():
            os.remove(SAVE_FILE)