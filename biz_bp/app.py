"""LocalLens Flask application entry point."""

from __future__ import annotations

import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from blueprints.auth.auth import auth_bp
from blueprints.businesses.businesses import businesses_bp
from blueprints.reviews.reviews import reviews_bp
from globals import DB_NAME, ensure_indexes


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(auth_bp)
    app.register_blueprint(businesses_bp)
    app.register_blueprint(reviews_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "database": DB_NAME})

    @app.cli.command("init-db")
    def init_db_command():
        """Create MongoDB indexes used by the API."""
        ensure_indexes()
        print("MongoDB indexes created.")

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception):
        app.logger.exception("Unhandled application error")
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )