from flask_restful import Resource, Api
from app import spotifyapi, db
from app.models import Song,Playlist
import requests
import time
import json
from flask_restful import reqparse
from app import Config
import time
import threading
from app.models import Playlist,Song
threads=[]
threadid=0
thread_running=None


class GetSpotifyPlaylistWithITunesThread(threading.Thread):
    _its = "https://itunes.apple.com/search?entity=song&attribute=songTerm&term=%s"
    def __init__(self,playlistObject, spotifyURI, id,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.playlistID=playlistObject
        self.spotifyURI=spotifyURI
        self.id=id
        self._progress=0.0

    def run(self):
        global threads, thread_running
        thread_running=self
        print("{} started!".format(self.getName()))

        d = spotifyapi._getPlaylist(self.spotifyURI)
        data = []

        for t in d['tracks']['items']:
            data.append((t['track']['artists'][0]['name'], t['track']['name'],t['track']['album']['name']))

        for i,song in enumerate(data):
            self._progress=i/float(len(data))
            cleanArtist = song[0].lower().replace(' ', '+')
            cleanSong = song[1].split(' - ', 1)[0].strip().lower().replace(' ', '+')
            r = requests.get(self._its % cleanSong)
            print(self._its % cleanSong, cleanArtist)
            itdata = json.loads(r.text)["results"]
            playlist=Playlist.query.get(self.playlistID)
            success=False
            for result in itdata:
                if result['artistName'] == song[0] and result['collectionName'] == song[2]:
                    song_obj = Song.query.filter_by(itunes_resource_id=result['trackId']).first()
                    if song_obj is None:
                        song_obj=Song()
                        song_obj.name=result['trackCensoredName']
                        song_obj.artist=result['artistName']
                        song_obj.album=result['collectionCensoredName']
                        song_obj.thumbnail_url=result['artworkUrl100'].replace('100x100','400x400')
                        song_obj.preview_url=result['previewUrl']
                        song_obj.external_url=result['trackViewUrl']
                        song_obj.itunes_resource_id=result['trackId']
                        db.session.add(song_obj)
                        db.session.commit()
                    print('adding song...')
                    playlist.songs.append(song_obj)
                    db.session.commit()
                    success=True
                    break
            if success:
                continue
            for result in itdata:
                if result['artistName'] == song[0]:
                    song_obj = Song.query.filter_by(itunes_resource_id=result['trackId']).first()
                    if song_obj is None:
                        song_obj=Song()
                        song_obj.name=result['trackCensoredName']
                        song_obj.artist=result['artistName']
                        song_obj.album=result['collectionCensoredName']
                        song_obj.thumbnail_url=result['artworkUrl100'].replace('100x100','400x400')
                        song_obj.preview_url=result['previewUrl']
                        song_obj.external_url=result['trackViewUrl']
                        song_obj.itunes_resource_id=result['trackId']
                        db.session.add(song_obj)
                        db.session.commit()
                    print('adding song (no album match)...')
                    playlist.songs.append(song_obj)
                    db.session.commit()
                    break
            time.sleep(3)

        print("{} finished!".format(self.getName()))
        # if more threads waiting, start the next
        if len(threads)>0:
            thread_running=threads.pop(0)
            thread_running.start()
        else:
            thread_running = None

    def progress(self):
        return str(self._progress*100)


class AddPlaylist(Resource):
    def get(self):
        global threads
        global threadid
        parser = reqparse.RequestParser()
        parser.add_argument('spotifyid', type=str, required=True, help='spotify playlist URI')
        parser.add_argument('name', type=str, required=True, help='name for playlist')
        parser.add_argument('auth', type=str, required=True, help='auth token defined in .env')
        args = parser.parse_args()
        args['spotifyid']=args['spotifyid'].split(':')[-1]
        if args['auth']!=Config.PLAYLIST_API_SECRET:
            return {"message":"unauthorized"},401

        # create and populate the metadata of the new playlist
        playlist_object=Playlist()
        playlist_object.name=args['name']
        playlist_object.thumbnail="/resource/placeholder.png"
        playlist_object.spotifyid=args['spotifyid']
        db.session.add(playlist_object)
        db.session.commit()
        # create the thread to populate it
        threadid+=1
        thread=GetSpotifyPlaylistWithITunesThread(playlist_object.id,args['spotifyid'],threadid,name="Playlist-thread-%i"%threadid)
        # add new thread to queue and start it if no threads running
        threads.append(thread)
        if not thread_running:
            threads.pop().start()
            return {'threadid': threadid, 'queue_length': len(threads),'started':True}
        return {'threadid':threadid, 'queue_length':len(threads),'started':False}

class CheckThread(Resource):
    def get(self):
        global threads
        parser = reqparse.RequestParser()
        parser.add_argument('threadid', type=int, required=True, help='thread id to check')
        args = parser.parse_args()
        if args["threadid"] <= 0 or args["threadid"] > threadid:
            return {'status': 'nonexistent', "threadid": args["threadid"]}
        elif thread_running is None or thread_running.id > args["threadid"]:
            return {'status': 'finished', "threadid": args["threadid"]}
        elif thread_running.id == args['threadid']:
            return {'status':'running',"progress":thread_running.progress(),"threadid":args["threadid"]}
        else:  # thread_running.id < args["threadid"]:
            return {'status':'queued',"position":args["threadid"]-thread_running.id,"threadid":args["threadid"]}

class ListPlaylists(Resource):
    def get(self):
        return [p.toJSON() for p in Playlist.query.all()]

