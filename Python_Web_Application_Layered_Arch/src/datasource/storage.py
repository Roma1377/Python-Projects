import threading
from queue import Queue
from typing import Optional
from uuid import UUID

from datasource.model.game import GameModel


class GameStorage:
    def __init__(self) -> None:
        self._games: Queue = Queue()
        self._lock: threading.Lock = threading.Lock()

    def save(self, game: GameModel) -> None:
        with self._lock:
            size = self._games.qsize()
            for _ in range(size):
                existing = self._games.get()
                if existing.uuid != game.uuid:
                    self._games.put(existing)
            self._games.put(game)

    def get(self, uuid: UUID) -> Optional[GameModel]:
        with self._lock:
            size = self._games.qsize()
            result: Optional[GameModel] = None
            for _ in range(size):
                g = self._games.get()
                if g.uuid == uuid:
                    result = g
                self._games.put(g)
            return result