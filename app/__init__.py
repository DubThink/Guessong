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

from app.game import GameManager
from app import backend
socketio = SocketIO(app)
login.login_view = 'login'
gameManager = GameManager()
gameManager.updateClients = backend.update_game_state

# rest API
from flask_restful import Resource, Api
from app import playlistAPI
restAPI = Api(app)
restAPI.add_resource(playlistAPI.AddPlaylist, '/api/addplaylist')
restAPI.add_resource(playlistAPI.CheckThread, '/api/checkthread')
restAPI.add_resource(playlistAPI.ListPlaylists, '/api/playlists')
restAPI.add_resource(playlistAPI.ManageDatabase, '/api/managedb')
restAPI.add_resource(playlistAPI.ResetDatabase, '/api/resetdb')

from app import routes, models

