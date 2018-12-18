import app


def create_lobby():
    return app.gameManager.create_game().roomID

def join_lobby(room, username):
    game = app.gameManager.get_game(room.upper())
    if game == None:
        print("No room")
        return None
    else:
        return game.add_user(username)

def start_game(room, name, playlist, song_length):

    game = app.gameManager.get_game(room.upper())
    game.set_playlist(int(playlist))
    game.guess_time = int(song_length)
    app.gameManager.start_game(room.upper())

def get_game(room):
    return app.gameManager.get_game(room.upper())


def update_game_state(roomcode, game):
    #print("emitting:" + roomcode)
    #app.socketio.emit("update_game", "plub")
    return True
    
