import requests
import base64,json
from config import Config
token=None

def initAPI():
    headers = {
        'Authorization': b'Basic '+base64.b64encode(Config.SPOTIFY_ID + b':' + Config.SPOTIFY_SECRET),
    }

    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    global token
    token=json.loads(response.text)["access_token"]

def getToken():
    if token is None:
        initAPI()
    return token

def testspotifyapi(p):
    return json.dumps(getPlaylist(p.split(':')[-1]), sort_keys=True,indent=4)

def getPlaylist(p):
    headers = {
        'Authorization': 'Bearer %s'%getToken(),
    }

    response = requests.get('https://api.spotify.com/v1/playlists/%s'%p, headers=headers)
    return json.loads(response.text)