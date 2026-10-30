from datasource.model.board import BoardModel
from domain.model.board import Board


class BoardMapper:
    @staticmethod
    def to_datasource(board: Board) -> BoardModel:
        return BoardModel(cells=[row[:] for row in board.cells])

    @staticmethod
    def to_domain(model: BoardModel) -> Board:
        return Board(cells=[row[:] for row in model.cells])