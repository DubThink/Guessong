import requests
import base64,json
from config import Config
token=None

def _initAPI():
    headers = {
        'Authorization': b'Basic '+base64.b64encode(Config.SPOTIFY_ID + b':' + Config.SPOTIFY_SECRET),
    }

    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    global token
    token=json.loads(response.text)["access_token"]

def _getToken():
    if token is None:
        _initAPI()
    return token

def testspotifyapi(p):
    return json.dumps(_getPlaylist(p.split(':')[-1]), sort_keys=True,indent=4)

def _getPlaylist(p):
    headers = {
        'Authorization': 'Bearer %s'%_getToken(),
    }

    response = requests.get('https://api.spotify.com/v1/playlists/%s'%p, headers=headers)
    return json.loads(response.text)


def getPlaylistMeta(p):
    playlist=_getPlaylist(p)
    return { 'name' : playlist['name'],
                   'thumbnail' : playlist['images'][0]['url'],
                   'link' : playlist['external_urls']['spotify']}