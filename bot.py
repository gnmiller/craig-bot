import discord, asyncio, datetime, json, pytz, os, urllib3, random
from subprocess import call
from datetime import timedelta
from craig_server import craig_server as __serv, craig_user as __user
from craig_helper import get_got_time, magic_8ball, help_string, cmds

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
    await client.change_presence( game=discord.Game( name='Deez Nuts in ' + str(len( client.servers ))+" servers" ) )
    print( "startup finished" )
    started = True

@client.event
async def on_server_join( server ):
    for s in serv_arr:
        if s.me.name == server.name:
            return
    new_serv = __serv( server, max_time )
    for u in s.me.members:
        tmp = __user( u, u.state, datetime.datetime.now() )
        s.users.append( tmp )
    serv_arr.append( new_serv )
    await client.change_presence( game=discord.Game( name='Deez Nuts in ' + str(len( client.servers ))+" servers" ) )
    
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
    # valid cmd
    msg_prefix = msg.content[:len(prefix)]
    args = msg.content[len(prefix):].split()
    if prefix in msg_prefix:
        if args[0] not in cmds:
            return
    else:
        return
    # get what server sent message
    cur_serv = None
    for s in serv_arr :
        if s.me == msg.server: 
            cur_serv = s
    # timeout check
    if cur_serv.search_helper.timeout() == True :
        cur_serv.search_helper.clear_search()
        await client.send_message( msg.channel, "Timeout!" )
    not_auth = "You are not authorized to send this command."
    now = pytz.utc.localize( datetime.datetime.now() )
    # main processor
    if not cur_serv.busy :
        if args[0] == "qr" :
            if (len(args) != 2) :
                cur_serv.last_msg = await client.send_message( msg.channel, "```Usage:\n    "+prefix+"cr role_name```" )
                return
            if not now >= ( cur_serv.last_used["qr"] + timedelta( minutes=2 ) ):
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
            if not now >= ( cur_serv.last_used[ "got" ] + timedelta( minutes=5 )) :
                cur_serv.last_msg = await client.send_message( msg.channel, "Slow down!" )
                return
            cur_serv.last_msg = await client.send_message( msg.channel, get_got_time() )
            cur_serv.last_used[ "got" ] = now
            return
        elif args[0] == "hangman":
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
            cur_serv.last_message = await client.send_message( msg.author, help_string( prefix ) )
            return
        elif args[0] == "restart" :
            if cur_serv.check_auth( msg.author ) == True :
                cur_serv.last_msg = await client.send_message( msg.channel, "Restarting bot." )
                call( ["service", "craig-bot", "restart"] )
                return
            cur_serv.last_msg = await client.send_message( msg.channel, not_auth )
            return
        elif args[0] == "stop" :
            if cur_serv.check_auth( msg.author ) == True :
                cur_serv.last_msg = await client.send_message( msg.channel, "Stopping bot." )
                call( ["service", "craig-bot", "stop"] )
                return
            cur_serv.last_msg = await client.send_message( msg.channel, not_auth )
            return
        elif args[0] == "status" :
            if cur_serv.check_auth( msg.author ) == True :
                my_pid = os.getpid()
                created = os.path.getmtime( "/proc/"+str(my_pid) )
                creat_str = "```smalltalk\nBot running with PID "+str(my_pid)+" since "
                creat_str += datetime.datetime.fromtimestamp( int(created) ).strftime( date_format )
                creat_str += "```\n"
                cur_serv.last_msg = await client.send_message( msg.channel, creat_str )
                return
            cur_serv.last_msg = await client.send_message( msg.channel, not_auth )
            return
        elif args[0] == "auth":
            if len(args) == 1:
                ret_str = "```The following users and roles are authorized for this server: \nUsers\n----------------\n"
                if len(cur_serv.auth["user"]) <= 0:
                    ret_str += "None\n"
                for a in cur_serv.auth["user"]:
                    ret_str += a+"\n"
                ret_str += "----------------\nRoles\n----------------\n"
                if len(cur_serv.auth["role"]) <= 0:
                    ret_str += "None\n"
                for a in cur_serv.auth["role"]:
                    ret_str += a+"\n"
                ret_str += "```"
                cur_serv.last_msg = await client.send_message( msg.channel, ret_str )
                return
            elif len(args) == 3:
                if cur_serv.check_auth( msg.author ):
                    cur_serv.add_auth( args[2], args[1] )
                    cur_serv.last_msg = await client.send_message( msg.channel, "Adding new "+args[1]+" to the server's auth list with name: "+args[2]+" (temporarily).\n" )
                    return
                else:
                    cur_serv.last_msg = await client.send_message( msg.channel, not_auth )
                    return
            else:
                cur_sev.last_msg = await client.send_message( msg.channel, "Bad format! Check the help dialogue.\n" )
                return
        elif args[0] == "deauth":
            if cur_serv.check_auth( msg.author ):
                if len(args) == 1:
                    cur_serv.last_msg = await client.send_message( msg.channel, "You need to specify a name!\n" )
                if cur_serv.del_auth( args[1] ) == True:
                    cur_serv.last_msg = await client.send_message( msg.channel, "Removing "+args[1]+" from the authorized list.\n" )
                    return
                cur_serv.last_msg = await client.send_message( msg.channel, "It doesn't look like "+args[1]+" was in the authorized list.\n" )
                return
            else:
                cur_serv.last_msg = await client.send_message( msg.channel, not_auth )
                return
        elif args[0] == "8ball":
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
    if args[0] == "gamequit" and cur_serv.busy :
        if cur_serv.check_auth( msg.author ) == True :
            cur_serv.last_msg = await client.send_message( msg.channel, "```Terminating game of "+cur_serv.game.type+"```\n" )
            cur_serv.reset_game()
            return
        if not cur_serv.busy:
            cur_serv.last_msg = await client.send_message( msg.channel, "Doesn't look you're playing any games here right now, m8.\n" )
            return
        cur_serv.last_msg = await client.send_message( msg.channel, not_auth )
        return
    
    # play games
    if cur_serv.busy :
        if msg_prefix == prefix:
            await client.send_message( msg.channel, "Server is busy, try again in a bit!\n" )
            return
        # play hangman
        if cur_serv.game.type == "hangman" :
            guess = msg.content
            word = cur_serv.game.word
            # valid guess
            if len( guess ) != 1 : # invalid guess
                return
            # game state post guess
            status = cur_serv.play_hangman( guess )
            if status == "no":
                await client.send_message( msg.channel, "Doesn't look like we're playing hangman!\n" )
                return
            if status == "guessed":
                await client.send_message( msg.channel, guess+" has already been guessed!\n" )
                await client.delete_message( msg )
                return
            if status == "loss":
                ret_str = "```Game over!\nThe word was: "+word+"```\n"
                await client.delete_message( msg )
                cur_serv.last_msg = await client.edit_message( cur_serv.last_msg, ret_str )
                return
            if status == "won":
                ret_str = "```Congratulations! You guessed the word: "+word+"```\n"
                await client.delete_message( msg )
                cur_serv.last_msg = await client.edit_message( cur_serv.last_msg, ret_str )
                return
            # play the game
            board = cur_serv.hangman_word()
            remain = cur_serv.game.max_guesses - cur_serv.game.guess_count
            ret_str = "```Guesses left: "+str(remain)+"\n"
            if status == "in":
                ret_str += board+"\n"+guess+" is in the word!\n```"
                cur_serv.last_msg = await client.edit_message( cur_serv.last_msg, ret_str )
                await client.delete_message( msg )
                return
            if status == "out":
                ret_str += board+"\n"+guess+" is not in the word.\n```"
                cur_serv.last_msg = await client.edit_message( cur_serv.last_msg, ret_str )
                await client.delete_message( msg )
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
