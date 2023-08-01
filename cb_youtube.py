import discord, asyncio, config
from discord.ext import commands
from funcs import *
import pdb

class CB_youtube(commands.Cog):
    def __init__(self,bot,api_key, guilds, search=None):
        self.bot = bot
        self.search = search
        self.api_key = api_key
    
    @commands.command(
        help = "Search for a YouTube video with the message as the search terms.",
        brief = "Search YouTube"
    )
    async def yt(self, ctx, *, message):
        cur_guild = config.guilds[ctx.guild.id]
        print("cur guild: {}".format(cur_guild.guild_id))
        print( "ctx guild: {}".format(ctx.guild.id))
        if ctx.author.id == config.bot_id:
            return # dont respond to self
        search_arr = cur_guild.search
        cur_search = None
        try: # check for existing searches
            cur_search = await cur_guild.get_search( ctx.author.id, cur_guild.guild_id, ctx.channel.id )
        except RuntimeError as e:
            cur_search = None
        if not cur_search is None:
            await ctx.send("```I think you have an existing search running. Try completing that first.```")
            return cur_search
        
        res = await self._yt_search( message, self.api_key )
        sent_msg = await ctx.send("```Performing YouTube Search please hold.```")
        try:
            await cur_guild.add_search( "youtube", 
                                ctx.author.id, 
                                cur_guild.guild_id,
                                ctx.channel.id, 
                                message, 
                                res, 
                                sent_msg, 
                                search_arr )
            send_str = "Search Terms: {}\n" \
                        "Search Results: \n".format(message)
            # build string of results
            index = 0
            for k,v in res.items():
                index+=1
                send_str+="{}. {} -- {}\n".format(index,v,k)
            await sent_msg.edit("```{}```".format(send_str))
            return cur_search  
        except RuntimeError as e:
            await sent_msg.edit("```Problem performing search.\n{}\n```".format(e))
            s = await cur_guild.del_search( ctx.guild.id, ctx.author.id, ctx.channel.id ) # passing IDs direct from msg here to avoid issues
            return s
        
    @commands.Cog.listener('on_message')
    async def check_selection( self, ctx ):
        if len(ctx.content) > 1:
            return None
        if ctx.user.id == config.bot_id:
            return # dont respond to self
        cur_guild = config.guilds[ctx.guild.id]
        try: # check for existing searches
            cur_search = await cur_guild.get_search( ctx.author.id, ctx.guild.id, ctx.channel.id )
        except RuntimeError as e:
            cur_search = None
        if cur_search is None:
            return None
        else:
            select = get_selection(ctx.content)
            send_str = await self._get_yt_id_from_search(cur_guild, cur_search, select) 
            sent = await cur_search.data['sent_msg'].edit(send_str)
            await cur_guild.del_search( ctx.guild.id, ctx.author.id, ctx.channel.id )
            return sent
        
    # return a dict of video_id:title for search results
    async def _yt_search( self, parms, yt_api_key ):
        try:
            yt = apiclient.discovery.build( 'youtube', 'v3', developerKey=yt_api_key )
            resp = yt.search().list( q=parms, part='id,snippet', maxResults=10 ).execute()
        except HTTPError as e:
            print( "Error connecting to YouTube API -- {}".format(e) )
            return e
        result = OrderedDict()
        for r in resp.get( 'items', [] ):
            if r['id']['kind'] == 'youtube#video':
                vid_id = r['id']['videoId']
                title = r['snippet']['title'].replace('&quot;','"')
                result[vid_id]=title
        return result

    async def _get_yt_id_from_search( self, guild, search, select ):
        i = 0
        for k,v in search.data['search_results'].items():
                i+=1
                if i == select:
                    await guild.del_search( search.get_uid(), 
                                           search.get_gid(), 
                                           search.get_channel() )
                    return yt_uri(k)