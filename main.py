

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from extensions.database import db
from config import Config
from app.routes.auth import auth_bp
from app.routes.chat import chat_bp
from app.routes.message import message_bp
from app.routes.test2 import test_bp
from app.routes.upload import upload_bp
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True)
    db.init_app(app)
    jwt = JWTManager(app)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(message_bp, url_prefix='/api')
    app.register_blueprint(test_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)