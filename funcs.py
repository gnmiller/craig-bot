import datetime, urllib3, pytz, random, json
from datetime import date, timedelta
from tzlocal import get_localzone


def get_got_time():
    """Returns a formatted string with the time until the next and time from the previous GoT episode. Episode name is also returned in the string."""
    now = datetime.datetime.now().astimezone( get_localzone() )
    uri = "http://api.tvmaze.com/shows/82?embed[]=nextepisode&embed[]=previousepisode"
    http = urllib3.PoolManager()
    response = http.request( 'GET', uri )
    data = json.loads( response.data.decode( 'utf-8' ) )
    next_ep = parser.parse( data["_embedded"]["nextepisode"]["airstamp"] ).astimezone( get_localzone() )
    next_ep_name = data["_embedded"]["nextepisode"]["name"]
    prev_ep = parser.parse( data["_embedded"]["previousepisode"]["airstamp"] ).astimezone( get_localzone() )
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