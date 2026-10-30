from domain.model.game import Game
from web.mapper.board_mapper import BoardMapper
from web.model.board import BoardDto
from web.model.game import GameDto


class GameMapper:
    @staticmethod
    def to_web(game: Game) -> GameDto:
        return GameDto(uuid=game.uuid, board=BoardMapper.to_web(game.board))

    @staticmethod
    def to_domain(dto: GameDto) -> Game:
        return Game(uuid=dto.uuid, board=BoardMapper.to_domain(dto.board))

    @staticmethod
    def board_from_payload(payload: dict) -> BoardDto:
        if "board" not in payload:
            raise ValueError("В теле запроса отсутствует поле 'board'")
        raw = payload["board"]
        if not isinstance(raw, list):
            raise ValueError("Поле 'board' должно быть списком строк")
        try:
            cells = [[int(cell) for cell in row] for row in raw]
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Некорректные значения в поле 'board': {exc}"
            ) from exc
        return BoardDto(cells=cells)