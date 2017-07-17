import discord
from craig_search import search
import datetime

class craig_server:
    def __init__( self, serv, timeout ):
        self.me = serv
        self.search_helper = search( serv.name, timeout )
        self.users = []
        
    def get_role_status( self, role_name ):
        ret_users = []
        for u in self.users :
            for r in u.me.roles :
                if r.name == role_name :
                    ret_users.append( u )
        return ret_users
    
    def search( self, term, mode, apikey, msg ):
        print( term )
        if mode == "youtube":
            return self.search_helper.youtube_search( term, apikey, msg )
        if mode == "tmdb":
            return self.search_helper.tmdb_search( term, apikey, msg )
        if mode == "final":
            return self.search_helper.finalize_search( term )
        return ""

class craig_user:
    def __init__( self, user, status, time ):
        self.me = user
        self.status = status
        self.time = datetime.datetime.now()
