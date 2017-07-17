import discord
import server
import search
import asyncio
import datetime
import os

# load settings file
path = os.path.dirname( os.path.realpath(__file__))
with open( path='/settings.json' ) as f:
    data = json.load( f )

serv_arr = []
@client.event
async def on_ready():
    print( "startup" )
    for s in client.servers :
        tmp = server( s )
        serv_arr.append( tmp )
    for s in serv_arr :
        for u in s.me.users :
            tmp = user( u.name, u.id, u.status, datetime.datetime.now() )
            s.users.append( tmp )
    for s in serv_arr :
        for u in s.users :
            print( u.name )
