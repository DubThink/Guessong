import requests
import json


def _get_song(id):
    return requests.get('https://itunes.apple.com/us/lookup?id={}'.format(id)).text


def _get_playlist(playlistID):
    pass


def get_playlist_songs(id):
    return json.loads(open('playlist'+str(id)+'.json').read())['songs']


def get_playlist_meta(p):
    playlist = get_playlist_songs(p)
    # print(playlist)
    return playlist

