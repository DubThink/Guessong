from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time

class PlaylistScore(db.Model):
    __tablename__='playlistscore'
    # id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
    timestamp = db.Column(db.Integer)
    score = db.Column(db.Integer)

    user = db.relationship("User",back_populates="scores")
    playlist=db.relationship("Playlist",back_populates="scores")

    def __repr__(self):
        return '<PlaylistScore {} {} {} {}>'.format(self.user_id,self.team_id,self.score,self.timestamp)

class PlaylistSong(db.Model):
    __tablename__='playlistsong'
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)

    song = db.relationship("User",back_populates="playlists")
    playlist=db.relationship("Playlist",back_populates="songs")

    def __repr__(self):
        return '<PlaylistSong {} {} {} {}>'.format(self.user_id,self.team_id,self.score,self.timestamp)

class User(UserMixin,db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    email = db.Column(db.String(120), index=True)
    password_hash = db.Column(db.String(128))

    scores = db.relationship("PlaylistScore",back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {} {} {}>'.format(self.id,self.username,self.email)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Playlist(db.Model):
    __tablename__='playlist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    thumbnail = db.Column(db.String(256))

    spotifyid = db.Column(db.String(1024))

    scores = db.relationship("PlaylistScore",back_populates="playlist")
    songs = db.relationship("PlaylistSongs",back_populates="playlist")

    def __repr__(self):
        return '<Playlist {}>'.format(self.name)

class Song(db.Model):
    __tablename__='song'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    artist = db.Column(db.String(256), index=True)
    thumbnail_url = db.Column(db.String(256))
    preview_url = db.Column(db.String(256))
    external_url = db.Column(db.String(256))

    playlists = db.relationship("PlaylistSongs",back_populates="song")
