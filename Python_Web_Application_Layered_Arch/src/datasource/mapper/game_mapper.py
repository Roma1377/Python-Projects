from datasource.mapper.board_mapper import BoardMapper
from datasource.model.game import GameModel
from domain.model.game import Game


class GameMapper:
    @staticmethod
    def to_datasource(game: Game) -> GameModel:
        return GameModel(
            uuid=game.uuid,
            board=BoardMapper.to_datasource(game.board),
        )

    @staticmethod
    def to_domain(model: GameModel) -> Game:
        return Game(
            uuid=model.uuid,
            board=BoardMapper.to_domain(model.board),
        )