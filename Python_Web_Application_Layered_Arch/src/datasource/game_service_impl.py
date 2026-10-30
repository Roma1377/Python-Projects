from typing import Optional, Tuple
from uuid import UUID

from datasource.repository.game_repository import GameRepository
from domain.model.board import Board, BOARD_SIZE, COMPUTER, EMPTY, PLAYER
from domain.model.game import Game
from domain.service.game_service import GameService


class GameServiceImpl(GameService):
    def __init__(self, repository: GameRepository) -> None:
        self._repository = repository

    def get_next_move(self, game_uuid: UUID, board: Board) -> Game:
        self.validate_board(game_uuid, board)
        self._validate_turn_order(board)

        new_board = board.copy()
        if not self.is_game_over(new_board):
            move = self._minimax_move(new_board)
            if move is not None:
                row, col = move
                new_board.set_cell(row, col, COMPUTER)

        updated = Game(uuid=game_uuid, board=new_board)
        self._repository.save(updated)
        return updated

    def validate_board(self, game_uuid: UUID, board: Board) -> None:
        self._check_shape(board)
        self._check_values(board)
        current = self._repository.get(game_uuid)
        if not self._previous_moves_preserved(current.board, board):
            raise ValueError(
                "Нельзя изменять предыдущие ходы: значения клеток, "
                "установленные ранее, должны оставаться неизменными"
            )

    def is_game_over(self, board: Board) -> bool:
        return board.get_winner() is not None or board.is_full()

    @staticmethod
    def _check_shape(board: Board) -> None:
        if not isinstance(board.cells, list) or len(board.cells) != BOARD_SIZE:
            raise ValueError(
                f"Игровое поле должно быть матрицей {BOARD_SIZE}x{BOARD_SIZE}"
            )
        for row in board.cells:
            if not isinstance(row, list) or len(row) != BOARD_SIZE:
                raise ValueError(
                    f"Каждая строка поля должна иметь длину {BOARD_SIZE}"
                )

    @staticmethod
    def _check_values(board: Board) -> None:
        allowed = {EMPTY, PLAYER, COMPUTER}
        for r, row in enumerate(board.cells):
            for c, cell in enumerate(row):
                if cell not in allowed:
                    raise ValueError(
                        f"Недопустимое значение в клетке ({r},{c}): {cell}. "
                        f"Разрешены только {allowed}"
                    )

    @staticmethod
    def _previous_moves_preserved(old: Board, new: Board) -> bool:
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if old.cells[r][c] != EMPTY and old.cells[r][c] != new.cells[r][c]:
                    return False
        return True

    @staticmethod
    def _validate_turn_order(board: Board) -> None:
        players = sum(cell == PLAYER for row in board.cells for cell in row)
        computers = sum(cell == COMPUTER for row in board.cells for cell in row)
        if players - computers not in (0, 1):
            raise ValueError(
                f"Некорректное количество ходов: игрок={players}, "
                f"компьютер={computers}"
            )

    def _minimax_move(self, board: Board) -> Optional[Tuple[int, int]]:
        best_score = float("-inf")
        best_move: Optional[Tuple[int, int]] = None
        for row, col in board.get_empty_cells():
            board.set_cell(row, col, COMPUTER)
            score = self._minimax(board, depth=0, maximizing=False)
            board.set_cell(row, col, EMPTY)
            if score > best_score:
                best_score = score
                best_move = (row, col)
        return best_move

    def _minimax(self, board: Board, depth: int, maximizing: bool) -> int:
        winner = board.get_winner()
        if winner == COMPUTER:
            return 10 - depth
        if winner == PLAYER:
            return depth - 10
        if board.is_full():
            return 0
        if maximizing:
            best = float("-inf")
            for row, col in board.get_empty_cells():
                board.set_cell(row, col, COMPUTER)
                best = max(best, self._minimax(board, depth + 1, False))
                board.set_cell(row, col, EMPTY)
            return best
        best = float("inf")
        for row, col in board.get_empty_cells():
            board.set_cell(row, col, PLAYER)
            best = min(best, self._minimax(board, depth + 1, True))
            board.set_cell(row, col, EMPTY)
        return best