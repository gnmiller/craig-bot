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


class MissingValueError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors
