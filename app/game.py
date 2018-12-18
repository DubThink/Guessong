# from app import db
from app.models import Song,Playlist
from difflib import SequenceMatcher
import threading
import time
import random

"""
* game.py
* manages the gamestate of guessong
"""

validchars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"

def clean(s):
    return ''.join(c for c in s if c in validchars)

def similar(a, b):
    """ :returns the similarity of a and b in the range [0:1] """
    fullmatch= SequenceMatcher(None, clean(a.lower()), clean(b.lower())).ratio()
    # only stuff before parenthesis
    partmatch= SequenceMatcher(None, clean(a.lower()), clean(b.lower().split('(')[0])).ratio()
    return max(fullmatch,partmatch)


class GameUser:
    def __init__(self, name):
        self.name = name
        self.score = 0
        # used to prevent people sending correct guesses after they guess correctly
        self.hasGuessedCorrectly = False

    def add_score(self, score):
        if not self.hasGuessedCorrectly:
            self.score += score
            self.hasGuessedCorrectly = True
            return score
        return 0


class GameConstants:
    GUESS_INCORRECT = 'incorrect'
    GUESS_CLOSE = 'close'
    GUESS_CORRECT = 'correct'
    GUESS_ALREADY = 'already'

    WAITING=0
    ROUND_LIVE=1
    ROUND_END=2
    GAME_END=3


class Game:
    def __init__(self, roomcode):

        self.playlist = None
        self.unplayedSongs = []
        self.playedSongs = []
        self.currentSong = None
        self.gameUsers = {}
        self.roomID = roomcode
        self.gameStarted = False
        self.playlistData = None
        self.max_songs = 10
        self.guess_time=10
        self.jumpToEnd=False

        # game state data
        self.startTime = 0
        self.state = GameConstants.WAITING

    def debug_game_state(self):
        """
        prints a bunch of stuff to help with debugging
        """
        print("\nDebugging game state for game <%s>"%self.roomID)
        print(":playlist <%s>"%self.playlist)
        print(":currentSong <%s>"%str(self.currentSong))
        print(":startTime <%f>"%self.startTime)
        print(":time.time() <%f>"%time.time())
        print(":state <%s>"%self.state)
        print()

    def add_user(self, username):
        """ Adds a user by name to the game. Returns false if that username is already taken """
        if username in self.gameUsers:
            print("user already exists")
            return False
        user = GameUser(username)
        self.gameUsers[username]=user
        return True

    def remove_user(self, username):
        """ Removes a user by name from the game. Returns false if the user does not exist in the game. """
        if username not in self.gameUsers:
            # user does not exist, cannot remove
            return False
        self.gameUsers.pop(username)
        return True

    def end_game(self):
        """ Sets the game to an end-game state """
        self.state = GameConstants.GAME_END
        return True

    def check_guess(self, username, guess):
        """ Returns GUESS_CORRECT, GUESS_CLOSE, or GUESS_INCORRECT depending on the guess.
        Returns GUESS_INCORRECT if the specified user does not exist """
        if self.state!=GameConstants.ROUND_LIVE:
            return GameConstants.GUESS_INCORRECT,0
        if username not in self.gameUsers:
            return GameConstants.GUESS_INCORRECT,0
        if self.currentSong is None:
            return 0

        sim = similar(guess,self.currentSong.name)

        if sim > 0.80 and self.gameUsers[username].hasGuessedCorrectly:
            return GameConstants.GUESS_ALREADY,0
        if sim > 0.95:
            score=self.guess_time-int(time.time() - self.startTime)
            score=self.gameUsers[username].add_score(score)
            # if all([a.hasGuessedCorrectly for a in self.gameUsers.values()]):
            #     self.jumpToEnd=True
            return GameConstants.GUESS_CORRECT,score
        if sim > 0.80:
            return GameConstants.GUESS_CLOSE,0
        return GameConstants.GUESS_INCORRECT,0

    def get_song_info(self):
        """ Gets current song object as a dict/json """
        return self.currentSong.toJSON()

    def get_playlist_meta(self):
        """ Gets the metadata of the playlist """
        return self.playlist.toJSON()

    def set_playlist(self, playlist_id):
        """ sets game's playlist. returns false if playlist does not exist """
        if Playlist.query.filter_by(id=playlist_id).first() is None:
            return False
        self.playlist=Playlist.query.filter_by(id=playlist_id).first()
        return True

    def get_players_data(self):
        return [{"name": n.name, "score": n.score} for n in self.gameUsers.values()]

    def start_round(self):
        print("started round")
        self.state=GameConstants.ROUND_LIVE
        self.startTime = time.time()

        for key, gameUser in self.gameUsers.items():
            gameUser.hasGuessedCorrectly=False

        if not self.playlist:
            print("No playlist for room with code",self.roomID,", users",str(self.gameUsers))
        if len(self.unplayedSongs) == 0:
            self.unplayedSongs = list(self.playlist.songs)
            random.shuffle(self.unplayedSongs)
        if self.currentSong:
            self.playedSongs.append(self.currentSong)
        self.currentSong = self.unplayedSongs.pop()
        print("new song:",self.currentSong)

    def finish_round(self):
        self.state=GameConstants.ROUND_END
        if len(self.playedSongs)>=self.max_songs:
            return True
        self.startTime = time.time()
        print('finished round')
        return False

    def reset_game(self):
        for p in self.gameUsers.values():
            p.score=0
        self.playedSongs=[]
        self.currentSong=None

class GameManager:
    roomToGame = {}
    ticking=False
    updateClients=None

    def get_game(self, key):
        if key not in self.roomToGame:
            return None
        return self.roomToGame[key]

    def create_game(self):
        # generate a random unique string of 4 hex chars.
        # Using hex cause unlikely that there'll be a bad word
        # b00b is the only one I can think of
        randcode = '%04X'%random.randint(0,0xFFFF)
        while randcode in self.roomToGame:
            randcode = '%04X' % random.randint(0,0xFFFF)
        game = Game(randcode)
        self.roomToGame[randcode] = game
        print(randcode)
        return game
        
    def start_game(self, key):
        print("starting game")
        if key not in self.roomToGame:
            return False
        self.roomToGame[key].reset_game()
        self.roomToGame[key].start_round()
        self.start_ticking()
        self.updateClients(key, self.roomToGame[key])
        return True

    def end_game(self, key):
        print("ending game")
        if key not in self.roomToGame:
            return False
        self.get_game(key).end_game()
        if len(self.roomToGame) is 0:
            self.stop_ticking()
        return True

    def kill_game(self, key):
        print("killin game")
        if key not in self.roomToGame:
            return False
        self.get_game(key).end_game()
        self.roomToGame.pop(key)
        if len(self.roomToGame) is 0:
            self.stop_ticking()
        return True

    def start_ticking(self):
        print('starting to tick')
        if not self.ticking:
            self.ticking=True  # enable ticking
            self._update_tick()  # start ticking

    def stop_ticking(self):
        self.ticking=False

    def _update_tick(self):
        if self.ticking:
            threading.Timer(1, self._update_tick).start()
        print('ticking...')
        for roomcode, game in list(self.roomToGame.items()):
            if (game.state is GameConstants.ROUND_LIVE and time.time()-game.startTime > game.guess_time) or game.jumpToEnd:
                game.jumpToEnd=False
                killgame = game.finish_round()
                if killgame:
                    self.end_game(game.roomID)
                if self.updateClients:
                    self.updateClients(roomcode, game)
            elif game.state is GameConstants.ROUND_END and time.time()-game.startTime > 8:
                game.start_round()
                if self.updateClients:
                    self.updateClients(roomcode, game)
                return



