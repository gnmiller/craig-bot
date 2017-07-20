import datetime, json, urllib3, random, os, pytz
from apiclient.discovery import build
from datetime import date, timedelta
from dateutil import parser, relativedelta
from math import floor
import signal

cmds = ["qr","yt","tmdb","got","hangman","8ball","auth","deauth","gamequit","status","restart","stop","help","h","save_auth","load_auth"]

path = os.path.dirname(os.path.realpath(__file__))
with open( path+'/settings.json' ) as f:
    settings = json.load( f )

class result:
    """Search results container."""
    name = ""
    id = ""
    def __init__( self, name, id ):
        self.name = name
        self.id = id

class search:
    """Helper class for searching. Holds global information about the state of the search and it's results."""
    def __init__( self, name, timeout ):
        self.serv_name = name
        self.searched = False
        self.search_time = datetime.datetime.now()
        self.search_msg = None
        self.results = {}
        self.mode = "none"
        self.max_time = timeout

    def timeout( self ):
        """Determines whether or not a search is in progress and if it has timed out."""
        now = datetime.datetime.now()
        if( self.searched == False ):
            return False
        elif( now > ( self.search_time + timedelta( seconds = self.max_time ) ) ):
            return True
        else:
            return False

    def search_clear( self ):
        """Reset the search object to a fresh state for the next search."""
        self.searched = False
        self.searc_time = datetime.datetime.now()
        self.search_msg = None
        self.results = {}
        self.mode = "none"
        self.search_msg = None

    def youtube_search( self, term, apikey, msg ):
        """Authenticate to the YouTube API  using apikey and perform a search with term returning a formatted string result."""
        if( self.timeout() == True ):
            return "timeout"
        if( self.searched == True ):
            return "previous search not completed"
        self.search_clear()
        youtube = build( "youtube", "v3", developerKey=apikey )
        response = youtube.search().list( q=term, part="id,snippet", maxResults=50 ).execute()

        count = 0
        res_str="```smalltalk\n"
        for res in response.get( "items", [] ):
            if res["id"]["kind"] == "youtube#video" :
                count+=1
                res_str+=str(count)+". "+res["snippet"]["title"]+"\n"
                self.results[count] = result( res["snippet"]["title"], res["id"]["videoId"] )
                if count >= 10 :
                    break
            else:
                continue

        self.mode = "youtube"
        self.searched = True
        self.search_time = datetime.datetime.now()
        self.search_msg = msg
        res_str+="```"
        return res_str

    def tmdb_search( self, term, apikey, msg ):
        """Authenticate to the TMDb API using apikey and perform a search with term returning a formatted string result."""
        if( self.timeout() == True ):
            return "timeout"
        if( self.searched == True ):
            return "previous search still in progress"
        self.search_clear()
        uri = "https://api.themoviedb.org/3/search/movie?api_key="+apikey
        uri += "&query="+term
        http=urllib3.PoolManager()
        response = http.request( "GET", uri )
        data=json.loads( response.data.decode( 'utf-8' ) )
        count=0
        res_str="```smalltalk\n"
        for res in data.get( "results", [] ):
            rating = res["vote_average"]
            rating_count = res["vote_count"]
            year = res["release_date"][0:4]
            tmp = result( res["title"], res["id"] )
            if count >= 10 :
                break
            count += 1
            res_str += str(count)+". "+tmp.name+" ("+str(year)+" -- "+str(rating)+"/10 ("
            res_str += str(rating_count)+" votes)\n"
            self.results[count] = tmp

        self.searched = True
        self.mode = "tmdb"
        self.search_msg = msg
        self.search_time = datetime.datetime.now()
        res_str+="```"
        return res_str

    def finalize_search( self, val ):
        """Select which results to use"""
        if( self.timeout() == True ):
            return "timeout"
        if( self.searched == False ):
            return "why did you do this?"
        if self.mode == "youtube" :
            ret_str = "Selected video -" +val+ "-\nTitle: "+self.results[int(val)].name+"\nhttps://www.youtube.com/watch?v="+str(self.results[int(val)].id)
        elif self.mode == "tmdb" :
            ret_str = "Selected video -"+val+"-\nTitle: "+self.results[int(val)].name+"\nhttps://www.themoviedb.org/movie/"+str(self.results[int(val)].id)
        elif self.mode == "ff" : #NYI
            ret_str = "Selected character - "+val+"-\nName: "+self.results[val].name+"\nhttps://api.xivdb.com/characters/"+str(self.results[int(val)].id)
        else:
            return "what"
        self.search_clear()
        return ret_str
        
