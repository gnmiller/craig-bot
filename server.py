import discord, asyncio, collections, datetime, os, json
from search import bs_search
from tzlocal import get_localzone as glz

class bs_timer:
    def __init__( self, timeout, callback ):
        self.timeout = timeout
        self.callback = callback
        self.task = asyncio.ensure_future( self.job() )
        
    async def job( self ):
        await asyncio.sleep( self.timeout )
        await self.callback()
        return
        
    async def cancel( self ):
        self.task.cancel()
        return

class bs_user:
    def __init__( self, user ):
        self.user = user
        self.state = user.status
        self.last = datetime.datetime.now().astimezone( glz() )
    
class bs_server:
    def __init__( self, client, server, max_time, max_msg ):
        self.mode = None
        self.busy = False
        self.me = server
        self.client = client
        self.results = {}
        self.msg_q = collections.deque()
        self.cmd_q = collections.deque()
        self.helper = None
        self.server = server
        self.timer = None
        self.msg_lim = max_msg
        self.max_time = max_time
        self.users = {}
        self.game = None
        for m in server.members:
            self.users[int(m.id)] = bs_user( m )
        self.load_auth( "./authorized.json" )
    
    def load_auth( self, auth_file ):
        path = os.path.dirname( os.path.realpath( __file__ ) )
        with open( auth_file, 'r' ) as f:
            auth_data = json.load( f )
        self.auth = {}
        if self.me.id in auth_data:
            for e in auth_data[self.me.id]:
                self.auth[e] = auth_data[self.me.id][e]
        return
        
    def get_auth( self, user ):
        if user.id in self.auth:
            return self.auth[user.id]
        else:
            return None
    
    def queue_msg( self, msg ):
        if len( self.msg_q ) >= self.msg_lim:
            self.msg_q.popleft()
        self.msg_q.append( msg )
        return
    
    def queue_cmd( self, msg ):
        if len( self.cmd_q ) >= self.msg_lim:
            self.cmd_q.popleft()
        self.cmd_q.append( msg )
        return
    
    async def reset( self ):
        self.mode = None
        self.busy = False
        self.helper = None
        self.game = None
        if not self.timer == None:
            await self.timer.cancel()
            self.timer = None
        return
    
    async def timeout( self ):
        await self.reset()
        await self.client.send_message( self.cmd_q[-1].channel, "Timeout!\n" )
        return

    async def search( self, term, mode, apikey ):
        if not self.busy:
            self.timer = bs_timer( self.max_time, self.timeout )
            self.helper = bs_search( term, mode, apikey )
            self.helper.do_search()
            self.busy = True
            self.mode = "search"
            msg_str = "```Please select a video:\n"
            for i in range( 1, len(self.helper.results)+1 ):
                msg_str += str(i)+". "+self.helper.results[i].name+"\n"
            msg_str += "```\n"
            last_msg = await self.client.send_message( self.cmd_q[-1].channel, msg_str )
            return
        else:
            return
        
    async def get_res( self, res ):
        if not self.busy:
            return
        if self.helper.mode == "yt":
            msg_str = "Selected video: {}\nTitle: {}\nhttps://www.youtube.com/watch?v={}\n".format( str(res), self.helper.results[res].name, self.helper.results[res].id )
            await self.client.edit_message( self.msg_q[-1], msg_str )
            await self.reset()
        elif self.helper.mode == "tmdb":
            msg_str = "Selected film: {}\nName: {}\nhttps://www.themoviedb.org/movie/{}".format( str(res), self.helper.results[res].name, self.helper.results[res].id )
            await self.client.edit_message( self.msg_q[-1], msg_str )
            await self.reset()
        return          