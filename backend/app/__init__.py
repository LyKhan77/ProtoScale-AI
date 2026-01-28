"""Flask application factory."""
import os
from flask import Flask, jsonify
from flask_cors import CORS

from app.config import get_config


def create_app(config_name: str = None) -> Flask:
    """Create and configure Flask application.

    Args:
        config_name: Configuration name (development, production, testing)

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    config = get_config()
    app.config.from_object(config)

    # Additional config from object
    app.config["REDIS_URL"] = config.REDIS_URL
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

    # Enable CORS - allow all origins in development
    # For production, restrict to specific domains
    cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    # Initialize extensions
    from app.extensions import init_redis
    init_redis(app)

    # Register blueprints
    from app.api import register_blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Create storage directories
    config.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    config.JOBS_DIR.mkdir(parents=True, exist_ok=True)
    config.EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    return app


def register_error_handlers(app: Flask):
    """Register custom error handlers."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request", "message": str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found", "message": str(error)}), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({"error": "File too large", "message": "Maximum file size exceeded"}), 413

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error", "message": str(error)}), 500

    from app.utils.errors import AppError

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify(error.to_dict()), error.status_code
