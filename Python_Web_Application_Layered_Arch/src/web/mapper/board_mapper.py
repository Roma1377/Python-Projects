from domain.model.board import Board
from web.model.board import BoardDto


class BoardMapper:
    @staticmethod
    def to_web(board: Board) -> BoardDto:
        return BoardDto(cells=[row[:] for row in board.cells])

    @staticmethod
    def to_domain(dto: BoardDto) -> Board:
        return Board(cells=[row[:] for row in dto.cells])