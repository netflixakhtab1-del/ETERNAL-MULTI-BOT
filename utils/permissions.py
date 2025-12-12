# =========================================================
#  EternalMC Multi Bot - Permissions System
#  Demon Edition V4
# =========================================================

import json
from pathlib import Path

MASTER_ID = 1206125304116940810
ACCESS_PATH = Path("data/access.json")

ACCESS_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load():
    if not ACCESS_PATH.exists():
        ACCESS_PATH.write_text(json.dumps({}, indent=4))
    return json.loads(ACCESS_PATH.read_text())


def _save(data):
    ACCESS_PATH.write_text(json.dumps(data, indent=4))


# -----------------------------------------
# CHECK MASTER
# -----------------------------------------
def is_master(user_id: int) -> bool:
    return user_id == MASTER_ID


# -----------------------------------------
# GET ACCESS LEVEL
# -----------------------------------------
def get_level(guild, member):
    if is_master(member.id):
        return 999

    data = _load()
    gid = str(guild.id)

    if gid not in data:
        return 0

    # User level
    user_lvl = data[gid].get("users", {}).get(str(member.id), 0)

    # Role level
    max_role_lvl = 0
    for r in member.roles:
        lvl = data[gid].get("roles", {}).get(str(r.id), 0)
        if lvl > max_role_lvl:
            max_role_lvl = lvl

    return max(user_lvl, max_role_lvl)


# -----------------------------------------
# CHECK REQUIRED LEVEL
# -----------------------------------------
def has_level(interaction, required: int):
    if is_master(interaction.user.id):
        return True

    return get_level(interaction.guild, interaction.user) >= required


# -----------------------------------------
# SETTERS
# -----------------------------------------
def set_user_level(guild_id, user_id, level):
    data = _load()
    gid = str(guild_id)

    if gid not in data:
        data[gid] = {"users": {}, "roles": {}}

    data[gid]["users"][str(user_id)] = level
    _save(data)


def remove_user_level(guild_id, user_id):
    data = _load()
    gid = str(guild_id)

    if gid in data and str(user_id) in data[gid]["users"]:
        del data[gid]["users"][str(user_id)]
        _save(data)


def set_role_level(guild_id, role_id, level):
    data = _load()
    gid = str(guild_id)

    if gid not in data:
        data[gid] = {"users": {}, "roles": {}}

    data[gid]["roles"][str(role_id)] = level
    _save(data)


def remove_role_level(guild_id, role_id):
    data = _load()
    gid = str(guild_id)

    if gid in data and str(role_id) in data[gid]["roles"]:
        del data[gid]["roles"][str(role_id)]
        _save(data)
