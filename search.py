import datetime, json, urllib3
from apiclient.discovery import build
from datetime import date
from datetime import timedelta

class result:
    name = ""
    id = ""
    def __init__( self, name, id ):
        self.name = name
        self.id = id

class search:
    def __init__( self, timeout ):
        self.searched = False
        self.search_time = datetime.datetime.now()
        self.search_msg = None
        self.results = {}
        self.mode = "none"
        self.max_time = timeout

    def timeout( self ):
        now = datetime.datetime.now()
        if( self.searched == False ):
            return False
        elif( now > ( self.search_time + timedelta( seconds = self.max_time ) ):
            return True
        else:
            return False

    def search_clear( self ):
        self.searched = False
        self.searc_time = datetime.datetime.now()
        self.search_msg = None
        self.results = {}
        self.mode = "none"

    def youtube_search( self, term, apikey ):
        """Search YouTube for 'term', authenticating with 'apikey' and returning a formatted string of results"""
        if( self.timeout() == True ):
            return "timeout"
        if( self.searched == True ):
            return "previous search not completed"
        self.search_clear()
        youtube = build( "youtube", "v3", developerKey=apikey )
        response = youtube.search().list( q=term, part="id,snippet", maxResults=50 ).execute()

        count = 0
        res_str="```css\n"
        for res in response.get( "items", [] ):
            if res["id"]["kind"] == "youtube#video" :
                count+=1
                res_str+=str(count)+". "+res["snippet"]["title"]+"\n"
                result[count] = result( res["snippet"]["id"], res["id"]["videoId"] )
                if count >= 10 :
                    break
            else:
                continue
        self.mode = "youtube"
        self.searched = True
        self.search_time = datetime.datetime.now()
        res_str+="```"
        return res_str

    def tmdb_search( self, term, apikey ):
        """Search tmdb for 'term' authenticating with 'apikey' and returning a formatted results string"""
        if( self.timeout() == True ):
            return "timeout"
        if( self.searched == True ):
            return "previous search still in progress"
        self.search_clear()
        uri = "https://api.themoviedb.org/3/search/movie?api_key="+api_key
        uri += "&query="+term
        http=urllib3.PoolManager()
        response = http.request( "GET", uri )
        data=json.loads( response.data.decode( 'utf-8' ) )
        count=0
        res_str="```css\n"
        for res in data.get( "results", [] ):
            rating = res["vote_average"]
            rating_count = ["vote_count"]
            year = res["release_date"][0:4]
            tmp = result( res["title"], res["id"] )
            if count >= 10 :
                break
            count += 1
            res_str += str(count)+". "+tmp.title+" ("+str(year)+" -- "+str(rating)+"/10 ("
            res_str += rating_count+" votes)\n"
            results[count] = tmp

        self.searched = True
        self.mode = "tmdb"
        return res_str

    def finalize_search( self, val  ):
        """Select which results to use"""
        if( self.timeout() == True ):
            return "timeout"
        if( self.searched == False ):
            return "why did you do this?"

        if self.mode == "youtube" :
            return ret_uri = "Selected video -"+str(val)+"-\nTitle: "+self.results[val].name+"\nhttps://www.youtube.com/watch?v="+str(self.results[val].id)
        elif self.mode == "tmdb" :
            return ret_uri = "Selected video -"+str(val)+"-\nTitle: "+self.results[val].name+"\nhttps://www.themoviedb.org/movie/"+str(results[val].id)
        elif self.mode == "ff" : #NYI
            return ret_uri = "Selected character - "+str(val)+"-\nName: "+self.results[val].name+"\nhttps://api.xivdb.com/characters/"+str(results[val].id)
        else:
            return "what"
