from uuid import UUID

from datasource.mapper.game_mapper import GameMapper
from datasource.repository.game_repository import GameRepository
from datasource.storage import GameStorage
from domain.model.game import Game


class GameRepositoryImpl(GameRepository):
    def __init__(self, storage: GameStorage) -> None:
        self._storage = storage

    def save(self, game: Game) -> None:
        self._storage.save(GameMapper.to_datasource(game))

    def get(self, uuid: UUID) -> Game:
        model = self._storage.get(uuid)
        if model is None:
            raise ValueError(f"Игра с UUID {uuid} не найдена в хранилище")
        return GameMapper.to_domain(model)