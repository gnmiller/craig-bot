import discord
class my_guild(discord.Guild):
        def __init__(self,id,name):
                self.id = id
                self.name = name

class my_user():
        def __init__(self,id,name,roles):
                self.id = id
                self.name = name
                self.roles = roles

class my_role():
        def __init__(self,id,name):
                self.id=id
                self.name=name
