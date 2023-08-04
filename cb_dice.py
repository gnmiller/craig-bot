from discord.ext import commands
import statistics
import config
import random
import cb_sql


class cb_dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        return

    @commands.command(
            help="Roll x dice y times. To avoid spam the max number"
                 " of dice is 50 and the max number of sides is 100",
            brief="Roll some dice",
            usage="[x] [y]\nRoll x dice y times."
    )
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def roll(self, ctx, dice="1d20"):
        sent_msg = await ctx.send("```Rattling the dice tower, one moment please.```")
        try:
            num_d = dice.split('d')[0]
            num_s = dice.split('d')[1]
        except Exception:
            num_d = 1
            num_s = 20
        num_d = min(int(num_d), 50)
        num_s = ck_sides(num_s)
        rolls = cb_roll(int(num_d), int(num_s), config.db_file)
        cb_dice.insert_roll(ctx.guild, ctx.author, rolls, config.db_info)
        send_str = "```You rolled {} {} with {} sides.\nResults: {}"
        if num_d == 1:
            s = "die"
        else:
            s = "dice"
            send_str += "\nAverage: {}".format(cb_avg(rolls))
        send_str += "```"
        send_str = send_str.format(num_d, s, num_s, [x[1] for x in rolls])
        await sent_msg.edit(content=send_str)

    @commands.command()
    async def stats(self, ctx):
        raise NotImplementedError


def ck_sides(sides: int):
    dice = [2, 4, 6, 8, 10, 20, 100]
    if sides not in dice:
        return 20
    else:
        return sides


def cb_roll(rollc, sides, db_file="craig-bot.sql"):
    """Rolls a b-sided die a times.
    Returns a tuple of (sides,result)"""
    random.seed()
    ret = []
    for i in range(0, rollc):
        ret.append((sides, random.randint(1, sides)))
    return ret


def cb_avg(rolls):
    """Wrapper for statistics.mean()"""
    data = [x[1] for x in rolls]
    return int(statistics.mean(data))


def insert_roll(guild, user, rolls, db_info=config.db_info):
    if not isinstance(rolls, list):
        return
    try:
        db = cb_sql._connect_db(db_info)
    except Exception as e:
        raise e
    try:
        for roll in rolls:
            q = "INSERT INTO `dice_data`"\
                " (`guild_id`,`user_id`,`num_sides`,`result`)"\
                f" VALUES ({guild.id},{user.id},{roll[0]},{roll[1]})"
            cur = db.cursor()
            cur.execute(q)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    return rolls
