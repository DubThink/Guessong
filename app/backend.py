import app


def createLobby():
    return app.gameManager.createGame().roomID

def joinLobby(room, username):
    game = app.gameManager.getGame(room)
    if  game == None:
        print("No room")
        return None
    else:
        return game.addUser(username)

def startGame(room, name, playlist, song_length):
    game = app.gameManager.getGame(room)
    game.setPlaylist(1)
    app.gameManager.startGame(room)

def getGame(room):
    return app.gameManager.getGame(room)

def getGamePlaylist(room):
    return app.gameManager.getGame(room).getPlaylistMeta()

def updateGameState(roomcode, game):
    #print("emitting:" + roomcode)
    #app.socketio.emit("update_game", "plub")
    return True
    
