import mysql.connector
import discord
import funcs
import test_classes
import config


def _connect_db(db_info=config.db_info):
    con = None
    try:
        con = mysql.connector.connect(user=db_info['user'],
                                      password=db_info['pw'],
                                      host=db_info['host'],
                                      database=db_info['name'],
                                      port=db_info['port'])
    except Exception as e:
        if con is not None:
            con.close()
        raise e
    return con


def _check_guild(guild, db_info=config.db_info):
    if not isinstance(guild, discord.guild.Guild):
        raise TypeError(f"got: {type(guild)} expected Guild")
    try:
        db = _connect_db(db_info)
    except Exception as e:
        raise e
    ret = None
    try:
        cur = db.cursor()
        q = "SELECT `guild_id`,`guild_name` "\
            f"from guilds WHERE `guild_id`={guild.id}"
        cur.execute(q)
        res = cur.fetchall()
        ret = (res[0][0], res[0][1])  # (guild_id, guild_name)
    except IndexError:
        return None
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    return ret


def insert_guild(guild, db_info=config.db_info):
    if not isinstance(guild, discord.guild.Guild):
        raise TypeError(f"insert_guild() got: {type(guild)} expected Guild")
    try:
        db = _connect_db(db_info)
    except Exception as e:
        raise e
    try:
        guild_info = _check_guild(guild, db_info)
        if guild_info is not None:
            return guild_info
        cur = db.cursor()
        q = "INSERT INTO `guilds` (`guild_id`,`guild_name`,`added`) VALUES (%s,%s,%s)"
        # TODO insert help and announce chans
        cur.execute(q, (guild.id, guild.name, funcs.now()))
        db.commit()
        return _check_guild(guild, db_info)
    except mysql.connector.errors.IntegrityError:
        db.rollback()
        return None
    finally:
        db.close()


def drop_guild(guild, db_info=config.db_info):
    if not isinstance(guild, discord.guild.Guild):
        raise TypeError(f"check_guild() got: {type(guild)} expected Guild")
    try:
        db = _connect_db(db_info)
    except Exception as e:
        raise e
    try:
        cur = db.cursor()
        check = _check_guild(guild, db_info)
        if check is None:
            raise RuntimeError(f"guild not in database id: {guild.id}")
        queries = []
        queries.append(f"DELETE FROM `guilds` WHERE `guild_id`=\"{guild.id}\"")
        queries.append(f"DELETE FROM `opts` WHERE `guild_id`=\"{guild.id}\"")
        for q in queries:
            cur.execute(q)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def get_opt(guild, opt, db_info=config.db_info):
    """Returns a tuple of guild_id,opt_name,opt_val"""
    if not isinstance(guild, discord.guild.Guild):
        raise TypeError(f"get_opt() got: {type(guild)} expected Guild".format)
    try:
        db = _connect_db(db_info)
    except Exception as e:
        raise e
    try:  # guild_id,opt_name is a unique key so we only care about 1 row here
        cur = db.cursor()
        q = "SELECT `guild_id`,`opt_name`,`opt_val` "\
            f"FROM opts WHERE `guild_id`=\"{guild.id}\""\
            f"and `opt_name`=\"{opt}\""
        cur.execute(q)
        res = cur.fetchall()
        return res[0]
    except mysql.connector.errors.InterfaceError:
        return None
    except IndexError:
        return None
    except Exception as e:
        raise e
    finally:
        db.close()


def set_opt(guild, opt, val, user, db_info=config.db_info):
    if not isinstance(guild, discord.guild.Guild):
        raise TypeError(f"set_opt() got: {type(guild)} expected Guild")
    cur_val = get_opt(guild, opt, db_info)
    try:
        db = _connect_db(db_info)
    except Exception as e:
        raise e
    try:
        cur = db.cursor()
        if cur_val is None:
            q = "INSERT INTO `opts` (`guild_id`,`opt_name`,`opt_val`,`set_by`) VALUES (%s,%s,%s,%s)"
            cur.execute(q, (guild.id, opt, val, user.id))
        else:
            q = f"UPDATE `opts` SET `opt`.`opt_val`='{val}' WHERE `opt_name`='{opt}' AND `guild_id`=\"{guild.id}\""
            cur.execute(q)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_auth(guild, user, db_info=config.db_info):
    if not isinstance(guild, discord.guild.Guild):
        raise TypeError(f"get_auth() got: {type(guild)} expected Guild")
    if not isinstance(user, discord.user.ClientUser) \
        and not isinstance(user, discord.member.Member)\
            and not isinstance(user, test_classes.my_user):
        raise TypeError(f"get_auth() got: {type(user)} expected User")
    perms = None
    try:
        user_perms = _get_user_auth(guild, user, db_info)
        role_perms = []
        for role in user.roles:
            db_role_data = _get_role_auth(guild, role, db_info)
            if db_role_data is None:
                continue
            role_perms.append(db_role_data)
        perms = (user_perms, role_perms)
    except Exception as e:
        raise e
    return perms


def _get_user_auth(guild, user, db_info=config.db_info):
    if not isinstance(guild, discord.guild.Guild):
        raise TypeError(f"get_user_auth() got: {type(guild)} expected Guild")
    if not isinstance(user, discord.user.ClientUser) \
            and not isinstance(user, discord.member.Member) \
            and not isinstance(user, test_classes.my_user):
        raise TypeError(f"get_user_auth() got: {type(user)} expected User")
    try:
        db = _connect_db(db_info)
    except Exception as e:
        raise e
    try:  # user_id,guild_id is a unique key so we only care about 1 row here
        cur = db.cursor()
        q = "SELECT `guild_id`,`user_id`,`added_by`,`role` FROM `auth_user` "\
            f"WHERE `user_id`=\"{user.id}\" AND `guild_id`=\"{guild.id}\""
        cur.execute(q)
        res = cur.fetchall()
        return res[0]
    except IndexError:
        return None


