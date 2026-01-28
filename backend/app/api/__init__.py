"""API blueprint registration."""
from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")


def register_blueprints(app):
    """Register all API blueprints."""
    from app.api.upload import upload_bp
    from app.api.job import job_bp
    from app.api.result import result_bp
    from app.api.download import download_bp
    from app.api.health import health_bp
    from app.api.files import files_bp

    api_bp.register_blueprint(upload_bp)
    api_bp.register_blueprint(job_bp)
    api_bp.register_blueprint(result_bp)
    api_bp.register_blueprint(download_bp)
    api_bp.register_blueprint(health_bp)
    api_bp.register_blueprint(files_bp)

    app.register_blueprint(api_bp)
