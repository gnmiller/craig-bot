import json, os, sqlite3, openai, re, ast, apiclient, random, statistics
from urllib.error import HTTPError
from datetime import datetime
from collections import OrderedDict
from cb_classes import cb_guild

import pdb

now = lambda : datetime.today().strftime('%Y-%m-%d') # YYYY-MM-DD
dictify = lambda string: ast.literal_eval( string ) # turn a str thats a dict into an actual dict
yt_uri = lambda string: "https://www.youtube.com/watch?v={}".format( string )

def get_settings( file ):
    """Load file as a json and return it"""
    path = os.path.dirname( os.path.realpath( __file__ ))
    try:
        with open( '{}/{}'.format(path,file) ) as f:
            settings = json.load( f )
        f.close()
        return settings
    except FileNotFoundError as e:
        print( "Settings file not found. Expecting: {}/settings.json", os.getwd() )
        print( e )
        return -1

# put this in a file?
prep_queries = [
    "CREATE TABLE IF NOT EXISTS guilds(name,id,data,date_added)",
    "CREATE TABLE IF NOT EXISTS oai_cmds(prompt,model,resp,uid,date)",
    "CREATE TABLE IF NOT EXISTS flagged_msgs(username,user_id,guild,guild_id,content,score,date)",
    "CREATE TABLE IF NOT EXISTS rolls(id INTEGER PRIMARY KEY,num_sides,result)",
    "CREATE TABLE IF NOT EXISTS admin_users(id INTEGER PRIMARY KEY,user_id,guild_id,role)",
    "CREATE TABLE IF NOT EXISTS admin_groups(id INTEGER PRIMARY KEY,group_id,guild_id,role)"
]
def init_db(db_file):
    """ Prep the sqlite file with our defined array of tables."""
    res = []
    try:
        if not os.path.isfile(db_file):
            con = sqlite3.connect( db_file )
            cur = con.cursor()
            for q in prep_queries:
                res.append(cur.execute( q ))
            con.commit()
            con.close()
        else:
            raise RuntimeError("DB File already exists.")
    except RuntimeError as e:
        con = sqlite3.connect( db_file )
        cur = con.cursor()
        for q in prep_queries:
            res.append(cur.execute( q ))
        con.commit()
        con.close()
        return
    except Exception as e:
        return None
    return res

def _check_db( db_file ):
    if not os.path.isfile( db_file ):
        raise FileNotFoundError
    else:
        return sqlite3.connect( db_file )

def check_guild( guild, db_file="craig-bot.sqlite" ):
    """Check if a guild is logged in the local DB.
    Returns a cb_guild object if it exists otherwise None"""
    try:
        db = _check_db( db_file )
        q = "SELECT name,id,data FROM guilds WHERE guilds.id=\"{}\" AND guilds.name=\"{}\"".format( guild.id, guild.name )
        cur = db.cursor()
        res = cur.execute( q )
        row = res.fetchone()
        db.close()
        if row == None:
            return None
        data = dictify(row[2])
        admin_data = _get_admins( guild, db_file )
        if not guild.owner.id in admin_data[0]:
            admin_data[0].append(guild.owner.id)
        _insert_admin_user(guild.owner,guild,db_file=db_file)
        ret = cb_guild( int(row[1]), admin_data[0], admin_data[1], data )
        if row == None:
            return None
        else:
            return ret
    except FileNotFoundError as e:
        print("No db file found! Expecting: {}/{}",os.getcwd(),db_file)
        return None
    
def _get_admins( guild, db_file="craig-bot.sqlite" ):
    """Return a tuple of 2 lists. [0] refers to admin users, [1] refers to admin groups"""
    auq = "SELECT user_id,guild_id FROM admin_users WHERE admin_users.guild_id=\"{}\"".format(guild.id)
    agq = "SELECT group_id,guild_id FROM admin_groups WHERE admin_groups.guild_id=\"{}\"".format(guild.id)
    try:
        db = _check_db( db_file )
        cur = db.cursor()
        aurows = cur.execute(auq)
        agrows = cur.execute(agq)
        admin_users = []
        admin_groups = []
        for u in aurows:
            admin_users.append(u)
        for g in agrows:
            admin_groups.append(g)
        db.close()
        return(admin_users,admin_groups)
    except FileNotFoundError as e:
        print("No db file found! Expecting: {}/{}",os.getcwd(),db_file)
        return None

def _check_admin( guild, user, db_file="craig-bot.sqlite" ):
    admin_data = _get_admins( guild, db_file )
    if user.id in admin_data[0]:
        return True
    for g in user.roles:
        if g.id in admin_data[1]:
            return True
    return False

def _insert_admin_user( user, guild, role="admin", db_file="craig-bot.sqlite" ):
    try:
        db = _check_db( db_file )
    except FileNotFoundError as e:
        return e
    if not _check_admin( user, guild, db_file ):
        q = "INSERT INTO admin_users (user_id,guild_id,role) VALUES (\"{}\",\"{}\",\"{}\")".format(
                                                        user.id,
                                                        guild.id,
                                                        role
        )
    try:
        cur = db.cursor()
        res = cur.execute(q)
        db.commit()
        db.close()
        return res
    except Exception as e:
        return e    

