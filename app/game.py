from app import itunesapi as musicapi
from difflib import SequenceMatcher
import threading
import time
import random

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class GameUser:
    name = ""
    score = 0
    # used to prevent people sending correct guesses after they guess correctly
    hasGuessedCorrectly=False

    def __init__(self, name):
        self.name = name

    def addScore(self,score):
        if not self.hasGuessedCorrectly:
            self.score += score
        self.hasGuessedCorrectly = True


GUESS_INCORRECT = 'incorrect'
GUESS_CLOSE = 'close'
GUESS_CORRECT = 'correct'

WAITING=0
ROUND_LIVE=1
ROUND_END=2
GAME_END=3

class Game:
    playlistID = None
    unplayedSongs = []
    playedSongs = []
    currentSong=None
    gameUsers = {}
    roomID = "tacocode"
    gameStarted = False
    playlistData = None
    max_songs=4

    # game state data
    startTime=0
    state=WAITING

    def __init__(self,roomcode):
        self.roomID=roomcode

    def addUser(self, username):
        if username in self.gameUsers:
            # user already exists
            return False
        user = GameUser( username)
        self.gameUsers[username]=user
        return True

    def removeUser(self, username):
        if username not in self.gameUsers:
            # user does not exist, cannot remove
            return False
        self.gameUsers.pop(username)
        return True
    
    def endGame(self):
        self.state = GAME_END
        return True

    def checkGuess(self, username, guess):
        if username not in self.gameUsers:
            return GUESS_INCORRECT
        if self.currentSong is None:
            return 0
        sim = similar(guess,self.currentSong['name'])>0.9
        if sim > 0.95:
            self.gameUsers[username].addScore(int(time.time()-self.startTime))
            return GUESS_CORRECT
        if sim > 0.80:
            return GUESS_CLOSE
        return GUESS_INCORRECT

    def getSongInfo(self):
        return self.currentSong

    def getPlaylistMeta(self):
        if self.playlistData is None:
            return None
        try:
            return { 'name' : self.playlistData['name'],
                   'thumbnail' : self.playlistData['images'][0]['url'],
                   'link' : self.playlistData['external_urls']['spotify']}
        except KeyError as e:
            return None

    def setPlaylist(self, playlist_id):
        self.playlistID = playlist_id

        return True

    def getPlayersData(self):
        return {{"name":n.name,"score":n.score} for n in self.gameUsers.items()}

    def startRound(self):
        self.state=ROUND_LIVE
        self.startTime = time.time()

        for gameUser in self.gameUsers:
            gameUser.hasGuessedCorrectly=False

        if len(self.unplayedSongs) == 0:
            self.unplayedSongs = musicapi.getPlaylist(self.playlistID)
            random.shuffle(self.unplayedSongs)
        if self.currentSong:
            self.playedSongs.append(self.currentSong)
        self.currentSong = self.unplayedSongs.pop()



    def finishRound(self):
        self.state=ROUND_END
        if len(self.playedSongs)>=self.max_songs:
            return True
        self.startTime = time.time()
        return False

class GameManager:
    roomToGame = {}
    ticking=False
    updateClients=None

    def getGame(self, key):
        if key not in self.roomToGame:
            return None
        return self.roomToGame[key]

    def createGame(self):
        # generate a random unique string of 4 hex chars.
        # Using hex cause unlikely that there'll be a bad word
        # b00b is the only one I can think of
        randcode = '%04x'%random.randint(0,0xFFFF)
        while randcode in self.roomToGame:
            randcode = '%04x' % random.randint(0,0xFFFF)
        game = Game(randcode)
        self.roomToGame[randcode] = game
        return game
        
    def startGame(self, key):
        if key in self.roomToGame:
            return False
        self.roomToGame[key].nextRound()
        self.startTicking()
        return True

    def endGame(self, key):
        if key not in self.roomToGame:
            return False
        self.getGame(key).endGame()
        self.roomToGame.pop(key)
        if len(self.roomToGame) is 0:
            self.stopTicking()
        return True

    def startTicking(self):
        print('starting to tick')
        if not self.ticking:
            self.ticking=True  # enable ticking
            self._updateTick()  # start ticking

    def stopTicking(self):
        self.ticking=False

    def _updateTick(self):
        if self.ticking:
            threading.Timer(1, self._updateTick).start()
        print('ticking...')
        for roomcode, game in self.roomToGame.items():
            if game.state is ROUND_LIVE and time.time()-game.startTime>30:
                killgame=game.finishRound()
                if(killgame):
                    self.endGame(game.roomID)
                if self.updateClients:
                    self.updateClients(roomcode, game)
            elif game.state is ROUND_END and time.time()-game.startTime>15:
                game.startRound()
                if self.updateClients:
                    self.updateClients(roomcode, game)
                return



