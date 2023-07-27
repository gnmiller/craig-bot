class cb_guild:
    guild_id = None
    data = { # just one for now but maybe more opts later
        "prof_filter":"False"
    }
    def __init__(self, gid, data):
        self.guild_id = gid
        if not data == None:
            self.data = data

    def set_prof_filter( self, opt ):
        self.data["prof_filter"] = str(bool(opt))
        return bool(self.data["prof_filter"])
    
    def get_prof_filter( self ):
        return bool(self.data["prof_filter"])
    
    def __str__( self ):
        return self.guild_id
