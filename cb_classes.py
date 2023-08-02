from discord import Member, Message
import config, asyncio
import pdb

class cb_guild:
    guild_id = None
    data = { # just one for now but maybe more opts later
        "prof_filter":"False"
    }
    
    search = []
    admin_users = []
    admin_groups = []

    def __init__(self, gid, admin_users, admin_groups, data):
        self.guild_id = gid
        if not type(admin_users) is list or not type(admin_groups) is list:
            raise TypeError("Did not get valid list of admin users or groups!")
        for u in admin_users:
            self.admin_users.append(u)
        for g in admin_groups:
            self.admin_groups.append(g)
        if not data == None:
            self.data = data

    def auth_user( self, user, guild, db_file="craig-bot.sqlite"):
        self.admin_users.append(user.id)
        # TODO write out to DB
        return

    def get_auth( self ):
        return (self.admin_users,self.admin_groups)
    
    # expects a discord.User object as user
    async def add_search( self, engine, user, guild, channel, parms, results, msg ):
        """Adds a search object to the internal list of searches for this guild object.
        Engine(string): The API that this search object will search.
        User(int): Discord user id that sent the message
        Guild(int): Discord guild ID the search came from
        Channel(int): Discord channel ID the search came from"""
        if not type(msg) == Message:
            raise TypeError("Non-Message passed as message. Expecting discord.Message got: {}".format(type(msg)))
        for s in self.search:
            if s.get_uid() == user and s.get_gid() == guild and s.get_channel == channel:
                raise RuntimeError("This user already has an on-going search!")
        new_search = _cb_search( engine, user, guild, channel, parms, results, msg )
        self.search.append(new_search)
        return new_search

    async def get_search( self, uid, gid, cid ):
        """Return a cb_search object that matches the gived user id (uid), guild id (gid) and channel id (cid)
        If none is found throws a RuntimeError"""
        try:
            if len(self.search) == 0:
                raise RuntimeError("No searches for this guild!")
        except RuntimeError as e:
                return None
        except Exception as e:
                print("unhandled exception in get_search()")
                return e
        for s in self.search:
            if s.get_uid() == uid and s.get_gid() == gid and s.get_channel() == cid:
                return s
        raise RuntimeError("No searches for this guild!")
 
    def my_search(self):
        return self.search    
            
    async def del_search( self, user, guild, channel ):
        for s in self.search:
            if s.get_uid() == user and s.get_gid() == guild and s.get_channel() == channel:
                try:
                    self.search.remove(s)
                    print( "del search user: {} guild {} channel {}".format( user,guild,channel ))
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
    def __init__( self, engine, author, guild_id, channel,
                 search_parms, search_results, sent_msg ):
        self.data['engine'] = engine
        self.data['uid'] = author
        self.data['gid'] = guild_id
        self.data['cid'] = channel
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
    
    def get_channel(self):
        return self.data['cid']
    

