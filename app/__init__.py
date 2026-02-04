import pymysql
from flask import Flask
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Create DB connection
    app.db = pymysql.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASS'],
        database=app.config['DB_NAME'],
        cursorclass=pymysql.cursors.DictCursor
    )

    from .controllers.profileController import profile_bp
    app.register_blueprint(profile_bp)

    from .controllers.indexController import index_bp
    app.register_blueprint(index_bp)

    return app
