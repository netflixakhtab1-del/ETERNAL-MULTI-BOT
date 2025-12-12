# =========================================================
#  EternalMC Multi Bot - Embed Builder (WOW UI)
#  Demon Edition V4
# =========================================================

import discord
from . import db

PREMIUM_FOOTER = "🧠 EternalMC MultiBot • Created by GameTime_Studies & Demon"


async def make_embed(title="", description="", guild=None, color=discord.Color.gold()):
    """
    Creates a premium-style embed.
    Removes footer for premium servers.
    """

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
    )

    if guild:
        is_premium = await db.is_premium(guild.id)

        if not is_premium:
            embed.set_footer(text=PREMIUM_FOOTER)

    return embed
