import funcs, openai, re
import discord
from discord.ext import commands
settings = funcs.get_settings( 'settings.json' )
pfx = settings['bot']['prefix']
discord_token = settings['discord']['token']
youtube_token = settings['youtube']['token']
openai_token = settings['openai']['token']
db_file = settings['bot']['db_file']
import config

intents = discord.Intents( messages = True, presences = True, guilds = True, 
                          members = True, reactions = True, message_content = True )
bot = commands.Bot(command_prefix=pfx,intents=intents,reconnect=False)

guild1 = {
        "id":1,
        "data":None,
        "name":"guild1"
}

guild1 = {
        "id":1,
        "data":None,
        "name":"guild2"
}
