import discord, asyncio, datetime, json, pytz, os, urllib3, random
import dateutil.parser
import dateutil.relativedelta
from subprocess import call
from datetime import timedelta
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
date_format = "%m/%d/%y %I:%M %p"
authorized = ["btcraig","klobb"]

def check_auth( user, cur ):
    """Check if a user is authorized for a server."""
    for r in user.roles :
        for a in cur.auth :
            if r.name.lower() == a :
                return True
    for a in cur.auth :
        if a.lower() == user.name.lower() :
            return True
    return False

def magic_8ball():
    yes = ["It is decidedly so","Without a doubt","Yes, definitely","You can count on it","As I see it: Yes", "Most likely", "Outlook good", "Yes!", "All signs point to yes"]
    maybe = ["Reply hazy, try again", "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again"]
    no = ["Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]
    r = random.randint( 0, 2 )
    if r == 0 :
        return yes[ random.randint( 0, len( yes ) ) ]
    if r == 1 :
        return maybe[ random.randint( 0, len( maybe ) ) ]
    if r == 2 :
        return no[ random.randint( 0, len( no ) ) ]
    return "what"

def help_string():
    ret_str = "```css\nBeeStingBot help menu\nBot prefix: "+prefix+"\nCommands\n------------```\n"
    ret_str += "```css\n"
    ret_str += prefix+"yt <search query>\n"+"    Search YouTube for a video.\n\n"
    ret_str += prefix+"tmdb <search query>\n"+"    Search TMDb for a movie.\n\n"
    ret_str += prefix+"got\n    Print brief info on the most recent and next Game of Thrones episode.\n\n"
    ret_str += prefix+"cr <role_name>\n    Print out status on users that belong to role_name\n            Only information since the bot was last restarted is kept.\n\n"
    ret_str += prefix+"hangman\n    Start a game of hangman.\n    This will suspend other bot actions until the game is over.\n"
    ret_str += prefix+"qr <role_name>\n    Print out status on users that belong to role_name\n    Only information since the bot was last restarted is kept.\n\n"
    ret_str += prefix+"8ball <question>\n    Ask the Magic 8-ball a question and see what the fates have in store.\n\n"
    ret_str += prefix+"auth\n    Returns a list of the users authorized for privileged commands on the server.\n    Privileged commands are denoted with a (+) in the help dialogue\n\n"
    ret_str += prefix+"gamequit (+)\n    Quit the current game. Does nothing if a game is not in progress.\n\n"
    ret_str += prefix+"stop (+)\n    Stops the bot.\n\n"
    ret_str += prefix+"restart (+)\n    Restarts th bot.\n\n"
    ret_str += prefix+"status (+)\n    Displays status of the bot (PID and start time).\n\n"
    ret_str += "```"
    return ret_str

def get_got_time():
    """Returns a formatted string with the time until the next and time from the previous GoT episode. Episode name is also returned in the string."""
    cur = datetime.datetime.now()
    uri = "http://api.tvmaze.com/shows/82?embed[]=nextepisode&embed[]=previousepisode"
    http = urllib3.PoolManager()
    response = http.request( 'GET', uri )
    data = json.loads( response.data.decode( 'utf-8' ) )
    next_ep = dateutil.parser.parse( data["_embedded"]["nextepisode"]["airstamp"] )
    next_ep_name = data["_embedded"]["nextepisode"]["name"]
    prev_ep = dateutil.parser.parse( data["_embedded"]["previousepisode"]["airstamp"] )
    prev_ep_name = data["_embedded"]["previousepisode"]["name"]
    cur = pytz.utc.localize( cur )
    next_diff = dateutil.relativedelta.relativedelta( next_ep, cur )
    prev_diff = dateutil.relativedelta.relativedelta( prev_ep, cur )
    print_str = "```smalltalk\nLast Episode: "+prev_ep_name+" aired "
    if (abs(prev_diff.months) > 0):
        print_str+=str(abs(prev_diff.months))+" months "
    if (abs(prev_diff.days) > 0):
        print_str+=str(abs(prev_diff.days))+" days "
    if (abs(prev_diff.hours) > 0):
        print_str+=str(abs(prev_diff.hours))+" hours "
    if (abs(prev_diff.minutes) > 0):
        print_str+=str(abs(prev_diff.minutes))+" minutes and "
    if (abs(prev_diff.seconds) > 0):
        print_str+=str(abs(prev_diff.seconds))+" seconds ago\n"
    print_str+="Next Episode: "+next_ep_name+" airs in "
    if next_diff.months > 0 :
        print_str+=str(next_diff.months)+" months "
    if next_diff.days > 0 :
        print_str+=str(next_diff.days)+" days "
    if next_diff.hours > 0 :
        print_str+=str(next_diff.hours)+" hours "
    if next_diff.minutes > 0 :
        print_str+=str(next_diff.minutes)+" minutes and "
    if next_diff.seconds > 0 :
        print_str+=str(next_diff.seconds)+" seconds\n"
    print_str += "```"
    return print_str

serv_arr = []
authorized = ["btcraig"]
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
            tmp = __user( u, u.status, pytz.utc.localize( datetime.datetime.now() ) )
            s.users.append( tmp )
    print( "startup finished" )
    started = True

        
@client.event
async def on_server_join( server ):
    print( "new server!" )
    for s in serv_arr:
        if s.me.name.lower() == server.name.lower():
            return
    new_server = __serv( server, max_time )
    for u in s.me.members :
        tmp = __user( u, u.status, pytz.utc.localize( datetime.datetime.now() ) )
        new_server.users.append( u )
    serv_arr.append( new_server )
    return

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
    
    not_auth = "You are not authorized to send this command."
    now = pytz.utc.localize( datetime.datetime.now() )
    # main processor
    if ( msg.content[:len(prefix)].find( prefix ) >= 0 ) and not cur_serv.busy :
        args = msg.content[len(prefix):].split()
        if args[0] == "qr" :
            if (len(args) != 2) :
                cur_serv.last_msg = await client.send_message( msg.channel, "```Usage:\n    "+prefix+"cr role_name```" )
                return
            if cur_serv.last_used[ "qr" ] >= ( now + timedelta( minutes=-2 ) ) :
                cur_serv.last_msg = await client.send_message( msg.channel, "Slow down!\n" )
                return
            res = []
            role = None
            res = cur_serv.get_role_status( args[1] )
            if res == []:
                cur_serv.last_msg = await client.send_message( msg.channel, "No users with that role." )
                return
            # get the role object
            for r in cur_serv.me.roles :
                if r.name.lower() == args[1].lower() :
                    role = r
            # only allowed if youre in the group
            allow = False
            for r in msg.author.roles :
                if r.name == role.name :
                    allow = True
            if not allow :
                cur_serv.last_msg = await client.send_message( msg.channel, "```You are disallowed from this command because you are not a member of <"+role.name+">\n```" )
                return
            ret_str = "Current Status of <@&"+role.id+"> :: \n```smalltalk\n"
            for u in res :
                ret_str += u.me.name+" | Status: "+str(u.status)+" | Last Updated: "
                ret_str += u.time.strftime( date_format )+"\n"
            ret_str += "```"
            cur_serv.last_msg = await client.send_message( msg.channel, ret_str )
            cur_serv.last_used[ "qr" ] = now
            return
        elif args[0] == "yt" :
            # ' ' -> '+'
            search_str = ""
            for arg in args[1:]:
                search_str += arg+"+"
            search_str = search_str[:len(search_str)-1]
            ret_str = cur_serv.search( search_str, "youtube", youtube_key, msg )
            cur_serv.last_msg = await client.send_message( msg.channel, ret_str )
            return
        elif args[0] == "tmdb" :
            # ' ' -> '+'
            search_str = ""
            for arg in args[1:]:
                search_str += arg+"+"
            search_str = search_str[:len(search_str)-1]
            ret_str = cur_serv.search( search_str, "tmdb", tmdb_key, msg )
            cur_serv.last_msg = await client.send_message( msg.channel, ret_str )
            return
        elif args[0] == "got" :
            now = pytz.utc.localize( datetime.datetime.now() )
            if now >= (cur_serv.last_used[ "got" ] + timedelta( minutes=-5 )) :
                cur_serv.last_msg = await client.send_message( msg.channel, "Slow down!" )
                return
            cur_serv.last_msg = await client.send_message( msg.channel, get_got_time() )
            cur_serv.last_used[ "got" ] = now
            return
        elif args[0] == "hangman" :
            if cur_serv.search_helper.searched :
                await client.send_message( msg.channel, "Server is searching, try again in a bit." )
                return
            cur_serv.last_msg = await client.send_message( msg.channel, "```Starting up a game of hangman!\nPicking a word and getting ready...\n```")
            cur_serv.games( "hangman" )
            cur_serv.last_msg = await client.edit_message( cur_serv.last_msg, cur_serv.last_msg.content+"```All set, send your guesses!```" )
            ret_str = "```Max Guesses: "+str(cur_serv.game.max_guesses)+"\n"
            for i in range( len( cur_serv.game.word ) ):
                ret_str += "_ "
            ret_str += '```\n'
            cur_serv.last_msg = await client.send_message( msg.channel, ret_str )
            return
        elif args[0] == "help" or args[0] == "h" :
            cur_serv.last_message = await client.send_message( msg.author, help_string() )
            return
        elif args[0] == "restart" :
            if check_auth( msg.author, cur_serv ) == True :
                cur_serv.last_msg = await client.send_message( msg.channel, "Restarting bot." )
                call( ["service", "craig-bot", "restart"] )
                return
            cur_serv.last_msg = await client.send_message( msg.channel, not_auth )
            return
        elif args[0] == "stop" :
            if check_auth( msg.author, cur_serv ) == True :
                cur_serv.last_msg = await client.send_message( msg.channel, "Stopping bot." )
                call( ["service", "craig-bot", "stop"] )
                return
            cur_serv.last_msg = await client.send_message( msg.channel, not_auth )
            return
        elif args[0] == "status" :
            if check_auth( msg.author, cur_serv ) == True :
                my_pid = os.getpid()
                created = os.path.getmtime( "/proc/"+str(my_pid) )
                creat_str = "```smalltalk\nBot running with PID "+str(my_pid)+" since "
                creat_str += datetime.datetime.fromtimestamp( int(created) ).strftime( date_format )
                creat_str += "```\n"
                cur_serv.last_msg = await client.send_message( msg.channel, creat_str )
                return
            cur_serv.last_msg = await client.send_message( msg.channel, not_auth )
            return
        elif args[0] == "auth" :
            ret_str = "```The following users and roles (in no order) are authorized for this server: \n"
            for a in cur_serv.auth :
                ret_str += a+"\n"
            ret_str += "```"
            cur_serv.last_msg = await client.send_message( msg.channel, ret_str )
            return
        elif args[0] == "8ball" :
            question = "```You asked: \n"
            if len(args) == 1 :
                cur_serv.last_msg = await client.send_message( msg.channel, "You didn't ask me anything!" )
                return
            for arg in args[1:]:
                question += arg+" "
            question = question[:len(question)-1]
            ret_str = question+"```\n```\nThe Magic 8 Ball says:\n"
            ret_str += magic_8ball()+"```\n"
            cur_serv.last_msg = await client.send_message( msg.channel, ret_str )
            return
        else:
            return
    
    # cant go in main loop since it checks busy
    if msg.content == "!gamequit" and cur_serv.busy :
        if check_auth( msg.author, cur_serv ) == True :
            cur_serv.last_msg = await client.send_message( msg.channel, "Terminating game of"+cur_serv.game.type+"```\n" )
            cur_serv.game = None
            cur_serv.busy = False
            return
        if not cur_serv.busy:
            cur_serv.last_msg = await client.send_message( msg.channel, "Doesn't look you're playing any games here right now, m8.\n" )
            return
        cur_serv.last_msg = await client.send_message( msg.channel, not_auth )
        return
    
    # play games
    if cur_serv.busy :
        if msg.content[:len(prefix)] == prefix:
            await client.send_message( msg.channel, "Server is busy, try again in a bit!\n" )
            return
        if cur_serv.game.type == "hangman" :
            # valid guess
            if len(msg.content) != 1 : # invalid guess
                return
            # check if guess is char and update guess table
            for i in range( 25 ):
                if msg.content.lower() == chr( i+97 ):
                    if cur_serv.game.guesses[ msg.content ] == False:
                        cur_serv.game.guesses[ msg.content ] = True
                    else:
                        await client.send_message( msg.channel, msg.content+" has already been guessed!\n" )
                        await client.delete_message( msg )
                        return
            # guess in word
            in_word = False
            for letter in cur_serv.game.word :
                if msg.content == letter:
                    in_word = True
                    break
            if not in_word:
                cur_serv.game.guess_count += 1
            # loss
            if cur_serv.game.guess_count >= cur_serv.game.max_guesses:
                ret_str = "```Game over!\nThe word was: "+cur_serv.game.word+"```"
                cur_serv.last_msg = await client.edit_message( cur_serv.last_msg, ret_str )
                cur_serv.game = None
                cur_serv.busy = False
                return
            ret_str = "```Guesses Left: "+str( cur_serv.game.max_guesses - cur_serv.game.guess_count )+"\n"
            # build the current 'word'
            t_str = ""
            for letter in cur_serv.game.word :
                if cur_serv.game.guesses[ letter ] == True:
                    ret_str += letter+" "
                    t_str += letter
                else:
                    ret_str += "_ "
            # chicken dinner
            if t_str == cur_serv.game.word :
                ret_str = "```Game over, you guessed the word!\nAnswer: "+cur_serv.game.word+"```"
                await client.delete_message( msg )
                cur_serv.last_msg = await client.edit_message( cur_serv.last_msg, ret_str )
                cur_serv.game = None
                cur_serv.busy = False
                return
            ret_str += "\n"
            if in_word:
                ret_str += '"'+msg.content+'"'+" is in the word!\n"
            else:
                ret_str += '"'+msg.content+'"'+" is not in the word!\n"
            ret_str += "```"
            cur_serv.last_msg = await client.edit_message( cur_serv.last_msg, ret_str )
            await client.delete_message( msg )
            return
        else:
            return
        return
            
    # search results
    if ( cur_serv.search_helper.searched == True ):
        if( msg.content.isdigit and msg.author.name == cur_serv.search_helper.search_msg.author.name ):
            ret_str = cur_serv.search( msg.content, "final", None, None )
            cur_serv.last_msg = await client.edit_message( cur_serv.last_msg, ret_str )
            return
        else:
            return
# bottom of on_message()       

client.run( discord_key )