class hangman:
    """Hangman game. max_guesses can be modified for longer or shorter games. NOTE: Requires /usr/share/dict/words (provided by package words). Also any non-alphanumeric characters are removed before starting."""
    def __init__( self ):
        self.word = None
        self.type = "hangman"
        self.guess_count = 0
        self.word_list = None
        self.max_guesses = settings["bot"]["hangman"]["max_guess"]
        # use a dict to track guesses
        self.guesses = {}
        for i in range( 25 ):
            self.guesses[ chr( i+97 ) ] = False
        words = []
        with open( "/usr/share/dict/words" ) as f:
            words = f.read().split("\n")
        # find a sort of long word
        rand = random.randint( 0, len( words ) )
        t_word = words[ rand ]
        while len( t_word ) < 6 :
            rand = random.randint( 0, len( words ) )
            t_word = words[ rand ]
        self.word = t_word.lower()
        import re
        reg = re.compile('[^a-zA-Z]')
        self.word = reg.sub( '', self.word )
        
def get_got_time():
    """Returns a formatted string with the time until the next and time from the previous GoT episode. Episode name is also returned in the string."""
    cur = datetime.datetime.now()
    uri = "http://api.tvmaze.com/shows/82?embed[]=nextepisode&embed[]=previousepisode"
    http = urllib3.PoolManager()
    response = http.request( 'GET', uri )
    data = json.loads( response.data.decode( 'utf-8' ) )
    next_ep = parser.parse( data["_embedded"]["nextepisode"]["airstamp"] )
    next_ep_name = data["_embedded"]["nextepisode"]["name"]
    prev_ep = parser.parse( data["_embedded"]["previousepisode"]["airstamp"] )
    prev_ep_name = data["_embedded"]["previousepisode"]["name"]
    cur = pytz.utc.localize( cur )
    next_diff = relativedelta.relativedelta( next_ep, cur )
    prev_diff = relativedelta.relativedelta( prev_ep, cur )
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
        return yes[ random.randint( 0, len( yes ) ) ]
    if r == 1 :
        return maybe[ random.randint( 0, len( maybe ) ) ]
    if r == 2 :
        return no[ random.randint( 0, len( no ) ) ]
    return "what"

def save_auth( servers, auth_file ):
    """Write the auth file with the current auth state for all servers. This is destructive and will clobber the existing file."""
    data = {}
    data["user"] = {}
    data["role"] = {}
    for s in servers:
        serv_name = s.me.name.lower()
        data["user"][serv_name] = []
        data["role"][serv_name] = []
        for u in s.auth["user"]:
            data["user"][serv_name].append( u.lower().strip() )
        for r in s.auth["role"]:
            data["role"][serv_name].append( r.lower().strip() )
    with open(auth_file, 'w') as f:
        json.dump(data, f, ensure_ascii=False)
    return

def reload_auth( servers, auth_file ):
    for s in servers:
        s.load_auth( auth_file )
    return
    

def help_string( prefix ):
    """Construct the string for the help dialogue."""
    ret_str = "```css\nBeeStingBot help menu\nBot prefix: "+prefix+"\nCommands\n------------```\n"
    ret_str += "```css\n"
    ret_str += prefix+"yt <search query>\n"+"    Search YouTube for a video.\n\n"
    ret_str += prefix+"tmdb <search query>\n"+"    Search TMDb for a movie.\n\n"
    ret_str += prefix+"got\n    Print brief info on the most recent and next Game of Thrones episode.\n\n"
    ret_str += prefix+"qr <role_name>\n    Print out status on users that belong to role_name\n            Only information since the bot was last restarted is kept.\n\n"
    ret_str += prefix+"hangman\n    Start a game of hangman.\n    This will suspend other bot actions until the game is over.\n\n"
    ret_str += prefix+"qr <role_name>\n    Print out status on users that belong to role_name\n    Only information since the bot was last restarted is kept.\n\n"
    ret_str += prefix+"8ball <question>\n    Ask the Magic 8-ball a question and see what the fates have in store.\n\n"
    ret_str += prefix+"auth [user|role] [username|rolename] (+)\n    Returns a list of the users authorized for privileged commands on the server.\n    Privileged commands are denoted with a (+) in the help dialogue\n    If role/user is specified (and a name given) the server will temporarily authorize that user/role.\n    Does not check if role or user actually exists\n\n"
    ret_str += prefix+"deauth <username|rolename> (+)\n    De-authorize the given role or user. If the user/role is in the authorized config file it will re-load on re-start.\n\n"
    ret_str += prefix+"save_auth (+)\n    Write the auth data out to file.\n    This is destructive and will clobbed the contents of authorized.json\n\n"
    ret_str += prefix+"load_auth (+)\n    Load the auth data from the auth file.\nThis will clobber any temporary authorizations unless they are saved first.\n\n"
    ret_str += prefix+"gamequit (+)\n    Quit the current game. Does nothing if a game is not in progress.\n\n"
    ret_str += prefix+"stop (+)\n    Stops the bot.\n\n"
    ret_str += prefix+"restart (+)\n    Restarts the bot.\n\n"
    ret_str += prefix+"status (+)\n    Displays status of the bot (PID and start time).\n\n"
    ret_str += "```"
    return ret_str