import config
import requests
from discord.ext import commands
import apiclient
import collections
from urllib.error import HTTPError
from funcs import yt_uri


class cb_youtube(commands.Cog, name="YouTube Search"):
    def __init__(self, bot, api_key):
        self.bot = bot,
        self.api_key = api_key

    @commands.command(
        help="Search for a YouTube video with the message as the search terms.",
        brief="Search YouTube"
    )
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def yt(self, ctx, *, message):
        if ctx.author.id == config.bot_id:
            return  # dont respond to self
        ret = None
        res = self._yt_search(message, self.api_key)
        sent_msg = await ctx.send("```Performing YouTube Search please hold.```")
        try:
            send_str = "Search Terms: {}\n" \
                        "Search Results: \n".format(message)
            # build string of results
            index = 0
            topres = ""
            for k, v in res.items():
                if index == 0:
                    topres = yt_uri(k)
                index += 1
                send_str += "{}. {} -- {}\n".format(index, v, k)
            send_str_more = "If you would like to select another"\
                            f" video check {config.pfx}help yt_id."
            await sent_msg.edit(f"{topres}\n```{send_str}\n{send_str_more}```")
        except RuntimeError as e:
            await sent_msg.edit(f"```Problem performing search.\n{e}\n```")
            return e
        return ret

    @commands.command(
            help="Attempts to embed the video ID provided (probably from !yt)"
                 " into a message.\n"
                 "Minimal validation is performed to ensure it's a video before"
                 " responding.",
            brief="Embed a video from a YouTube ID",
            usage="<video_id> The YouTube video ID to lookup."
    )
    async def yt_id(self, ctx, video_id):
        if not type(video_id) is str:
            raise TypeError("give me a string")
        req = requests.get("https://www.youtube.com/watch?v={}".format(video_id))
        if not req.status_code == "200":
            raise RuntimeError("give me a valid ID!")
        elif "This video isn't available anymore" in req.content.decode(req.encoding):
            raise RuntimeError("That does not look like a valid video ID.")
        await ctx.send(f"{ctx.author.mention}\n\nyt_uri(video_id)")

    # return a dict of video_id:title for search results
    def _yt_search(self, parms, yt_api_key):
        try:
            yt = apiclient.discovery.build('youtube', 'v3', developerKey=yt_api_key)
            resp = yt.search().list(q=parms, part='id,snippet', maxResults=5).execute()
        except HTTPError as e:
            print("Error connecting to YouTube API -- {}".format(e))
            return e
        result = collections.OrderedDict()
        for r in resp.get('items', []):
            if r['id']['kind'] == 'youtube#video':
                vid_id = r['id']['videoId']
                title = r['snippet']['title'].replace('&quot;', '"')
                result[vid_id] = title
        return result
