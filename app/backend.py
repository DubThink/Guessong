import app


def createLobby():
    return app.gameManager.createGame().roomID

def joinLobby(room, username):
    return app.gameManager.getGame(room).addUser(username)

def updateGameState(game):
    return True
    
