# =========================================================
#  EternalMC Multi Bot - Status Panel Storage
#  Demon Edition V4
# =========================================================

import json
from pathlib import Path

IP_FILE = Path("data/ip_status.json")
IP_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load():
    if not IP_FILE.exists():
        IP_FILE.write_text(json.dumps({}, indent=4))
    return json.loads(IP_FILE.read_text())


def _save(data):
    IP_FILE.write_text(json.dumps(data, indent=4))


def set_ip(guild_id, ip):
    data = _load()
    gid = str(guild_id)

    if gid not in data:
        data[gid] = {}

    data[gid]["ip"] = ip
    _save(data)


def set_website(guild_id, website):
    data = _load()
    gid = str(guild_id)

    if gid not in data:
        data[gid] = {}

    data[gid]["website"] = website
    _save(data)


def set_botlink(guild_id, link):
    data = _load()
    gid = str(guild_id)

    if gid not in data:
        data[gid] = {}

    data[gid]["botlink"] = link
    _save(data)


def get_status(guild_id):
    data = _load()
    return data.get(str(guild_id), {})
