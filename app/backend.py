import app


def create_lobby():
    return app.gameManager.create_game().roomID

def join_lobby(room, username):
    game = app.gameManager.get_game(room)
    if  game == None:
        print("No room")
        return None
    else:
        return game.add_user(username)


def start_game(room, name, playlist, song_length):
    game = app.gameManager.get_game(room)
    game.set_playlist(1)
    app.gameManager.start_game(room)


def get_game(room):
    return app.gameManager.get_game(room).get_playlist_meta()


def update_game_state(roomcode, game):
    #print("emitting:" + roomcode)
    #app.socketio.emit("update_game", "plub")
    return True
    
