from datasource.repository.game_repository_impl import GameRepositoryImpl
from datasource.storage import GameStorage
from datasource.game_service_impl import GameServiceImpl


class Container:
    def __init__(self) -> None:
        self._storage: GameStorage = GameStorage()
        self._repository: GameRepositoryImpl = GameRepositoryImpl(self._storage)
        self._service: GameServiceImpl = GameServiceImpl(self._repository)

    @property
    def storage(self) -> GameStorage:
        return self._storage

    @property
    def repository(self) -> GameRepositoryImpl:
        return self._repository

    @property
    def service(self) -> GameServiceImpl:
        return self._service