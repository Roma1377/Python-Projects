from dataclasses import dataclass
from uuid import UUID

from web.model.board import BoardDto


@dataclass
class GameDto:

    uuid: UUID
    board: BoardDto
