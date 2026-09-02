import os

from flask import Flask, render_template, request
from sqlalchemy import inspect


from config import config
from controllers.search_controller import SearchController
from data.models import db
from scripts.data_importer import DataImporter
from utils.logger import setup_logging


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)

    app.config.from_object(config[config_name])

    setup_logging(
        level=app.config.get("LOG_LEVEL", "INFO"), log_file=app.config.get("LOG_FILE")
    )

    db.init_app(app)

    register_routes(app)

    initialize_data(app)

    return app


def register_routes(app):
    search_controller = SearchController(app.config)

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            return search_controller.handle_search_request()
        else:
            return search_controller.handle_search_page()

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500


def initialize_data(app):
    try:
        with app.app_context():
            from data.models import Vehicle

            inspector = inspect(db.engine)

            if 'vehicles' not in inspector.get_table_names():
                db.create_all()
                app.logger.info("Vehicle table created successfully")
                if not Vehicle.query.first():
                    importer = DataImporter(app.config)
                    success = importer.import_inventory_data(app)

                    if success:
                        app.logger.info("Data initialization completed successfully")
                    else:
                        app.logger.error("Data initialization failed")
                else:
                    app.logger.info("Data already exists, skipping initialization")

    except Exception as e:
        app.logger.error(f"Error during data initialization: {str(e)}")


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
