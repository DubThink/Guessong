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
@socket.on('create_lobby')
def create_lobby(message):
   room = createLobby() 
   if not joinLobby(room, message['name']) :
       emit('redirect', {'error_type': 'name'})
   else:
       join_room(room)
       emit('room_code', {'room': room})

#Expects message to contain name and room
@socket.on('join_lobby')
def join_lobby(message):
    joined = joinLobby(message['room'], message['name'])
    if joined == None: #None means room didn't exist
        emit('redirect', {'error_type': 'room'})
    elif joined == False:
        emit('redirect', {'error_type': 'name'})
    else:
        join_room(message['room'])
        print('joined ' + message['room'])
        emit('join_message', message['name'] + 'has joined the room', room=message['room'])

@socket.on('chat_message')
def chat_message(message):
   emit( 'chat_message', message, room=message["room"]);

@socket.on('start_game')
def start_game(message):
    print(message)
