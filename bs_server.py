import discord, json, datetime, pytz, os

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

class bs_server:
    def __init__( self, server, timeout_val, auth_list ):
        self.server = server
        self.max_time = 0
        self.user_list = []
        self.msg_log = []
        self.busy = False
        self.mode = None
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
    
    