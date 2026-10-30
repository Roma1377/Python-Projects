from flask import Blueprint

from di.container import Container
from web.controller import GameController
from web.route.game_route import create_game_route_blueprint


def create_game_blueprint(container: Container) -> Blueprint:
    controller = GameController(container.service)
    return create_game_route_blueprint(controller)