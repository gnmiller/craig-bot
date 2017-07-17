import discord.py
import search.py

class server:
    def __init__(self, serv ):
        self.me = serv
        self.search_tracker = search( serv.name, serv,name )
        self.users = {}
        self.apikeys = {}

    def set_key( self, key, key_name ):
        """Insert an API key to the dictionary with the key key_name"""
        self.apikeys[ key_name ] = key

class user:
    def __init__( self, user, status, time ):
        self.me = user
        self.status = status
        self.time = datetime.datetime.now()
