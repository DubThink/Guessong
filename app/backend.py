import app


def createLobby():
    return app.gameManager.createGame().roomID

def joinLobby(room, username):
    game = app.gameManager.getGame(room)
    if  game == None:
        return None
    else:
        return game.addUser(username)

def updateGameState(game):
    return True
    
