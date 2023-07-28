from discord import Member, Message
class cb_guild:
    guild_id = None
    data = { # just one for now but maybe more opts later
        "prof_filter":"False"
    }
    search = []
    def __init__(self, gid, data):
        self.guild_id = gid
        if not data == None:
            self.data = data

    def set_prof_filter( self, opt ):
        self.data["prof_filter"] = str(bool(opt))
        return bool(self.data["prof_filter"])
    
    def get_prof_filter( self ):
        return bool(self.data["prof_filter"])
    
    # expects a discord.User object as user
    def add_search( self, engine, user, parms, results, msg ):
        if not type(user) == Member:
            raise TypeError("Non-user object passed. Expected discord.User object got: {}".format(type(user)))
        if not type(msg) == Message:
            raise TypeError("Non-Message passed as message. Expecting discord.Message got: {}".format(type(msg)))
        for s in self.search:
            if s.get_uid() == user.id and s.get_gid() == self.guild_id:
                raise RuntimeError("This user already has an on-going search!")
        new_search = _cb_search( engine, user, self.guild_id, parms, results, msg )
        self.search.append(new_search)
        return new_search

    def get_search( self, uid, gid ):
        try:
            if len(self.search) == 0:
                raise RuntimeError("No searches for this guild!")
        except RuntimeError as e:
                return None
        except Exception as e:
                print("unhandled exception in get_search()")
                return e
        for s in self.search:
            if s.get_uid() == uid and s.get_gid() == gid:
                return s
        
            
    def del_search( self, uid, gid ):
        for s in self.search:
            if s.get_uid() == uid and s.get_gid() == gid:
                try:
                    self.search.remove(s)
                    return s
                except ValueError as e:
                    print("value was not in list")
                    return None
        return None
    
    # debug function to refresh searches without restarting
    def _flush( self ):
        self.search = []
        return None

    def __str__( self ):
        return self.guild_id
    
class _cb_search:
    data = {}
    def __init__( self, engine, author, guild_id, 
                 search_parms, search_results, sent_msg ):
        self.data['engine'] = engine
        self.data['user'] = author.name
        self.data['uid'] = author.id
        self.data['gid'] = guild_id
        self.data['parms'] = search_parms
        self.data['search_results'] = search_results
        self.data['sent_msg'] = sent_msg

    def get_user(self):
        return self.data['user']

    def get_uid(self):
        return self.data['uid']

    def get_gid(self):
        return self.data['gid']

    def get_parms(self):
        return self.data['parms']

