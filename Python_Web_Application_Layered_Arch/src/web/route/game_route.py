from uuid import UUID

from flask import Blueprint, jsonify, request

from web.controller import GameController


def create_game_route_blueprint(controller: GameController) -> Blueprint:
    blueprint = Blueprint("game", __name__)

    @blueprint.route("/game", methods=["POST"])
    def create_game():
        result = controller.create_game()
        return jsonify(result), 201

    @blueprint.route("/game/<uuid:game_uuid>", methods=["POST"])
    def make_move(game_uuid: UUID):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or "board" not in payload:
            return jsonify({"error": "Поле 'board' обязательно"}), 400
        try:
            result = controller.make_move(game_uuid, payload)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": f"Внутренняя ошибка: {exc}"}), 500
        return jsonify(result), 200

    return blueprint