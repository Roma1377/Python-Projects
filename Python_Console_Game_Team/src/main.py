#!/usr/bin/env python3.10

import curses
import sys

from presentation.curses_renderer import CursesRenderer
from domain.game import Game
from datalayer.save_manager import SaveManager
from datalayer.stats_manager import StatsManager


MIN_WIDTH = 60
MIN_HEIGHT = 20


def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.nodelay(False)

    height, width = stdscr.getmaxyx()
    if height < MIN_HEIGHT or width < MIN_WIDTH:
        stdscr.clear()
        try:
            stdscr.addstr(0, 0, f"Terminal too small. Minimum: {MIN_WIDTH}x{MIN_HEIGHT}.")
            stdscr.addstr(1, 0, "Press any key to exit.")
        except curses.error:
            pass
        stdscr.refresh()
        stdscr.getkey()
        return

    renderer = CursesRenderer(stdscr)
    save_manager = SaveManager()
    stats_manager = StatsManager()

    game = Game(renderer, save_manager, stats_manager)

    if save_manager.has_save():
        if renderer.ask_continue():
            try:
                game.load_session()
            except Exception:
                save_manager.clear()
                game.start_new_game()
        else:
            save_manager.clear()
            game.start_new_game()
    else:
        game.start_new_game()

    game.run()


def entry():
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f"Fatal error: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise

if __name__ == "__main__":
    entry()