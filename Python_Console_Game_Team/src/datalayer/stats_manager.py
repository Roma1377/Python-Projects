import json
import os

STATS_FILE = "stats.json"


class StatsManager:
    def __init__(self):
        self.stats = self._load()

    def _load(self):
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def add_result(self, treasure, level, enemies_killed, food_eaten,
                   elixirs_drunk, scrolls_read, hits, misses, steps):
        self.stats.append({
            'treasure': treasure,
            'level': level,
            'enemies_killed': enemies_killed,
            'food_eaten': food_eaten,
            'elixirs_drunk': elixirs_drunk,
            'scrolls_read': scrolls_read,
            'hits': hits,
            'misses': misses,
            'steps': steps,
        })
        self.stats.sort(key=lambda x: x['treasure'], reverse=True)
        self._save()

    def _save(self):
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def get_leaderboard(self):
        return self.stats