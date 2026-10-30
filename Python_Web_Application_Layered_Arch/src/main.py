from flask import Flask, send_from_directory
import os

from di.container import Container
from web.module.game_module import create_game_blueprint


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    container = Container()
    app.register_blueprint(create_game_blueprint(container))

    @app.route("/", methods=["GET"])
    def index():
        return send_from_directory(os.path.dirname(__file__), "index.html")

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)