import requests
import json


def _getsong(id):
    return requests.get('https://itunes.apple.com/us/lookup?id={}'.format(id)).text

def _getPlaylist(playlistID):
    pass

def getPlaylist(id):
    return json.loads(open('playlist'+str(id)+'.json').read())['songs']

def getPlaylistMeta(p):
    playlist=getPlaylist(p)
    print(playlist)
    #return { 'name' : playlist['name'],
    #               'thumbnail' : playlist['images'][0]['url'],
    #               'link' : playlist['external_urls']['spotify']}
    return playlist

