import os, json


def get_settings(file):
    """Load file as a json and return it"""
    path = os.path.dirname(os.path.realpath(__file__))
    try:
        with open('{}/{}'.format(path, file)) as f:
            settings = json.load(f)
        f.close()
        return settings
    except FileNotFoundError:
        raise FileNotFoundError("Settings file not found."
                                f" Expecting: {os.getwd()}/settings.json")


settings = get_settings('settings.json')
pfx = settings['bot']['prefix']
discord_token = settings['discord']['token']
youtube_token = settings['youtube']['token']
openai_token = settings['openai']['token']
db_file = settings['bot']['db_file']
logfile = settings['bot']['logfile']
db_info = {
    "host": settings['bot']['db']['host'],
    "name": settings['bot']['db']['name'],
    "user": settings['bot']['db']['user'],
    "pw": settings['bot']['db']['password'],
    "port": settings['bot']['db']['port']
}

msg_owner_string = "Hello! A user has added this bot to a server that you own!\n"\
                         "Server Name: {guild_name}\n"\
                         "Server ID: {guild_id}\n"\
                         "The bot requires the server be a Discord community. "\
                         "This has a few side effects on your server!\n\n"\
                         "First verified e-mail is required to enable communities"\
                         "features.\n"\
                         "Second media content from all users will be scanned and"\
                         " purged if Discord believes it to be explicit (this"\
                         " excludes age-restricted channels)\n\n"\
                         "You may also want to enable several security"\
                         "features on your server to protect your users.\n"\
                         "These can be found under Server Settings -> Safety Setup\n\n"\
                         "Finally communities require rules and announcement channels\n"\
                         "The bot will automatically create these for you if you click "\
                         "confirm below.\n\n"\
                         "You may also respond to this DM with confirm rules announcement"\
                         "Where rules and announcement correspond to the names of those"\
                         "channels"

bee_emoji = "🐝"


class MissingValueError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
