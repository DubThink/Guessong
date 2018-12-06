import app

codecount = 0

def createLobby():
    global codecount
    codecount += 1
    return app.gameManager.createGame(str(codecount)).roomID

def joinLobby(room, username):
    app.gameManager.getGame(room).addUser(username)

def updateGameState(game):
    return True
    
