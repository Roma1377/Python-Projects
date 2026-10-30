from dataclasses import dataclass, field
from typing import List, Optional, Tuple

EMPTY: int = 0
PLAYER: int = 1
COMPUTER: int = 2
BOARD_SIZE: int = 3


@dataclass
class Board:
    cells: List[List[int]] = field(
        default_factory=lambda: [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    )

    def copy(self) -> "Board":
        return Board(cells=[row[:] for row in self.cells])

    def get_cell(self, row: int, col: int) -> int:
        return self.cells[row][col]

    def set_cell(self, row: int, col: int, value: int) -> None:
        self.cells[row][col] = value

    def get_empty_cells(self) -> List[Tuple[int, int]]:
        return [
            (r, c)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if self.cells[r][c] == EMPTY
        ]

    def is_full(self) -> bool:
        return all(cell != EMPTY for row in self.cells for cell in row)

    def get_winner(self) -> Optional[int]:
        for line in self._get_all_lines():
            first = line[0]
            if first != EMPTY and first == line[1] == line[2]:
                return first
        return None

    def _get_all_lines(self) -> List[List[int]]:
        lines: List[List[int]] = []
        for i in range(BOARD_SIZE):
            lines.append([self.cells[i][c] for c in range(BOARD_SIZE)])
            lines.append([self.cells[r][i] for r in range(BOARD_SIZE)])
        lines.append([self.cells[i][i] for i in range(BOARD_SIZE)])
        lines.append([self.cells[i][BOARD_SIZE - 1 - i] for i in range(BOARD_SIZE)])
        return lines