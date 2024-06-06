import os
from flask import Flask, render_template, send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    if not os.path.exists(app.config['UPLOADED_PHOTOS_DEST']):
        os.makedirs(app.config['UPLOADED_PHOTOS_DEST'])

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.main import main as main_bp
    app.register_blueprint(main_bp)

    from app.auth import auth_bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.route('/media/<path:filename>')
    def media(filename):
        return send_from_directory(current_app.config['UPLOADED_PHOTOS_DEST'], filename)

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        return render_template("500.html", error=e), 500

    return app