
import random


def _find_free_neighbor(x, y, level):
    
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        occupied_by_enemy = any(e.x == nx and e.y == ny for e in level.enemies)
        occupied_by_item = any(i.x == nx and i.y == ny for i in level.items)
        if not occupied_by_enemy and not occupied_by_item:
            return nx, ny
    return x, y


def use_food(player, food):
    
    player.health = min(player.max_health, player.health + food.health)
    player.stat_food_eaten += 1


def use_elixir(player, elixir, duration=10):
    
    if elixir.subtype == 'agility':
        player.agility += elixir.agility
        player.elixir_effects.append(('agility', elixir.agility, duration))
    elif elixir.subtype == 'strength':
        player.strength += elixir.strength
        player.elixir_effects.append(('strength', elixir.strength, duration))
    elif elixir.subtype == 'max_health':
        player.max_health += elixir.max_health
        player.health += elixir.max_health
        player.elixir_effects.append(('max_health', elixir.max_health, duration))
    player.stat_elixirs_drunk += 1


def use_scroll(player, scroll):
    
    if scroll.subtype == 'agility':
        player.agility += scroll.agility
    elif scroll.subtype == 'strength':
        player.strength += scroll.strength
    elif scroll.subtype == 'max_health':
        player.max_health += scroll.max_health
        player.health += scroll.max_health
    player.stat_scrolls_read += 1


def use_weapon(player, weapon, level):
    
    if player.weapon is not None:
        drop_x, drop_y = _find_free_neighbor(player.x, player.y, level)
        player.weapon.x = drop_x
        player.weapon.y = drop_y
        level.add_item(player.weapon)
    player.weapon = weapon
    return weapon


def unequip_weapon(player):
    
    if player.weapon is None:
        return False
    if player.backpack.add_item(player.weapon):
        player.weapon = None
        return True
    return False


def tick_elixir_effects(player):
    
    remaining = []
    for stat_name, value, turns_left in player.elixir_effects:
        turns_left -= 1
        if turns_left <= 0:
            if stat_name == 'agility':
                player.agility -= value
                if player.agility < 1:
                    player.agility = 1
            elif stat_name == 'strength':
                player.strength -= value
                if player.strength < 1:
                    player.strength = 1
            elif stat_name == 'max_health':
                player.max_health -= value
                if player.max_health < 1:
                    player.max_health = 1
                if player.health > player.max_health:
                    player.health = player.max_health
        else:
            remaining.append((stat_name, value, turns_left))
    player.elixir_effects = remaining

    if player.health <= 0:
        player.health = 1