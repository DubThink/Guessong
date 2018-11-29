from time import time

from app.backend import * 
import json
from flask import render_template, flash, redirect, url_for, abort, send_from_directory, request
from flask_socketio import SocketIO, emit, join_room, send
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, socketio
from app.spotifyapi import testspotifyapi
import os
from app.models import User
from werkzeug.urls import url_parse
import requests
import time
ADMIN_ID = 1

socket = SocketIO(app)

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Sam'}
    return render_template('index.html', title='Home', user=user)

@app.route('/resource/<path:path>')
def serve_file(path):
    return send_from_directory('resource', path)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html')

@app.route('/testspotify/<s>')
def testspotify(s):
    return testspotifyapi(s)

@app.route('/testbackend')
def testbackend():
    return render_template('testbackend.html', async_mode=socketio.async_mode)

#Expects message to contain name : the user's name
@socket.on('create_lobby')
def create_lobby(message):
   room = createLobby() 
   joinLobby(room, message['name']) 
   join_room(room)
   print(message['name'])

#Expects message to contain name and room
@socket.on('join_lobby')
def join_lobby(message):
    joinLobby(message['room'], message['name'])
    print('joined ' + message['room'])
    emit('reply', message['name'] + 'has joined the room', broadcast=True)