def del_user_auth(guild, user, db_info=config.db_info):
    if not isinstance(guild, discord.guild.Guild):
        raise TypeError(f"del_user_auth() got: {type(guild)} expected Guild")
    if not isinstance(user, discord.user.ClientUser) \
            and not isinstance(user, discord.member.Member) \
            and not isinstance(user, test_classes.my_user):
        raise TypeError(f"del_user_auth() got: {type(user)} expected User")
    try:
        db = _connect_db(db_info)
    except Exception as e:
        raise e
    perms = None
    try:
        perms = _get_user_auth(guild, user, db_info)
        if perms is not None:
            cur = db.cursor()
            q = "DELETE FROM `auth_user` WHERE `guild_id`='%s' AND `user_id`='%s'"
            cur.execute(q, (guild.id, user.id))
            db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    return perms


def set_user_auth(guild, user, added_by,
                  role="administrator", db_info=config.db_info):
    if not isinstance(guild, discord.guild.Guild):
        raise TypeError(f"set_user_auth() got: {type(guild)} expected Guild")
    if not isinstance(user, discord.user.ClientUser) \
            and not isinstance(user, discord.member.Member):
        raise TypeError(f"set_user_auth() got: {type(user)} expected User")
    if not isinstance(user, discord.user.ClientUser) \
            and not isinstance(user, discord.member.Member):
        raise TypeError(f"set_user_auth() got: {type(added_by)} expected User")
    ret = None
    try:
        db = _connect_db(db_info)
    except Exception as e:
        raise e
    try:
        cur = db.cursor()
        perms = _get_user_auth(guild, user, db_info)
        if perms is None:
            q = "INSERT INTO auth_user (`guild_id`,`user_id`,`added_by`,`role`) VALUES (%s,%s,%s,%s)"
            cur.execute(q, (guild.id, user.id, added_by.id, role))
            db.commit()
        else:
            return perms
        # ensure it was inserted
        q = "SELECT `guild_id`,`user_id`,`added_by`,`role`,`added_by` "\
            "FROM auth_user WHERE `guild_id`='%s' AND `user_id`='%s'"
        cur.execute(q, (guild.id, user.id))
        res = cur.fetchall()
        ret = res[0]
    except IndexError:
        db.rollback()
        raise IndexError(f"results array was: {res}")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    return ret


def _get_role_auth(guild, role, db_info=config.db_info):
    if not isinstance(guild, discord.guild.Guild):
        raise TypeError("_get_role_auth() got: {type(guild)} expected Guild")
    if not isinstance(role, discord.role.Role):
        raise TypeError(f"_get_role_auth() got: {type(role)} expected str")
    try:
        db = _connect_db(db_info)
    except Exception as e:
        raise e
    try:  # user_id,guild_id is a unique key so we only care about 1 row here
        cur = db.cursor()
        q = "SELECT `guild_id`,`user_id`,`role`,`added_by` FROM `auth_user` "\
            f"WHERE `user_id`=\"{role.id}\" AND `guild_id`=\"{guild.id}\""
        cur.execute(q)
        res = cur.fetchall()
        return res[0]
    except IndexError:
        return None


def set_role_auth(guild, role, added_by, db_info=config.db_info):
    if not isinstance(guild, discord.guild.Guild):
        raise TypeError(f"set_role_auth() got: {type(guild)} expected Guild")
    if not isinstance(role, discord.role.Role):
        raise TypeError(f"set_role_auth() got: {type(role)} expected str")
    if not type(added_by) is discord.user.ClientUser \
            and not type(added_by) is discord.member.Member:
        raise TypeError(f"set_role_auth() got: {type(added_by)} expected User")
    ret = None
    try:
        db = _connect_db(db_info)
    except Exception as e:
        raise e
    try:
        cur = db.cursor()
        perms = _get_role_auth(guild, role, db_info)
        if perms is not None:
            return perms
        else:
            q = "INSERT INTO auth_role (`guild_id`,`role`,`added_by`) VALUES (%s,%s,%s)"
            cur.execute(q, (guild.id, role.id, added_by.id))
            db.commit()
        # ensure it was inserted
        q = "SELECT `guild_id`,`user_id`,`added_by`,`role`,`added_by` "\
            "FROM auth_user WHERE `guild_id`='%s' AND `role`='%s'"
        cur.execute(q, (guild.id, role.id))
        res = cur.fetchall()
        ret = res[0]
    except IndexError:
        db.rollback()
        raise IndexError(f"results array was: {res}")
    except Exception:
        db.rollback()
        return None
    finally:
        db.close()
    return ret


def del_role_auth(guild, role, db_info=config.db_info):
    if not isinstance(guild, discord.guild.Guild):
        raise TypeError("check_guild() got: {type(guild)} expected Guild")
    if not isinstance(role, discord.Role):
        raise TypeError(f"check_guild() got: {type(role)} Role")
    try:
        db = _connect_db(db_info)
    except Exception as e:
        raise e
    perms = None
    try:
        perms = _get_role_auth(guild, role, db_info)
        if perms is not None:
            cur = db.cursor()
            q = "DELETE FROM `auth_user` WHERE `guild_id`='%s' AND `user_id`='%s'"
            cur.execute(q, (guild.id, role.id))
            db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    return perms
