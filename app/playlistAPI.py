from flask_restful import Resource, Api
from app import spotifyapi
import requests
import time
import json
from flask_restful import reqparse
import time
import threading
from app.models import Playlist,Song
threads=[]
threadid=0


class GetSpotifyPlaylistWithITunesThread(threading.Thread):
    def __init__(self,playlistObject, spotifyURI,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.playlistObject=playlistObject
        self.spotifyURI=spotifyURI

    def run(self):
        global threads
        print("{} started!".format(self.getName()))
        time.sleep(10)
        print("{} finished!".format(self.getName()))
        # if more threads waiting, start the next
        if len(threads)>0:
            threads.pop(0).start()


class AddPlaylist(Resource):
    def get(self):
        global threads
        global threadid
        parser = reqparse.RequestParser()
        parser.add_argument('spotifyid', type=str, help='spotify playlist URI')
        args = parser.parse_args()
        if 'spotifyid' in args:
            thread=GetSpotifyPlaylistWithITunesThread(None,args['spotifyid'],name=threadid)
            threadid+=1
            # add new thread to queue and start it if only item
            threads.append(thread)
            if len(threads)==1:
                threads.pop().start()
        return {'threadid':threadid}

class CheckThread(Resource):
    def get(self):
        global threads