def insert_guild( guild, data=None, db_file="craig-bot.sqlite" ):
    """Insert a new guild (server) into the local DB"""
    try:
        db = _check_db( db_file )
        cur = db.cursor()
        if data is None:
            data = {
               "prof_filter":"False"
            }
        q = "INSERT INTO guilds VALUES(\"{}\",\"{}\",\"{}\",\"{}\")".format(guild.name,guild.id,data,now())
        res = cur.execute( q )
        db.commit()
        db.close()
        ret = cb_guild(int(guild.id),[int(guild.owner.id)],[],data)
        if not _check_admin( guild.owner, guild, db_file ):
            _insert_admin_user(guild.owner, guild, db_file=db_file)
        return ret
    except Exception as e:
        db.rollback()
        db.close()
        print(e)
        return None
        
def _update_db( query, db_file ):
    """Pass a query to the sqlite file specified. Not very safe."""
    try:
        db = _check_db( db_file )
        cur = db.cursor()
        res = cur.execute(query)
        db.commit()
        db.close()
        return res
    except Exception as e:
        db.rollback()
        db.close()
        return e

def strip_user_id( message_text ):
    """Strip the Discord user ID from messages before passing to OpenAI.
        discord.Message.content includes a username ex:
            <@123457890> This is my message!
        This function strips off the text between <> (inc.) and returns only the
        actual message data."""
    strip_user_regex=re.compile('\<[^)]*\>')
    if not type(message_text) is str:
        raise TypeError("Error when stripping Discord ID's. Expecting type str got: {}".format( type( message_text )))
    else:
        try:
            ret = message_text[strip_user_regex.match(message_text).end()+1:len(message_text)]
        except AttributeError as e:
            raise RuntimeError("User ID sub-string not found in message text! Reccomend setting message text manually.")
        return ret
    
def prompt_openai( in_text, user, openai_key, model="gpt-3.5-turbo", max_resp_len=200, db_file="craig-bot.sqlite" ):
    """Interact with OpenAI's API."""
    try: # if no id in message pass the raw message as input to chatgpt
        prompt = strip_user_id( in_text )
    except RuntimeError as e:
        prompt = in_text
    try:
        openai.api_key = openai_key
        data = [
            {"role": "assistant", "content": "limit the response to {} characters or less".format(max_resp_len)},
            {"role": "user", "content": "{}".format(prompt)}
        ]    
        response = openai.ChatCompletion.create(
        model = model,
        messages = data,
        max_tokens = 256,
        n = 1,
        stop = None,
        temperature = 0.5,
        )
        _log_ai_prompt( in_text, model, response, user.id, db_file, now() )
        return response
    except openai.error.InvalidRequestError as e:
        print(e)
        return None
  
# TODO implement this in the process for returning AI prompts
def _log_ai_prompt( in_text, model, reply, user, db_file="craig-bot.sqlite", date=now(), ):
    db_data = {
            "prompt":in_text,
            "model":model,
            "resp":reply,
            "uid":user,
            "date":date,
        }
    try:
        db = _check_db(db_file)
        cur = db.cursor()
        q = "INSERT INTO oai_cmds VALUES(\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(
            db_data["prompt"],
            db_data["model"],
            db_data["resp"],
            db_data['uid'],
            db_data["date"])
        res = cur.execute(q)
        db.commit()
        db.close()
        return res
    except Exception as e:
        db.rollback()
        db.close()
        return None
       
# always returns 1 if it catches an error
def get_selection( text ):
    try:
        v = int(text[0:1])
    except ValueError as e:
        v = 1
    return v
        
# slice off the prefix from a string
def slicer( text, pfx ):
    if len(pfx) > len(text):
        raise RuntimeError("pfx longer than string!")
    else:
        return text[len(pfx):len(text)]


def cb_roll(rollc, sides, db_file="craig-bot.sql"):
    """Rolls a b-sided die a times.
    Returns a tuple of (sides,result)"""
    random.seed()
    ret = []
    for i in range(1,rollc):
        ret.append((sides,random.randint(0,sides)))
    _insert_roll(ret, db_file)
    return ret

def cb_avg(rolls):
    """Wrapper for statistics.mean()"""
    data = [x[1] for x in rolls]
    return int(statistics.mean(data))


def _insert_roll(result_list, db_file="craig-bot.sql"):
    """Insert dice roll data into the database."""
    if not type(result_list) == list:
        raise TypeError("result_list is not a list!")
    try:
        db = _check_db(db_file)
    except Exception as e:
        print(e)
        return None
    q = "INSERT INTO rolls (num_sides,result) VALUES (?,?)"
    try:
        cur = db.cursor()
        ret = cur.executemany(q,result_list)
        db.commit()
        db.close()
    except Exception as e:
        ret = None
        db.rollback()
        db.close()
    return ret