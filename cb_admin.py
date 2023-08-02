import discord, asyncio, config
from discord.ext import commands
from funcs import *

class cb_admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    def _check_auth(self,user,auth):
        """Check auth() for the user or any of their roles.
        auth should be a tuple of lists (admin_users,admin_groups)"""
        allow = False
        if user.id in auth[0]:
            return True
        for g in auth[1]:
            for r in user.roles:
                if g == r:
                    allow = True
                    break
            if allow == True:
                break
        return allow
    
    @commands.command()
    async def kick(self,ctx,user):
        # TODO validate no race conditions here like in yt()
        username = user.split()[0] # no funny business
        auth = config.guilds[ctx.guild.id].get_auth()
        # if not self._check_auth(user,auth):
        #     return None
        sent_msg = await ctx.send(username)
        return sent_msg
    
    @commands.command()
    async def talkback(self,ctx,*,message):
        # TODO validate no race conditions here like in yt()
        auth = config.guilds[ctx.guild.id].get_auth()
        if not self._check_auth(ctx.author,auth):
            return None
        sent_msg = await ctx.send(f"{ctx.author.mention} you said {message}")
        return sent_msg
