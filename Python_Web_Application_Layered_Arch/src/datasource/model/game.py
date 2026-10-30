from dataclasses import dataclass, field
from uuid import UUID

from datasource.model.board import BoardModel


@dataclass
class GameModel:
    uuid: UUID
    board: BoardModel = field(default_factory=BoardModel)