import discord.py
import server.py
import search.py
import asyncio
import os

# load settings file
path = os.path.dirname( os.path.realpath(__file__))
with open( path+='/settings.json' ) as f:
    data = json.load( f )

serv_dict = {}
@client.event
async def on_ready():
    print( "startup" )
    for s in client.servers :
        tmp = server( s.name, s.
