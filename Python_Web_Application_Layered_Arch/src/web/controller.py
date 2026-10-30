from uuid import UUID, uuid4

from domain.model.board import Board
from domain.model.game import Game
from domain.service.game_service import GameService
from web.mapper.board_mapper import BoardMapper
from web.mapper.game_mapper import GameMapper


class GameController:
    def __init__(self, service: GameService) -> None:
        self._service = service

    def create_game(self) -> dict:
        new_game = Game(uuid=uuid4(), board=Board())
        self._service._repository.save(new_game)
        return {"uuid": str(new_game.uuid)}

    def make_move(self, game_uuid: UUID, payload: dict) -> dict:
        board_dto = GameMapper.board_from_payload(payload)
        board = BoardMapper.to_domain(board_dto)
        updated = self._service.get_next_move(game_uuid, board)
        return {
            "uuid": str(updated.uuid),
            "board": [row[:] for row in updated.board.cells],
        }