import datetime, urllib3, random, json, os, getpass
from datetime import date, timedelta
from dateutil import parser, relativedelta
from tzlocal import get_localzone as glz
from discord.utils import find

date_str = "%m/%d/%y %I:%M %p"

def bs_now():
    return datetime.datetime.now().astimezone( glz() )

def get_got_time():
    """Returns a formatted string with the time until the next and time from the previous GoT episode. Episode name is also returned in the string."""
    now = bs_now()
    uri = "http://api.tvmaze.com/shows/82?embed[]=nextepisode&embed[]=previousepisode"
    http = urllib3.PoolManager()
    response = http.request( 'GET', uri )
    data = json.loads( response.data.decode( 'utf-8' ) )
    next_ep = parser.parse( data["_embedded"]["nextepisode"]["airstamp"] ).astimezone( glz() )
    next_ep_name = data["_embedded"]["nextepisode"]["name"]
    prev_ep = parser.parse( data["_embedded"]["previousepisode"]["airstamp"] ).astimezone( glz() )
    prev_ep_name = data["_embedded"]["previousepisode"]["name"]
    next_diff = relativedelta.relativedelta( next_ep, now )
    prev_diff = relativedelta.relativedelta( prev_ep, now )
    ret_str = "```smalltalk\nLast Episode: "+prev_ep_name+" aired "
    if (abs(prev_diff.months) > 0):
        ret_str+=str(abs(prev_diff.months))+" months "
    if (abs(prev_diff.days) > 0):
        ret_str+=str(abs(prev_diff.days))+" days "
    if (abs(prev_diff.hours) > 0):
        ret_str+=str(abs(prev_diff.hours))+" hours "
    if (abs(prev_diff.minutes) > 0):
        ret_str+=str(abs(prev_diff.minutes))+" minutes and "
    if (abs(prev_diff.seconds) > 0):
        ret_str+=str(abs(prev_diff.seconds))+" seconds ago\n"
    ret_str+="Next Episode: "+next_ep_name+" airs in "
    if next_diff.months > 0 :
        ret_str+=str(next_diff.months)+" months "
    if next_diff.days > 0 :
        ret_str+=str(next_diff.days)+" days "
    if next_diff.hours > 0 :
        ret_str+=str(next_diff.hours)+" hours "
    if next_diff.minutes > 0 :
        ret_str+=str(next_diff.minutes)+" minutes and "
    if next_diff.seconds > 0 :
        ret_str+=str(next_diff.seconds)+" seconds\n"
    ret_str += "```"
    return ret_str

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

def help_str( p ):
    ret_str = "```smalltalk\n{}help/{}h - Display this dialogue.\n    Parameters are given as [optional] and <required>\n\n".format( p, p )
    ret_str += "{}status - Display the bot's PID and when it was started.\n\n".format( p )
    ret_str += "{}set_game <message> - Set the bot's \"Now playing\" message.\n\n".format( p )
    ret_str += "{}auth - Display currently authorized user's and their level.\n\n".format( p )
    ret_str += "{}add <user> <level> - Add <user> to the auth list at level, user maybe @mention or a username.\n\n".format( p )
    ret_str += "{}save [file] - Writes the auth data to [auth_file], destroying whatever is there.\n    NOTE: The auth file will always be loaded from './'\n\n"
    ret_str += "{}del <user> - As with add but removes the user.\n\n".format( p )
    ret_str += "{}whoami - Display's the sender's username, Discord ID and current auth level.\n\n".format( p )
    ret_str += "{}got - Display when the last GoT episode aired and when the next will air (in terms of days, hours, minutes and seconds).\n\n".format( p )
    ret_str += "{}eval <func> - Performs simple calculations upon <func>, eg 2+2, etc\n'n".format( p )
    ret_str += "{}yt <search query> - Search YouTube for a video.\n\n".format( p )
    ret_str += "{}tmdb <search query> - Search TMDb for a film. Currently television show search is not implemented.\n\n".format( p )
    ret_str += "{}8ball <question> - Ask the magic 8-Ball a question and find out your fate!\n\n".format( p )
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
    f = find( lambda m: m.name == user, member_list )
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

def creat_time():
    my_pid = os.getpid()
    created = os.path.getmtime( "/proc/"+str(my_pid) )
    creat_str = "```smalltalk\nBot running with PID {} as {}({}) since {}```\n".format( str(my_pid), getpass.getuser(), os.getuid(), datetime.datetime.fromtimestamp( int(created) ).strftime( date_str ))
    return creat_str