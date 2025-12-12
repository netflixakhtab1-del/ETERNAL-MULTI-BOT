# =========================================================
#  EternalMC Multi Bot - AutoRole System
#  Demon Edition V4.0
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands
import json
from pathlib import Path

from utils.permissions import has_level, get_level
from utils.embeds import make_embed

AUTOROLE_PATH = Path("data/autorole.json")


# =========================================================
# Load / Save
# =========================================================
def load_autorole():
    if not AUTOROLE_PATH.exists():
        AUTOROLE_PATH.write_text(json.dumps({}, indent=4))
    return json.loads(AUTOROLE_PATH.read_text())


def save_autorole(data):
    AUTOROLE_PATH.write_text(json.dumps(data, indent=4))


# =========================================================
# AutoRole Cog
# =========================================================
class AutoRole(commands.Cog):
    """🎭 AutoRole System (Level 30+)"""

    def __init__(self, bot):
        self.bot = bot

    # Helper check
    async def need_level30(self, interaction):
        if not has_level(interaction, 30):
            lvl = get_level(interaction.guild, interaction.user)
            await interaction.response.send_message(
                f"❌ Access Denied\nYour Level: `{lvl}` • Required: `30`",
                ephemeral=True
            )
            return False
        return True

    # =========================================================
    # /autorole set
    # =========================================================
    @app_commands.command(
        name="autorole_set",
        description="Set the role given to new members. (Level 30+)"
    )
    async def autorole_set(self, interaction: discord.Interaction, role: discord.Role):

        if not await self.need_level30(interaction):
            return

        data = load_autorole()
        gid = str(interaction.guild.id)

        if gid not in data:
            data[gid] = {}

        data[gid]["member"] = role.id
        save_autorole(data)

        embed = make_embed(
            "AutoRole Updated",
            f"👤 **Member AutoRole:** {role.mention}",
            interaction.guild.id
        )
        await interaction.response.send_message(embed=embed)

    # =========================================================
    # /autorole botrole
    # =========================================================
    @app_commands.command(
        name="autorole_bot",
        description="Set the role given to bots. (Level 30+)"
    )
    async def autorole_bot(self, interaction: discord.Interaction, role: discord.Role):

        if not await self.need_level30(interaction):
            return

        data = load_autorole()
        gid = str(interaction.guild.id)

        if gid not in data:
            data[gid] = {}

        data[gid]["bot"] = role.id
        save_autorole(data)

        embed = make_embed(
            "AutoRole Updated",
            f"🤖 **Bot AutoRole:** {role.mention}",
            interaction.guild.id
        )
        await interaction.response.send_message(embed=embed)

    # =========================================================
    # /autorole muterole
    # =========================================================
    @app_commands.command(
        name="autorole_mute",
        description="Set the role used when muting members. (Level 30+)"
    )
    async def autorole_mute(self, interaction: discord.Interaction, role: discord.Role):

        if not await self.need_level30(interaction):
            return

        data = load_autorole()
        gid = str(interaction.guild.id)

        if gid not in data:
            data[gid] = {}

        data[gid]["mute"] = role.id
        save_autorole(data)

        embed = make_embed(
            "AutoRole Updated",
            f"🔇 **Mute Role:** {role.mention}",
            interaction.guild.id
        )
        await interaction.response.send_message(embed=embed)

    # =========================================================
    # /autorole boostrole (optional)
    # =========================================================
    @app_commands.command(
        name="autorole_boost",
        description="Set the role given to server boosters. (Level 30+)"
    )
    async def autorole_boost(self, interaction: discord.Interaction, role: discord.Role):

        if not await self.need_level30(interaction):
            return

        data = load_autorole()
        gid = str(interaction.guild.id)

        if gid not in data:
            data[gid] = {}

        data[gid]["boost"] = role.id
        save_autorole(data)

        embed = make_embed(
            "AutoRole Updated",
            f"💎 **Booster Role:** {role.mention}",
            interaction.guild.id
        )
        await interaction.response.send_message(embed=embed)

    # =========================================================
    # On Member Join → Apply AutoRoles
    # =========================================================
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        if member.bot:
            key = "bot"
        else:
            key = "member"

        data = load_autorole()
        gid = str(member.guild.id)

        if gid not in data:
            return

        role_id = data[gid].get(key)
        if not role_id:
            return

        role = member.guild.get_role(role_id)
        if not role:
            return

        try:
            await member.add_roles(role)
        except:
            pass

        # Booster role auto handled by Discord itself


# =========================================================
# Setup
# =========================================================
async def setup(bot):
    await bot.add_cog(AutoRole(bot))
