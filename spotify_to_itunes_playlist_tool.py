from app import spotifyapi
import requests
import time
import json

PLAYLIST_URI="66F0QIsuqsgMsL6EsgOHZh"
d=spotifyapi._getPlaylist(PLAYLIST_URI)
data=[]

for t in d['tracks']['items']:
    data.append((t['track']['artists'][0]['name'], t['track']['name']))

its="https://itunes.apple.com/search?entity=song&attribute=songTerm&term=%s"

songdata=[]

for song in data:
    cleanArtist=song[0].lower().replace(' ','+')
    cleanSong=song[1].split('-')[0].strip().lower().replace(' ','+')
    r = requests.get(its % cleanSong)
    print(its%cleanSong, cleanArtist)
    itdata=json.loads(r.text)["results"]
    for result in itdata:
        # print(result['artistName'])
        if result['artistName']==song[0]:
            songdata.append({
                'name': result['trackName'],
                'artist': result['artistName'],
                'thumbnail_url': result['artworkUrl100'],
                'preview_url' : result['previewUrl'],
                'external_url' : result['trackViewUrl']
            })
            break

    time.sleep(3)

print(songdata)



