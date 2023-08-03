import config
from discord.ext import commands


class cb_admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kick(self, ctx, user):
        username = user.split()[0]  # no funny business
        sent_msg = await ctx.send(username)
        return sent_msg

    @commands.command()
    async def talkback(self, ctx, *, message):
        cur_guild = config.guilds[ctx.guild.id]
        auth = cur_guild.get_auth()
        if not self._check_auth(ctx.author, auth):
            return None
        sent_msg = await ctx.send(f"{ctx.author.mention} you said {message}")
        return sent_msg
