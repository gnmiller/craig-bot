import discord, logging, config
import cb_youtube, cb_ai
import funcs # bot
from discord.ext import commands

# settings
settings = funcs.get_settings( 'settings.json' )
pfx = settings['bot']['prefix']
discord_token = settings['discord']['token']
youtube_token = settings['youtube']['token']
openai_token = settings['openai']['token']
db_file = settings['bot']['db_file']
logfile = settings['bot']['logfile']

# init
intents = discord.Intents( messages = True, presences = True, guilds = True, 
                          members = True, reactions = True, message_content = True )
#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=pfx,intents=intents)

# logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=logfile, encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# setup slash commands NYI
# tree = app_commands.CommandTree(client)

# generate a URI for inviting the bot to a server.
def invite_uri():
    if settings is None:
        raise FileNotFoundError("settings not loaded!")
    else:
        client_id = settings['discord']['app_id']
        permissions = settings['bot']['perms']
        scope = "bot%20applications.commands"
        ret = "https://discord.com/api/oauth2/authorize?client_id={}&permissions={}&scope={}".format(client_id,permissions,scope)
        return ret

@bot.event
async def on_ready():
    funcs.init_db( db_file )
    config.bot_id = bot.user.id
    for g in bot.guilds:
        await g.me.edit(nick="BeeStingBot2.0")
        t_guild = funcs.check_guild( g, db_file )
        if not t_guild:
            t_guild = funcs.insert_guild( g, data=None, db_file=db_file )
        config.guilds[t_guild.guild_id] = t_guild
    print(invite_uri())
    return

@bot.event
async def on_message( msg ):
    pinged = False
    # @ mentions block
    if msg.author.id == config.bot_id:
        return # dont respond to self
    try:
        for m in msg.mentions:
            if m.id == config.bot_id:
                pinged = True
            pinged = True
        if pinged == False:
            res = await bot.process_commands(msg) # on_message() blocks the bot.commands() syntax unless we explicitly call this
            return res
        else:
            # assume we want to query openAI
            prompt = msg.content
            msg_to_edit = await msg.channel.send("```Please hold while I commune with SkyNet.```")
            oai_resp = cb_ai.prompt_openai( in_text=prompt, user=msg.author,
                                        openai_key=openai_token, db_file=db_file )
            await msg_to_edit.edit("```"+str(oai_resp.choices[0].message.content+"```"))
            return
    except Exception as e:
        print(e)
        return e
    
@bot.event
async def on_guild_join( guild ):
    try:
        row = funcs.check_guild( guild, db_file )
        if row == None:
            ret = funcs.insert_guild( guild, db_file )
        else:
           ret = None
        return ret
    except FileNotFoundError as e:
        print(e)
        return None

async def getmsg( client, msg_id ):
    msg = await client.fetch_message(msg_id)
    return msg



@bot.command(
        help = "Roll x dice y times. To avoid spam the max number of dice is 50 and the max" \
             " number of sides is 100",
        brief = "Roll some dice",
        usage = "!roll [x] [y]\nRoll x dice y times."
)
async def roll(ctx, dice="1d20"):
    sent_msg = await ctx.send("```Rattling the dice tower, one moment please.```")
    try:
        num_d=dice.split('d')[0]
        num_s=dice.split('d')[1]
    except Exception as e:
        num_d=1
        num_s=20
    num_d = min(int(num_d),50)
    num_s = min(int(num_s),100)
    rolls = funcs.cb_roll(int(num_d),int(num_s), db_file)
    send_str = "```You rolled {} {} with {} sides.\nResults: {}"
    if num_d == 1:
        s = "die"
    else:
        s = "dice"
        send_str+="\nAverage: {}".format(funcs.cb_avg(rolls))
    send_str+="```"
    send_str = send_str.format(num_d,s,num_s,[x[1] for x in rolls])
    await sent_msg.edit(content=send_str)

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.bot.close()

bot.add_cog(cb_youtube.cb_youtube(bot, youtube_token))
bot.add_cog(cb_ai.cb_ai(bot, openai_token, db_file))
bot.run(discord_token)
