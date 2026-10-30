
import random
from domain.entities import Vampire, Ghost, Ogre, SnakeMage, Mimic


def hit_chance(attacker_agility, defender_agility):
    
    total = attacker_agility + defender_agility
    if total <= 0:
        return 0.5
    return attacker_agility / total


def calculate_damage(attacker):
    
    base = attacker.strength
    if attacker.weapon is not None:
        base += attacker.weapon.strength
    return base


def attack(attacker, defender):
    
    if random.random() > hit_chance(attacker.agility, defender.agility):
        return False, 0
    damage = calculate_damage(attacker)
    defender.health -= damage
    return True, damage


def player_attack(player, enemy):
    
    hit, damage = attack(player, enemy)
    if hit:
        player.stat_hits += 1
    else:
        player.stat_misses += 1
    return hit, damage


def enemy_attack(enemy, player):
    
    hit, damage = attack(enemy, player)

    if not hit:
        return False, 0

    
    if isinstance(enemy, Vampire):
        player.max_health -= 2
        if player.max_health < 1:
            player.max_health = 1
        if player.health > player.max_health:
            player.health = player.max_health

    
    if isinstance(enemy, SnakeMage):
        if random.random() < 0.3:
            player.sleep_counter = 1

    return True, damage