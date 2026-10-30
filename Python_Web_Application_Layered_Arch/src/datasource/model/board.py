from dataclasses import dataclass, field
from typing import List

BOARD_SIZE = 3


@dataclass
class BoardModel:
    cells: List[List[int]] = field(
        default_factory=lambda: [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    )