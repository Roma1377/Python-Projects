from abc import ABC, abstractmethod
from uuid import UUID

from domain.model.board import Board
from domain.model.game import Game


class GameService(ABC):
    @abstractmethod
    def get_next_move(self, game_uuid: UUID, board: Board) -> Game:
        pass

    @abstractmethod
    def validate_board(self, game_uuid: UUID, board: Board) -> None:
        pass

    @abstractmethod
    def is_game_over(self, board: Board) -> bool:
        pass