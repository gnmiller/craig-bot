import discord, json, datetime, pytz, os, threading, collections, urllib3
from apiclient.discovery import build

path = os.path.dirname(os.path.realpath( __file__ ))
with open( path+"/settings.json" ) as f:
    settings = json.load( f )
    
with open( path+"/auth.json" ) as f:
    auth_data = json.load( f )

class bs_user:
    def __init__( self, user, status, time, donger ):
        self.user = user
        self.status = status
        self.last_seen = pytz.utc.localize( datetime.datetime.now() )
        self.donger = 0
        self.auth_level = 0
        
class bs_result:
    def __init__( self, id, name ):
        self.id = id
        self.name = name
        
class bs_search:
    def __init__( self, mode, term, apikey ):
        self.started = False
        self.results = {}
        self.mode = None
        self.term = term
        self.api = apikey
        
    def youtube( self ):
        self.mode = "yt"
        yt = build( "youtube", "v3", developerKey=self.api )
        resp = youtube.search().list( q=self.term, part="id,snippet", maxResults=50 ).execute()
        count=0
        for res in response.get( "items", [] ):
            if res["id"]["kind"] == "youtube#video":
                count+=1
                self.results[count] = result( res["id"]["videoId"], res["snippet"]["title"] )
                if count >= 10:
                    break
            else:
                continue
        return self.results
    
    def tmdb( self ):
        self.mode = "tmdb"
        uri = "https://api.themoviedb.org/3/search/movie?api_key={}&query={}".format(api, term)
        http = urllib3.PoolManager()
        resp = http.request( "GET", uri )
        data = json.load( resp.data.decor( "utf-8" ) )
        t_result = {}
        count = 0
        for res in data.get( "results", [] ):
            rating = res["vote_average"]
            rating_count = res["vote_count"]
            year = res["release+date"][0:4]
            tmp = result( res["id"], res["title"] )
            count+=1
            self.results[count] = tmp
            t_result[count] = tmp
        return t_result
    
    def do_search( self ):
        if self.mode == "yt":
            return youtube( self )
        if self.mode == "tmdb":
            return tmdb( self )
        return None
        
class bs_server:
    def __init__( self, server, timeout_val, auth_list, q_len, discord ):
        self.server = server
        self.max_time = 0
        self.user_list = []
        self.msg_log = collections.deque()
        self.max_msg = q_len
        self.busy = False
        self.mode = None
        self.client = discord
        self.game = None
        self.search_helper = None
        try:
            self.max_tome = settings["bot"][server.id]["timeout"]
        except:
            self.max_time = 180
        for m in server.members:
            self.user_list.append( bs_user( u, u.status, pytz.utc.localize( datetime.datetime.now() ), 0 ) )
        
    def role_by_name( self, role_name ):
        for r in self.server.roles:
            if r.name.lower() == role_name.lower():
                return r
        return None
    
    def user_by_name( self, user_name ):
        for u in self.user_list:
            if u.user.name.lower() == user_name
                return u
        return None
    
    def user_by_id( self, user_id ):
        for u in self.user_list:
            if u.user.id == user_id:
                return u
        return None
    
    def load_auth( self, auth_file ):
        path = os.path.dirname( os.path.realpath( __file__ ) )
        with open( auth_file, 'r' ) as f:
            auth_data = json.load( auth_data ) 
        # check if server in auth
        # check all users of server if their id in auth file
        # check if theres a role with higher perm level
        if self.server.id in auth_data: 
            for u in self.server.user_list:
                if not u.user.id in auth_data[server.id]:
                    continue
                u.auth_level = auth_data[server.id][u.user.id]
                for r in u.user.roles:
                    if r.id in auth_data[server.id]:
                        if auth_data[server.id][r.id] > u.auth_level:
                            u.auth_level = auth_data[server.id][r.id]
        return
    
    def update_auth( self, user_id, new_mode ):
        user = self.user_by_id( self, user_id )
        user.auth_level = new_mode
        return user
    
    def get_role_status( self, role_id ):
        users = []
        if role == None:
            return users
        for u in self.user_list:
            for r in u.roles:
                if r.id == role.id:
                    users.append( u )
        return users 
    
    def queue_msg( self, new_msg ):
        if len( msg_log ) > self.max_msg:
            self.msg_log.popleft()
        self.msg_log.append( new_msg )
        
    def reset( self ):
        self.mode = None
        self.busy = False
        self.search_helper = None
    
    def timeout( self ):
        if self.busy == True:
            self.reset( self )
            msg = await client.send_message( msg_log.pop().channel, "Timeout!\n" )
        return
    
    def search( self, mode, term, api ):
        if not self.busy:
            self.mode = "search"
            self.search_helper = bs_search( mode, term, api )
                
    