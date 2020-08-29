from flask import Flask, redirect
from flask_cors import CORS
import logging
from marshmallow.exceptions import ValidationError
from . import Environment
from . extensions import db, filtr
from . config import Config
from . api import blueprint as api_v1
from . util import error


logger = logging.getLogger(__name__)


def create_app(env='prd') -> Flask:
    """ application factory creates and configures app """
    app = Flask(__name__)
    configure_app(app, env)
    register_extensions(app)
    setup_db(app)
    register_error_handlers(app)
    register_blueprints(app)
    add_special_routes(app)
    return app


def configure_app(app: Flask, env: str) -> None:
    config = Config.get(env)
    app.config.from_object(config)
    app.logger.setLevel(logging.INFO)
    Environment.set(config.ENV)


def register_blueprints(app: Flask):
    app.register_blueprint(api_v1, url_prefix="/api/v1")


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    filtr.init_app(app)
    CORS(app)


def setup_db(app: Flask) -> None:
    if app.config.get('CREATE_SCHEMA'):
        logger.warning("Setting up local database for development work!")
        with app.app_context():
            try:
                db.create_all()
                logger.warning(f"CREATE DATABASE @ {app.config.get('SQLALCHEMY_DATABASE_URI')}")
            except:
                logger.error(f"Database creation failed. It probably already exists")


def add_special_routes(app: Flask):
    @app.route("/swagger")
    def swagger():
        return redirect("/api/v1")


def register_error_handlers(app: Flask) -> None:

    @app.errorhandler(ValidationError)
    def validation_error_handler(err):
        logger.error("marshmallow validation error", err)
        return error(422, [{"message": "Validation error", "details": str(err)}])

    @app.errorhandler(Exception)
    def generic_error_handler(err):
        logger.error("unhandled application exception", err)
        code = getattr(err, "status_code", 500)
        message = getattr(err, "messages", "uncaught exception")
        return error(code, [dict(message=message, details=str(err))])
