from app import spotifyapi
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class GameUser:
    name = ""
    score = 0

    def __init__(self, name):
        self.name = name


GUESS_INCORRECT = 'incorrect'
GUESS_CLOSE = 'close'
GUESS_CORRECT = 'correct'


class Game:
    playlistID = None
    unplayedSongs = []
    playedSongs = []
    currentSong={ 'name' : 'September',
                 'artist' : 'Earth wind and fire' }
    gameUsers = {}
    roomID = "tacocode"
    gameStarted = False
    playlistData = None

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
        return True

    def checkGuess(self, username, guess):
        if self.currentSong is None:
            return 0
        sim = similar(guess,self.currentSong['name'])>0.9
        if sim > 0.95:
            return GUESS_CORRECT
        if sim > 0.80:
            return GUESS_CLOSE
        return GUESS_INCORRECT

    def getSongInfo(self):
        return self.currentSong

    def getRoomCode(self):
        return self.roomID

    def getPlaylistMeta(self):
        if self.playlistData is None:
            return None
        try:
            return { 'name' : self.playlistData['name'],
                   'thumbnail' : self.playlistData['images'][0]['url'],
                   'link' : self.playlistData['external_urls']['spotify']}
        except KeyError as e:
            return None

    def setPlaylist(self, spotifyURI):
        self.playlistID = spotifyURI
        self.playlistData = spotifyapi.getPlaylist(spotifyURI)
        return True

    def getPlayersData(self):
        return {{"name":n.name,"score":n.score} for n in self.gameUsers.items()}


class GameManager:
    roomToGame = {}

    def getGame(self, key):
        return self.roomToGame[key]

    def createGame(self):
        game = Game()
        self.roomToGame[game.getRoomCode()] = game
        return game
        
    def startGame(self, key):
        if key in self.roomToGame:
            return False
        self.roomToGame[key] = Game(key)
        return True

    def endGame(self, key):
        if key not in self.roomToGame:
            return False
        self.getGame(key).endGame()
        self.roomToGame.pop(key)
        return True
