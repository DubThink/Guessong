from flask_wtf import FlaskForm
from wtforms import *
import wtforms.validators as val
import requests
import json
from app.models import User

class GameLobby(FlaskForm):
    playlist = StringField('Playlist', validators=[DataRequired()])
    start = SubmitField('Start Game')
