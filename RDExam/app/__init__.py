from flask import Flask, render_template, send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
import logging
from logging.handlers import RotatingFileHandler

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/library.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Library startup')



from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    return render_template("500.html", error=e), 500

from app import routes, models

if __name__ == '__main__':
    app.run(debug=True)
