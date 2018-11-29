from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, emit
from app.game import GameManager
from app import backend

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
login = LoginManager(app)
socketio = SocketIO(app)
login.login_view = 'login'
gameManager = GameManager()
gameManager.updateClients = backend.updateGameState

from app import routes, models

