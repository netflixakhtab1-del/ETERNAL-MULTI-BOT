# =========================================================
#  EternalMC Multi Bot - Master Control System (V4 Demon)
#  Created by GameTime_Studies ❤️ Demon
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands
from utils import permissions, db, embeds

MASTER_ID = 1206125304116940810


class MasterControl(commands.Cog):
    """👑 Master-Only Control Panel"""

    def __init__(self, bot):
        self.bot = bot

    # =========================================================
    # 🧠 HIDDEN MASTER HELP
    # =========================================================
    @app_commands.command(name="masterhelp", description="(Hidden) Master-only commands.")
    async def masterhelp(self, interaction: discord.Interaction):

        if interaction.user.id != MASTER_ID:
            return await interaction.response.send_message("❌ Only the Master can view this.", ephemeral=True)

        embed = await embeds.make_embed(
            title="👑 EternalMC Master Panel",
            description=(
                "These commands are **only visible to Demon (Master)**.\n\n"
                "**/premium** — Add/remove server premium\n"
                "**/botpremium** — Add/remove botpremium\n"
                "**/server** — Leave/Ban/Unban servers\n"
                "**/serverlist** — View all joined servers\n"
                "**/massban** — Dangerous master action\n"
                "**/massrole** — Manage roles globally\n"
                "**/giveaccess** — Grant access levels\n"
            ),
            guild=interaction.guild
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================================================
    # 🌟 PREMIUM MANAGEMENT
    # =========================================================
    @app_commands.command(name="premium", description="Grant or remove server premium (Master only).")
    async def premium(self, interaction: discord.Interaction, action: str, guild_id: str):

        if interaction.user.id != MASTER_ID:
            return await interaction.response.send_message("❌ Only Demon can use this.", ephemeral=True)

        guild_id = int(guild_id)

        if action.lower() == "add":
            await db.set_premium(guild_id, True)
            msg = f"✅ Premium ENABLED for guild **{guild_id}**"
        elif action.lower() == "remove":
            await db.set_premium(guild_id, False)
            msg = f"❌ Premium DISABLED for guild **{guild_id}**"
        else:
            msg = "⚠️ Invalid action. Use: add / remove"

        await interaction.response.send_message(msg, ephemeral=True)

    # =========================================================
    # 🌌 BOTPREMIUM MANAGEMENT
    # =========================================================
    @app_commands.command(name="botpremium", description="Enable custom bot profile for guild.")
    async def botpremium(self, interaction: discord.Interaction, action: str, guild_id: str):

        if interaction.user.id != MASTER_ID:
            return await interaction.response.send_message("❌ Master only.", ephemeral=True)

        guild_id = int(guild_id)

        if action.lower() == "add":
            await db.set_botpremium(guild_id, True)
            msg = f"🔥 BotPremium ENABLED for guild **{guild_id}**"
        elif action.lower() == "remove":
            await db.set_botpremium(guild_id, False)
            msg = f"❌ BotPremium DISABLED for guild **{guild_id}**"
        else:
            msg = "⚠️ Invalid action. Use add/remove."

        await interaction.response.send_message(msg, ephemeral=True)

    # =========================================================
    # 🌍 SERVER LIST
    # =========================================================
    @app_commands.command(name="serverlist", description="Master — View all connected guilds.")
    async def serverlist(self, interaction: discord.Interaction):

        if interaction.user.id != MASTER_ID:
            return await interaction.response.send_message("❌ You cannot use this.", ephemeral=True)

        desc = ""
        for g in self.bot.guilds:
            desc += f"**{g.name}** — `{g.id}` ({g.member_count} members)\n"

        embed = await embeds.make_embed(
            title="🌍 Connected Servers",
            description=desc or "No servers found.",
            guild=interaction.guild
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================================================
    # 🚪 SERVER LEAVE / BAN / UNBAN
    # =========================================================
    @app_commands.command(name="server", description="Master server control.")
    async def server(self, interaction: discord.Interaction, action: str, guild_id: str):

        if interaction.user.id != MASTER_ID:
            return await interaction.response.send_message("❌ Not allowed.", ephemeral=True)

        guild_id = int(guild_id)
        guild = self.bot.get_guild(guild_id)

        if not guild:
            return await interaction.response.send_message("⚠️ Bot is not in that guild.", ephemeral=True)

        if action.lower() == "leave":
            await guild.leave()
            msg = f"👋 Left guild **{guild.name}** ({guild.id})"
        else:
            msg = "❌ Only leave is supported for now."

        await interaction.response.send_message(msg, ephemeral=True)

    # =========================================================
    # 🎭 GIVE ACCESS LEVEL
    # =========================================================
    @app_commands.command(name="giveaccess", description="Give a user or role access level.")
    async def giveaccess(
        self,
        interaction: discord.Interaction,
        target: discord.Member | discord.Role,
        level: int
    ):

        if interaction.user != interaction.guild.owner:
            return await interaction.response.send_message("❌ Only the guild owner may use this.", ephemeral=True)

        if level >= 999:
            return await interaction.response.send_message("⚠️ Cannot assign Master level.", ephemeral=True)

        if isinstance(target, discord.Member):
            permissions.set_user_level(interaction.guild.id, target.id, level)
            msg = f"✅ Set **{target}** to level **{level}**"
        else:
            permissions.set_role_level(interaction.guild.id, target.id, level)
            msg = f"✅ Set role **{target.name}** to level **{level}**"

        await interaction.response.send_message(msg, ephemeral=True)


async def setup(bot):
    await bot.add_cog(MasterControl(bot))
