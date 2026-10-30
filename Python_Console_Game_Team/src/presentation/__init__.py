


class UI:
    def __init__(self, renderer):
        self.renderer = renderer

    def draw_inventory(self, player):
        
        stdscr = self.renderer.stdscr
        stdscr.clear()
        stdscr.addstr(0, 0, "=== INVENTORY ===")

        row = 2
        for item_type in ('weapon', 'food', 'elixir', 'scroll', 'key'):
            items = player.backpack.get_items(item_type)
            stdscr.addstr(row, 0, f"{item_type.upper()} ({len(items)}):")
            row += 1
            for i, item in enumerate(items, 1):
                label = item.name
                if item.subtype:
                    label += f" [{item.subtype}]"
                stdscr.addstr(row, 4, f"{i}. {label}")
                row += 1

        treasures = player.backpack.get_items('treasure')
        stdscr.addstr(row + 1, 0,
                      f"Treasure count: {len(treasures)} | Total cost: {player.stat_treasure}")
        stdscr.addstr(row + 3, 0, "Press any key to return...")
        stdscr.refresh()
        stdscr.getkey()

    def draw_stats(self, stats_manager):
        
        stdscr = self.renderer.stdscr
        stdscr.clear()
        stdscr.addstr(0, 0, "=== LEADERBOARD ===")
        leaders = stats_manager.get_leaderboard()
        if not leaders:
            stdscr.addstr(2, 0, "No records yet.")
        else:
            header = f"{'#':<3} {'Treasure':<10} {'Level':<7} {'Kills':<7} {'Food':<6} {'Elix':<6} {'Scroll':<7} {'Hits':<6} {'Miss':<6} {'Steps':<6}"
            stdscr.addstr(2, 0, header)
            for i, rec in enumerate(leaders[:10], 1):
                line = (f"{i:<3} {rec.get('treasure', 0):<10} "
                        f"{rec.get('level', 0):<7} "
                        f"{rec.get('enemies_killed', 0):<7} "
                        f"{rec.get('food_eaten', 0):<6} "
                        f"{rec.get('elixirs_drunk', 0):<6} "
                        f"{rec.get('scrolls_read', 0):<7} "
                        f"{rec.get('hits', 0):<6} "
                        f"{rec.get('misses', 0):<6} "
                        f"{rec.get('steps', 0):<6}")
                stdscr.addstr(3 + i, 0, line)
        stdscr.addstr(self.renderer.height - 2, 0, "Press any key to return...")
        stdscr.refresh()
        stdscr.getkey()

    def draw_help(self):
        
        stdscr = self.renderer.stdscr
        stdscr.clear()
        stdscr.addstr(0, 0, "=== CONTROLS ===")
        stdscr.addstr(2, 0, "w/a/s/d - move")
        stdscr.addstr(3, 0, "h       - weapon menu (0 to unequip)")
        stdscr.addstr(4, 0, "j       - eat food")
        stdscr.addstr(5, 0, "k       - drink elixir")
        stdscr.addstr(6, 0, "e       - read scroll")
        stdscr.addstr(7, 0, "i       - inventory")
        stdscr.addstr(8, 0, "l       - leaderboard")
        stdscr.addstr(9, 0, "q       - quit")
        stdscr.addstr(11, 0, "Goal: reach the exit '@' on the last room of each level.")
        stdscr.addstr(12, 0, "Collect treasure, fight monsters, survive 21 levels.")
        stdscr.addstr(self.renderer.height - 2, 0, "Press any key to return...")
        stdscr.refresh()
        stdscr.getkey()