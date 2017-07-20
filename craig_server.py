import discord, json, datetime, pytz, os
from craig_helper import search, hangman, cmds
from datetime import timedelta

path = os.path.dirname(os.path.realpath(__file__))
with open( path+'/settings.json' ) as f:
    settings = json.load( f )

class craig_server:
    """Container for Discord.client.server objects and associated helper objects (eg search())"""
    def __init__( self, serv, timeout ):
        self.me = serv
        self.search_helper = search( serv.name, timeout )
        self.users = []
        self.last_msg = None
        self.busy = False
        self.game = None
        self.last_used = {}
        now = pytz.utc.localize( datetime.datetime.now() )
        for c in cmds :
            self.last_used[ c ] = ( now + timedelta( minutes=-5 ) )
        self.load_auth( settings["bot"]["auth_file"] )
                
    def load_auth( self, auth_file ):
        """Load auth data"""
        path = os.path.dirname(os.path.realpath(__file__))
        with open( auth_file, 'r' ) as f:
            auth_data = json.load( f )
        self.auth = {}
        self.auth["role"] = []
        self.auth["user"] = []
        my_name = self.me.name.lower()
        if my_name in auth_data["user"]:
            users = auth_data["user"][my_name]
            for u in users:
                self.auth["user"].append( u.lower().strip() )
        if my_name in auth_data["role"]:
            roles = auth_data["role"][my_name]
            for r in roles:
                self.auth["role"].append( r.lower().strip() )

    def get_role_status( self, role_name ):
        """Return all users in the server that are members of role_name"""
        ret_users = []
        for u in self.users :
            for r in u.me.roles :
                if r.name.lower() == role_name.lower() :
                    ret_users.append( u )
        return ret_users
    
    def add_auth( self, new, mode ):
        """Authorize a user or role (temp)"""
        if mode == "role":
            for r in self.auth["role"]:
                if r == new:
                    return False
            self.auth["role"].append( new.lower().strip() )
            return True
        if mode == "user":
            for u in self.auth["user"]:
                if u == new:
                    return False
            self.auth["user"].append( new.lower().strip() )
            return True
        
    def del_auth( self, delete ):
        """De-authorized a role or user (temp)"""
        if delete in self.auth["user"]:
            self.auth["user"].remove( delete )
            return True
        if delete in self.auth["role"]:
            self.auth["role"].remove( delete )
            return True
        return False
              
    def check_auth( self, user ):
        """Check if a user is authorized for a server."""
        for r in user.roles :
            for a in self.auth["role"] :
                if r.name.lower() == a :
                    return True
        for u in self.auth["user"] :
            if u.lower() == user.name.lower() :
                return True
        return False
        
    def games( self, mode ):
        """Construct games"""
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
        
    def reset_game( self ):
        """Reset the server to a state with no game playing"""
        self.game = None
        self.busy = False
        self.mode = None
        return
        
    def reset_search( self ):
        """Warpper for search clear function"""
        self.search_helper.clear_search()
        return
        
    def play_hangman( self, guess ):
        """Play hangman"""
        if not self.game.type == "hangman":
            return "no"
        
        # validate guess and update array
        for i in range( 25 ):
            if guess.lower() == chr( i+97 ):
                if self.game.guesses[ guess ] == False:
                    self.game.guesses[ guess ] = True
                else:
                    return "guessed"
        
        # is guess in word
        in_word = False
        for letter in self.game.word:
            if guess == letter:
                in_word = True
                break
        if not in_word:
            self.game.guess_count += 1
        
        # check loss
        if self.game.guess_count >= self.game.max_guesses:
            self.reset_game()
            return "loss"
        
        # chicken dinner
        temp_str = ""
        for letter in self.game.word:
            if self.game.guesses[ letter ] == True:
                temp_str += letter
        if temp_str == self.game.word:
            self.reset_game()
            return "won"
        
        if in_word:
            return "in"
        else:
            return "out"
        return
    
    def hangman_word( self ):
        """Return the 'word' formatted to display guessed letters -- Includes a line termination character."""
        ret_str = ""
        if self.game.type == "hangman":
            for letter in self.game.word:
                if self.game.guesses[ letter ] == True:
                    ret_str += letter+" "
                else:
                    ret_str += "_ "
            ret_str += "\n"
        return ret_str

class craig_user:
    """Container for Discord.user. Primarily for tracking the first time they were seen with their current status."""
    def __init__( self, user, status, time ):
        self.me = user
        self.status = status
        self.time = pytz.utc.localize( datetime.datetime.now() )
        self.donger = 0
    
        
