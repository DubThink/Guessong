
class GameUser:
    userID = 0
    name = ""
    score = 0

    def __init__(self, userID, name):
        self.userID = userID
        self.name = name
        
class Game:
    playlistID = 0
    unplayedSongs = []
    playedSongs = []
    gameUsers = []
    roomID = "tacocode"
    gameStarted = False

    def addUser(self, username):
        user = GameUser(len(self.gameUsers), username)
        self.gameUsers.append(user)

    def removeUser(self, username):
        return True
    
    def endRoom(self):
        return True

    def checkGuess(self, username, guess):
        return 0

    def getSongInfo(self):
        return { 'name' : 'September',
                 'artist' : 'Earth wind and fire' }
    def getRoomCode(self):
        return self.roomID

    def getPlaylistMeta(self):
        return { 'name' : 'cool tunes',
               'thumbnail' : 'http',
               'link' : 'http' }
    def setPlaylist(self, spotifyURI):
        return True

    def getPlayersData(self):
        return {{"name":n,"score":0} for n in gameUsers}



class GameManager:
    roomToGame = {}

    def getGame(self, key):
        return self.roomToGame[key]

    def createGame(self):
        game = Game()
        self.roomToGame[game.getRoomCode()] = game
        return game
        
    def startGame(self, key):
        return True

    def endGame(self, key):
        return True
