import discord, json, datetime, pytz, os
from craig_helper import search
from craig_helper import hangman
from datetime import timedelta

path = os.path.dirname(os.path.realpath(__file__))
with open( path+'/authorized.json' ) as f:
    settings = json.load( f )

class craig_server:
    """Container for Discord.client.server objects and associated helper objects (eg search())"""
    cmds = [ "got", "yt", "qr", "tmdb", "status", "stop" ]
    def __init__( self, serv, timeout ):
        self.me = serv
        self.search_helper = search( serv.name, timeout )
        self.users = []
        self.last_msg = None
        self.busy = False
        self.game = None
        self.last_used = {}
        now = pytz.utc.localize( datetime.datetime.now() )
        for c in self.cmds :
            self.last_used[ c ] = ( now + timedelta( minutes=-5 ) )
        self.auth = []
        for user in settings[ "user" ] :
            self.auth.append( settings["user"][user] )
        for role in settings[ "role" ] :
            self.auth.append( settings["role"][role] )
        

    def get_role_status( self, role_name ):
        """Return all users in the server that are members of role_name"""
        ret_users = []
        for u in self.users :
            for r in u.me.roles :
                if r.name.lower() == role_name.lower() :
                    ret_users.append( u )
        return ret_users
    
    def games( self, mode ):
        if( mode == "hangman" ):
            self.game = hangman()
            self.busy = True
            
    
    def search( self, term, mode, apikey, msg ):
        """Perform a search of term in the specified API, using the provided API key where appropriate. Must be called twice, once with the original mode then again with 'final'. Failure to follow this procedure will usually cause a timeout or other undefined behavior."""
        if not self.busy:
            # searching is NOT busy because search manages itself own state
            # TODO perhaps move the search busy state to the server busy state
            if mode == "youtube":
                return self.search_helper.youtube_search( term, apikey, msg )
            if mode == "tmdb":
                return self.search_helper.tmdb_search( term, apikey, msg )
            if mode == "final":
                return self.search_helper.finalize_search( term )
            return ""
        else:
            return "Server is busy, try again in a bit!"

class craig_user:
    """Container for Discord.user. Primarily for tracking the first time they were seen with their current status."""
    def __init__( self, user, status, time ):
        self.me = user
        self.status = status
        self.time = datetime.datetime.now()
        
        
