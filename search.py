#!/usr/bin/python3.6
from apiclient.discovery import build
import urllib3, json

class result:
    def __init__( self, name, id ):
        self.name = name
        self.id = id

class bs_search:
    def __init__( self, term, mode, apikey ):
        self.term = term
        self.mode = mode
        self.apikey = apikey
        self.results = {}
        
    def youtube_search( self ):
        youtube = build( "youtube", "v3", developerKey=self.apikey )
        response = youtube.search().list( q=self.term, part="id,snippet", maxResults=50 ).execute()
        count = 0
        for res in response.get( "items", [] ):
            if res["id"]["kind"] == "youtube#video" :
                count+=1
                self.results[count] = result( res["snippet"]["title"], res["id"]["videoId"] )
                if count >= 10 :
                    break
            else:
                continue
        return self.results
    
    def tmdb_search( self ):
        uri = "https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format( self.apikey, self.term )
        http = urllib3.PoolManager()
        response = http.request( "GET", uri )
        data = json.loads( response.data.decode( "utf-8" ) )
        count = 0
        for res in data.get( "results", [] ):
            count += 1
            self.results[count] = result( res["title"], res["id"] )
            if count >= 10:
                break
        return self.results
    
    def do_search( self ):
        if self.mode == "yt":
            return self.youtube_search()
        if self.mode == "tmdb":
            return self.tmdb_search()
        return