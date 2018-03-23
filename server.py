import discord, asyncio, datetime, os, json
from discord.utils import find
from search import bs_search
from tzlocal import get_localzone as glz
from funcs import bs_now as bnow
from collections import deque

path = os.path.dirname(os.path.realpath(__file__))
with open( path+'/settings.json' ) as f:
    settings = json.load( f )
youtube_key = settings["youtube"]["token"]

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
        self.last = bnow()
    
class bs_server:
    def __init__( self, client, server, max_time, max_msg ):
        self.mode = None
        self.busy = False
        self.me = server
        self.client = client
        self.results = {}
        self.msg_q = deque()
        self.cmd_q = deque()
        self.helper = None
        self.server = server
        self.timer = None
        self.msg_lim = max_msg
        self.max_time = max_time
        self.users = {}
        self.game = None
        self.voice = None
        self.stream = None
        self.video_queue = []
        for m in server.members:
            self.users[m.id] = bs_user( m )
        self.load_auth( "./authorized.json" )

    def load_auth( self, auth_file ):
        """Clobber the existing auth list and load the new one from auth_file"""
        path = os.path.dirname( os.path.realpath( __file__ ) )
        with open( auth_file, 'r' ) as f:
            auth_data = json.load( f )
        f.close()
        self.auth = {}
        if self.me.id in auth_data:
            for e in auth_data[self.me.id]:
                self.auth[e] = auth_data[self.me.id][e]
        return
    
    def list_auth( self ):
        """Return a dict of users (k,v) = ('uid', discord.User)"""
        user_list = {}
        for u in self.auth:
            #tuple of discord.user and auth level
            user_list[u] = ( find( lambda m: m.id == u, self.cmd_q[-1].server.members ), self.auth[u] )
        return user_list
    
    def add_auth( self, user, level ):
        """return 0 if not in, else old level"""
        if not user.id in self.auth:
            self.auth[user.id] = level
            return 0
        else:
            old = int(self.auth[user.id])
            self.auth[user.id] = level
            return old
        
    def get_auth( self, user ):
        """Return the users auth level or None"""
        if user.id in self.auth:
            return int(self.auth[user.id])
        else:
            return 0
    
    def queue_msg( self, msg ):
        """Enqueue a message (used to track what messages bot sends per server)"""
        if len( self.msg_q ) >= self.msg_lim:
            self.msg_q.popleft()
        self.msg_q.append( msg )
        return
    
    def queue_cmd( self, msg ):
        """Enqueue a command, tracks commands the bot has received per server"""
        if len( self.cmd_q ) >= self.msg_lim:
            self.cmd_q.popleft()
        self.cmd_q.append( msg )
        return
    
    async def reset( self ):
        """Set the bots state back to 'resting' ready for any command"""
        self.mode = None
        self.busy = False
        self.helper = None
        self.game = None
        if not self.timer == None:
            await self.timer.cancel()
            self.timer = None
        return
    
    async def timeout( self ):
        """Runs after a timer expires, calls reset()"""
        await self.reset()
        await self.client.send_message( self.cmd_q[-1].channel, "Timeout!\n" )
        return

    async def search( self, term, mode, apikey ):
        """Create a search_helper if needed and execute a search."""
        if not self.busy:
            self.timer = bs_timer( self.max_time, self.timeout )
            self.helper = bs_search( term, mode, apikey )
            self.helper.do_search()
            self.busy = True
            self.mode = "search"
            if len( self.helper.results ) <= 0:
                await self.client.send_message( self.cmd_q[-1].channel, "Didn't get any results!\n" )
                await self.reset()
                return
            if self.helper.mode == "yt":
                msg_str = "```smalltalk\nPlease select a video:\n"
                for i in range( 1, len(self.helper.results)+1 ):
                    msg_str += str(i)+". "+self.helper.results[i].name+"\n"
                msg_str += "```\n"
                last_msg = await self.client.send_message( self.cmd_q[-1].channel, msg_str )
                return
            if self.helper.mode == "tmdb":
                msg_str = "```smalltalk\nPlease select a video:\n"
                msg_str += "```\n"
                await self.client.send_message( self.cmd_q[-1].channel, msg_str )
                return
        else:
            return
        
    async def get_res( self, res ):
        """Fetch a result object based on the search type and return the appropriate URI for that object"""
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
    
    def enq_video( self, yt_link ):
        return self.video_queue.append( yt_link )
    
    def deq_video( self ):
        return self.video_queue.pop(0)

    async def play_video( self, **kwargs ):
        if len( self.video_queue ) > 0 :
            self.stream = await self.voice.create_ytdl_player( self.deq_video( ) )
            self.stream.start()
            self.vid_timer = bs_timer( self.stream.duration+3, self.play_video )
            title = self.stream.title
            if kwargs['p_flag'] is None:
                await client.send_message( self.msg_q[-1], "```playing {}```".format( title ) )
            return title
        await client.send_message( self.msg_q[-1], "```no songs in the queue!```" )
        return "No songs remaining in the queue."
        
    
    def print_voice_queue( self ):
        p_str = "```Current YouTube video queue \n -------------------- \n"
        count = 0
        if len( self.video_queue ) == 0:
            return "```No queue.```"
        for v in self.video_queue:
            count += 1
            id = v.split( '=' )[1]
            from apiclient.discovery import build
            youtube = build( "youtube", "v3", developerKey=youtube_key )
            response = youtube.search().list( q=id, part="id,snippet", maxResults=1 ).execute()
            for res in response.get( "items", [] ):
                title = res["snippet"]["title"]
            p_str += "{}. {}".format( count, title )
            p_str += "\n"
        p_str += "```"
        return p_str
            
