import re
import ast
import random
import statistics
import cb_sql
from datetime import datetime


def now(): return datetime.today().strftime('%Y-%m-%d')
def dictify(string): return ast.literal_eval(string)
def yt_uri(string): return f"https://www.youtube.com/watch?v={string}"


def strip_user_id(msg):
    """Strip the Discord user ID from messages before passing to OpenAI.
        discord.Message.content includes a username ex:
            <@123457890> This is my message!
        This function strips off the text between <> (inc.) and returns only the
        actual message data."""
    strip_user_regex = re.compile('\<[^)]*\>')
    if not isinstance(msg, str):
        raise TypeError("Error when stripping Discord ID's."
                        f" Expecting type str got: {type(msg)}")
    else:
        try:
            ret = msg[strip_user_regex.match(msg).end()+1:len(msg)]
        except AttributeError:
            raise RuntimeError("User ID sub-string not found in message text!")
        return ret
