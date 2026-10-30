from abc import ABC, abstractmethod
from uuid import UUID

from domain.model.game import Game


class GameRepository(ABC):
    @abstractmethod
    def save(self, game: Game) -> None:
        pass

    @abstractmethod
    def get(self, uuid: UUID) -> Game:
        pass