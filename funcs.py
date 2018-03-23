import datetime, urllib3, random, json, os, getpass
from datetime import date, timedelta
from dateutil import parser, relativedelta
from tzlocal import get_localzone as glz
from discord.utils import find

date_str = "%m/%d/%y %I:%M %p"

def bs_now():
    return datetime.datetime.now().astimezone( glz() )

def convert( args ):
    """args should be a tuple ( value, src_curr, dest_curr )"""
    c = cc()
    return 

def magic_8ball():
    """Select and return a random answer from the magic 8-ball"""
    yes = ["It is decidedly so","Without a doubt","Yes, definitely","You can count on it","As I see it: Yes", "Most likely", "Outlook good", "Yes!", "All signs point to yes"]
    maybe = ["Reply hazy, try again", "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again"]
    no = ["Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]
    r = random.randint( 0, 2 )
    if r == 0 :
        return yes[ random.randint( 0, len( yes )-1 ) ]
    if r == 1 :
        return maybe[ random.randint( 0, len( maybe )-1 ) ]
    if r == 2 :
        return no[ random.randint( 0, len( no )-1 ) ]
    return "what"

def help_str( p, al ):
    ret_str = "```smalltalk\n{}help/{}h - Display this dialogue.\n    Parameters are given as [optional] and <required>\n    Commands that require privilege are displayed with a '*'.\n    Only commands which you can execute are displayed.\n\n".format( p, p )
    ret_str += "{}auth - Display currently authorized user's and their level.\n\n".format( p )
    if al >= 1: # min auth of 1 needed
        ret_str += "{}add <user> <level> (*) - Add <user> to the auth list at level, user maybe @mention or a username.\n\n".format( p )
        ret_str += "{}del <user> (*) - As with add but removes the user.\n\n".format( p )
        ret_str += "{}set_game <string> (*) - Sets the bot's now playing message.\n\n".format( p )
        ret_str += "{}play (*) - Make the bot play a song. If a song is already playing the new one is queued. If the bot is not in a channel already an error is also returned.\n\n".format( p )
        ret_str += "{}queue (*) - Display the current queue of YouTube videos.\n\n.".format( p )
    if al >= 2: # min auth of 2
        ret_str += "{}stop (*) - Stop playback of the current track. If no song is playing returns an error to the channel. **UNTESTED WITH QUEUE**\n\n".format( p )
    if al >= 3: # min auth of 3
        ret_str += "{}join (*) - Joins the bot to a voice channel.\n\n".format( p )
        ret_str += "{}leave (*) - Leaves the active voice channel.\n\n".format( p )
        ret_str += "{}status (*) - Display the bot's PID and when it was started.\n\n".format( p )
    if al >= 4: # min auth of 4
        ret_str += "{}region <region>* - Select a new region for the current server.\nValid selections are: us_west, us_east, us_central, eu_west, eu_central, singapore, london, sydney, amsterdam, frankfurt, brazil.\n\n".format( p )
    if al == 5: # admin only
        ret_str += "{}save [file] (*) - Writes the auth data to [auth_file], destroying whatever is there.\n    NOTE: The auth file will always be loaded from './'\n\n".format( p )
    ret_str += "{}whoami - Display's the sender's username, Discord ID and current auth level.\n\n".format( p )
    ret_str += "{}info <user> - Like whoami but may specify a username.\n\n".format( p )
    ret_str += "{}got - Display when the last GoT episode aired and when the next will air (in terms of days, hours, minutes and seconds).\n\n".format( p )
    ret_str += "{}eval <func> - Performs simple calculations upon <func>, eg 2+2, etc\n\n".format( p )
    ret_str += "{}yt <search query> - Search YouTube for a video.\n\n".format( p )
    ret_str += "{}tmdb <search query> - Search TMDb for a film. Currently television show search is not implemented.\n\n".format( p )
    ret_str += "{}8ball <question> - Ask the magic 8-Ball a question and find out your fate!\n\n".format( p )
    ret_str += "{}shorten <URI> - Shorten a URL using https://btcraig.in/shorten.php.\n\n".format( p )
    ret_str += "```"
    return ret_str

def write_auth( servers, auth_file ):
    auth_data = {}
    for s in servers:
        auth_data[ s.me.id ] = s.auth
    with open( auth_file, 'w' ) as f:
        json.dump( auth_data, f, ensure_ascii=False )
    f.close()
    return

def find_user( user, member_list ):
    # find by name
    f = find( lambda m: m.name.lower() == user.lower(), member_list )
    if f == None: # find by id
        f = find( lambda m: m.id == user, member_list )
    if f == None: # find by mention
        f = find( lambda m: m.mention == user, member_list )
    return f

def build_func( args ):
    func = ""
    ops = [ '+', '-', '/', '*', '%', '.' ]
    for i in range( 1, len(args) ):
        for c in args[i]:
            if c in ops or c.isdigit():
                func += c
            else:
                return -1
    return func

def print_auth( auth_list ):
    auth_users = {}
    p_str = "```smalltalk\nCurrently authorized users \n{}\n".format( '|'+('-'*47)+'|' )
    p_str += "| Username (ID) " .ljust(32)+("| Auth Level ".ljust(16))+"|\n"
    for k,v in auth_list.items():
        p_str += ("| {} ({}) ".format(v[0].name, v[0].id).ljust(32)[:32])+("| {}".format(str(v[1])).ljust(16))+"|\n"
    p_str += "{}```".format( '|'+('-'*47)+'|' )
    return p_str

def query_string( content ):
    query = ""
    for i in range( 1, len(content) ):
        query += content[i]+"+"
    query = query[:len(query)-1]
    return query

async def whoami( serv, msg ):
    msg_str = "```smalltalk\nUsername: {}\nID: {}\nAuth Level: {}\n```".format( msg.author.name, msg.author.id, serv.get_auth( msg.author ) )
    serv.queue_cmd( msg )
    return await client.send_message( msg.channel, msg_str )

def find_bs_user( search, server ):
    """Return a bs_user object for the user (ID, name, @), Server should be bs_server object"""
    user = find_user( search, server.me.members )
    if not user == None:
        return server.users[user.id]
    else:
        return None

def creat_time():
    my_pid = os.getpid()
    created = os.path.getmtime( "/proc/"+str(my_pid) )
    creat_str = "```smalltalk\nBot running with PID {} as {}({}) since {}```\n".format( str(my_pid), getpass.getuser(), os.getuid(), datetime.datetime.fromtimestamp( int(created) ).strftime( date_str ))
    return creat_str
