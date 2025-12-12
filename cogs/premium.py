# =========================================================
#  EternalMC Multi Bot - Permissions Core
#  Demon Edition V4.0 (FIXED)
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


# =========================================================
#  BASIC CHECKS
# =========================================================

def is_master(interaction):
    """Check if user is bot master."""
    return interaction.user.id == MASTER_ID


def has_master(interaction):
    """Alias for import compatibility."""
    return is_master(interaction)


def get_level(guild, user):
    """Return combined (user + role) access level."""
    data = _load()
    gid = str(guild.id)

    if gid not in data:
        return 0

    # direct user access
    user_lvl = data[gid].get("users", {}).get(str(user.id), 0)

    # role access
    role_lvl = 0
    for role in user.roles:
        lvl = data[gid].get("roles", {}).get(str(role.id), 0)
        if lvl > role_lvl:
            role_lvl = lvl

    return max(user_lvl, role_lvl)


def has_level(interaction, required_level):
    """Check if user has required access or master."""
    if is_master(interaction):
        return True

    lvl = get_level(interaction.guild, interaction.user)
    return lvl >= required_level


# =========================================================
#  SET ACCESS
# =========================================================

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
