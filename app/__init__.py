from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
login = LoginManager(app)
socketio = SocketIO(app)
login.login_view = 'login'

from app import routes, models

