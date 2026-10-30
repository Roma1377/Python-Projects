from dataclasses import dataclass, field
from uuid import UUID, uuid4

from domain.model.board import Board


@dataclass
class Game:
    uuid: UUID = field(default_factory=uuid4)
    board: Board = field(default_factory=Board)