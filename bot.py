import discord, asyncio, datetime, json, pytz, os
from craig_server import craig_server as __serv
from craig_server import craig_user as __user

# load settings file
path = os.path.dirname(os.path.realpath(__file__))
with open( path+'/settings.json' ) as f:
    settings = json.load( f )
    
client = discord.Client()
discord_key = settings["discord"]["token"]
youtube_key = settings["youtube"]["token"]
tmdb_key = settings["tmdb"]["token"]
prefix = settings["bot"]["prefix"]
max_time = settings["bot"]["timeout"]
my_name = settings["bot"]["my_name"]
last_msg = None
started = False


def get_got_time():
    """fetch time to next got episode"""
    cur = datetime.datetime.now()
    uri = "http://api.tvmaze.com/shows/82?embed=nextepisode"
    http = urllib3.PoolManager()
    response = http.request( 'GET', uri )
    data = json.loads( response.data.decode( 'utf-8' ) )
    next_ep = dateutil.parser.parse( data["_embedded"]["nextepisode"]["airstamp"] )
    cur = pytz.utc.localize( cur )
    diff = dateutil.relativedelta.relativedelta( next_ep, cur )
    print_str = "```css\nThere are ---\n"
    if( diff.months > 0 ):
        print_str+=str(diff.months)+" Months\n"
    if( diff.days > 0 ):
        print_str+=str(diff.days)+" Days\n"
    if( diff.hours > 0 ):
        print_str+=str(diff.hours)+" Hours\n"
    if( diff.minutes > 0 ):
        print_str+=str(diff.minutes)+" Minutes and\n"
    if( diff.seconds > 0 ):
        print_str+=str(diff.seconds)+" Seconds\n"
    print_str+="until the next Game of Thrones airs!\n\n```"
    return print_str

serv_arr = []
@client.event
async def on_ready():
    global started
    print( "startup" )
    # build arrays of data
    # track all servers were on
    # track all members and their last known status
    for s in client.servers :
        new_server = __serv( s, max_time )
        serv_arr.append( new_server )
    for s in serv_arr :
        for u in s.me.members :
            tmp = __user( u, u.status, datetime.datetime.now() )
            s.users.append( tmp )
    print( "startup finished" )
    started = True

            
@client.event
async def on_member_update( before, after ):
    global started
    if not started:
        return
    
    for s in serv_arr :
        for u in s.users :
            # user match AND status change
            if u.me.name == after.name and u.status != after.status :
                u.status = after.status
                u.time = datetime.datetime.now()
                return
            
@client.event
async def on_message( msg ):
    global last_msg
    global started
    if not started:
        return
    
    # did i send the message?
    if msg.author.name.find( my_name ) >= 0 :
        return
    
    # get what server sent message
    cur_serv = None
    for s in serv_arr :
        if s.me == msg.server: 
            cur_serv = s
            
    if cur_serv.search_helper.timeout() == True :
        cur_serv.search_helper.clear_search()
        await client.send_message( msg.channel, "Timeout!" )
        
    # main processor
    if (msg.content[:len(prefix)].find( prefix ) >= 0):
        args = msg.content[len(prefix):].split()
        if args[0] == "cr" :
            if (len(args) != 2) :
                last_msg = await client.send_message( msg.channel, "```Usage:\n    "+prefix+"cr role_name```" )
                return
            res = []
            role = None
            res = s.get_role_status( args[1] )
            for r in cur_serv.me.roles :
                if r.name == args[1] :
                    role = r
            ret_str = "Current Status of <@&"+role.id+"> :: \n```css\n"
            for u in res :
                ret_str += u.me.name+" | Status: "+str(u.status)+" | Last Updated: "+u.time.strftime( "%c" )+"\n"
            ret_str += "```"
            last_msg = await client.send_message( msg.channel, ret_str )
            return
        elif args[0] == "yt" :
            search_str = ""
            for arg in args[1:]:
                search_str += arg+"+"
            search_str = search_str[:len(search_str)-1]
            ret_str = cur_serv.search( search_str, "youtube", youtube_key, msg )
            last_msg = await client.send_message( msg.channel, ret_str )
            return
        elif args[0] == "help" or args[0] == "h":
            await client.send_message( msg.author, "NYI" )
            return
        else:
            return
        
    # search results
    if ( cur_serv.search_helper.searched == True ):
        if( msg.content.isdigit and msg.author.name == cur_serv.search_helper.search_msg.author.name ):
            ret_str = cur_serv.search( msg.content, "final", None, None )
            last_msg = await client.edit_message( last_msg, ret_str )
            return
        else:
            return
        
client.run( discord_key )