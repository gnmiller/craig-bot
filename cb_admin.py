import discord, asyncio, config
from discord.ext import commands
from funcs import *

class cb_admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    async def _check_auth(self,user,auth):
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
    async def kick(self,ctx,user,auth,reason="get punted!"):
        if not self._check_auth(user,auth):
            return None
        send_str = "<@\{{}}\}> has been removed from the server"\
                    " (kick) with reason {}".format(user.id,reason)
        sent_msg = await ctx.send(send_str)
        return sent_msg
    
    @commands.command()
    async def talkback(self,ctx,user,auth):
        if not self._check_auth(user,auth):
            return None
        send_str = ctx.content
        sent_msg = "<@\{{}}\}> you said {}".format(user.id,ctx.content)
        sent_msg = await ctx.send(send_str)
        return sent_msg
