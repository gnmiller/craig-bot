import discord
import logging
import config
import cb_youtube
import cb_ai
import cb_sql
import funcs  # bot
from discord.ext import commands

# init
intents = discord.Intents(messages=True, presences=True, guilds=True,
                          members=True, reactions=True, message_content=True)
# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=config.pfx, intents=intents)

# logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=config.logfile,
                              encoding='utf-8', mode='w')
f = '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
handler.setFormatter(logging.Formatter(f))
logger.addHandler(handler)


def invite_uri():
    """Returns a discord invite URI to add the bot to your server."""
    if config.settings is None:
        raise FileNotFoundError("settings not loaded!")
    else:
        client_id = config.settings['discord']['app_id']
        permissions = config.settings['bot']['perms']
        scope = "bot%20applications.commands"
        ret = "https://discord.com/api/oauth2/authorize?"\
              f"client_id={client_id}&" \
              f"permissions={permissions}&scope={scope}"
        return ret


@bot.event
async def on_ready():
    config.bot_id = bot.user.id
    for g in bot.guilds:
        await g.me.edit(nick="BeeStingBot2.0")
        cb_sql.insert_guild(g, config.db_info)
        cb_sql.set_user_auth(g, g.owner, bot.user,
                             role="owner", db_info=config.db_info)
        for role in g.roles:
            if role.name.lower() == "administrator":
                cb_sql.set_role_auth(g, role.id, config.bot_id)
    print(invite_uri())
    return


@bot.event
async def on_message(msg):
    pinged = False
    # @ mentions block
    if msg.author.id == config.bot_id:
        return  # dont respond to self
    try:
        for m in msg.mentions:
            if m.id == config.bot_id:
                pinged = True
            pinged = True
        if pinged is False:
            # on_message() blocks the bot.commands()
            # syntax unless we explicitly call this
            res = await bot.process_commands(msg)
            return res
        else:
            # assume we want to query openAI
            # prompt = msg.content
            # msg_to_edit = await msg.channel.send("```Please hold while I commune with SkyNet.```")
            # oai_resp = cb_ai.prompt_openai( in_text=prompt, user=msg.author,
            #                            openai_key=openai_token, db_file=db_file )
            # await msg_to_edit.edit("```"+str(oai_resp.choices[0].message.content+"```"))
            return
    except Exception as e:
        print(e)
        return e


@bot.event
async def on_guild_join(guild):
    try:
        cb_sql.insert_guild(guild)
    except Exception as e:
        raise e


@bot.event
async def on_guild_leave(guild):
    raise NotImplementedError


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Sorry {ctx.author.mention} that command is"
                       " on cooldown. No spamerino in the chaterino."
                       f" -- {error}.")
        return
    raise NotImplementedError


@bot.command(
        help="Roll x dice y times. To avoid spam the max number"
             " of dice is 50 and the max number of sides is 100",
        brief="Roll some dice",
        usage="!roll [x] [y]\nRoll x dice y times."
)
@commands.cooldown(3, 30, commands.BucketType.user)
async def roll(ctx, dice="1d20"):
    sent_msg = await ctx.send("```Rattling the dice tower, one moment please.```")
    try:
        num_d = dice.split('d')[0]
        num_s = dice.split('d')[1]
    except Exception:
        num_d = 1
        num_s = 20
    num_d = min(int(num_d), 50)
    num_s = min(int(num_s), 100)
    rolls = funcs.cb_roll(int(num_d), int(num_s), config.db_file)
    send_str = "```You rolled {} {} with {} sides.\nResults: {}"
    if num_d == 1:
        s = "die"
    else:
        s = "dice"
        send_str += "\nAverage: {}".format(funcs.cb_avg(rolls))
    send_str += "```"
    send_str = send_str.format(num_d, s, num_s, [x[1] for x in rolls])
    await sent_msg.edit(content=send_str)


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("goodbye")
    await ctx.bot.close()

bot.add_cog(cb_youtube.cb_youtube(bot, config.youtube_token))
bot.add_cog(cb_ai.cb_ai(bot, config.openai_token, config.db_file))
bot.run(config.discord_token)
