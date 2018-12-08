from time import time

import json
from flask import render_template, flash, redirect, url_for, abort, send_from_directory, request, jsonify
from flask_socketio import SocketIO, emit, join_room, send
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, socketio, backend
from app.spotifyapi import testspotifyapi
import os
from app.models import User
from werkzeug.urls import url_parse
import requests
import time
ADMIN_ID = 1

#socket = SocketIO(app)

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

@app.route('/testbackend', methods=["GET", "POST"])
def testbackend():
    return render_template('testbackend.html', async_mode=socketio.async_mode)

@app.route('/game/<create>:<string:name>:<string:room>', methods=["GET", "POST"])
def game(create, name, room):
    return render_template('game.html', async_mode=socketio.async_mode)

@app.route('/create_game', methods=["GET", "POST"])
def creategame():
    if request.method == 'POST':
        return redirect(url_for('game', create=True, name=request.form["name"], room="None"))

@app.route('/join_game', methods=["GET", "POST"])
def joingame():
    if request.method == 'POST':
        return redirect(url_for('game', create=False, name=request.form["name"], room=request.form["room_code"]))

#Expects message to contain name : the user's name
@socketio.on('create_lobby')
def create_lobby(message):
   room = backend.create_lobby()
   print( "created" )
   if not backend.join_lobby(room, message['name']) :
       emit('redirect', {'error_type': 'name'})
   else:
       join_room(room)
       emit('room_code', {'room': room})

#Expects message to contain name and room
@socketio.on('join_lobby')
def join_lobby(message):
    joined = backend.join_lobby(message['room'], message['name'])
    if joined == None: #None means room didn't exist
        emit('redirect', {'error_type': 'room'})
    elif joined == False:
        emit('redirect', {'error_type': 'name'})
    else:
        join_room(message['room'])
        print('joined ' + message['room'])
        emit('join_message', message['name'] + 'has joined the room', room=message['room'])

@socketio.on('chat_message')
def chat_message(message):
   emit('chat_message', message, room=message["room"])

@socketio.on('start_game')
def start_game(message):
    backend.start_game(message["room"], message["username"], message["playlist"], message["song_length"])
    emit('game_started', room=message["room"])

@socketio.on('data_request')
def data_request(message):
    game = backend.get_game(message["room"])
    emit("update_game", game, room=message["room"])

