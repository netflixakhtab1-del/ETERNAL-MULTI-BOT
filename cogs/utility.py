# =========================================================
#  EternalMC Multi Bot - Utility Commands
#  Demon Edition V4 (Optimized + No Duplicate Conflicts)
# =========================================================

import discord
import time
import psutil
from discord.ext import commands
from discord import app_commands

from utils.embeds import make_embed
from utils.permissions import get_level

START_TIME = time.time()


class Utility(commands.Cog):
    """🛠️ EternalMC Demon Utility Tools"""

    def __init__(self, bot):
        self.bot = bot

    # =========================================================
    # 🏓 Ping
    # =========================================================
    @app_commands.command(name="ping", description="Check bot latency.")
    async def ping(self, interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)
        embed = make_embed(
            title="🏓 Pong!",
            description=f"**Latency:** `{latency_ms}ms`",
            guild=interaction.guild.id
        )
        await interaction.response.send_message(embed=embed)

    # =========================================================
    # ⏳ Uptime
    # =========================================================
    @app_commands.command(name="uptime", description="See how long the bot has been online.")
    async def uptime(self, interaction: discord.Interaction):

        seconds = int(time.time() - START_TIME)
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)

        text = f"**{days}d {hours}h {minutes}m {seconds}s**"

        embed = make_embed(
            title="⏳ Bot Uptime",
            description=f"Online for:\n{text}",
            guild=interaction.guild.id
        )
        await interaction.response.send_message(embed=embed)

    # =========================================================
    # ⚙️ About
    # =========================================================
    @app_commands.command(name="about", description="Bot information & system stats.")
    async def about(self, interaction: discord.Interaction):

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        embed = discord.Embed(
            title="⚙️ EternalMC Multi Bot — Demon Edition",
            description=(
                "A powerful & premium super-bot for EternalMC.\n"
                "Demon Edition focuses on stability, design, and control.\n\n"
                f"**Servers:** `{len(self.bot.guilds)}`\n"
                f"**CPU Usage:** `{cpu}%`\n"
                f"**RAM Usage:** `{ram}%`\n"
                "━━━━━━━━━━━━━━ 🟡 ━━━━━━━━━━━━━━"
            ),
            color=discord.Color.gold()
        )

        embed.set_footer(text="EternalMC Multi Bot • Demon Edition")
        await interaction.response.send_message(embed=embed)

    # =========================================================
    # 🖼️ Avatar (DETAILED VERSION)
    # =========================================================
    @app_commands.command(name="avatar", description="Shows a user's avatar (Full Demon UI).")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):

        user = user or interaction.user

        embed = make_embed(
            title=f"🖼️ Avatar — {user.name}",
            description=f"[Open Full Image]({user.display_avatar.url})",
            guild=interaction.guild.id
        )
        embed.set_image(url=user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    # =========================================================
    # 🎨 Banner
    # =========================================================
    @app_commands.command(name="banner", description="Shows a user's banner image.")
    async def banner(self, interaction: discord.Interaction, user: discord.Member = None):

        user = user or interaction.user

        # Force API fetch (Discord optimization)
        try:
            fetched = await interaction.client.fetch_user(user.id)
        except:
            fetched = user

        if not fetched.banner:
            return await interaction.response.send_message("⚠️ This user has no banner.", ephemeral=True)

        embed = make_embed(
            title=f"🎨 Banner — {user.name}",
            description=f"[Open Full Image]({fetched.banner.url})",
            guild=interaction.guild.id
        )
        embed.set_image(url=fetched.banner.url)

        await interaction.response.send_message(embed=embed)

    # =========================================================
    # 🏙️ Server Icon
    # =========================================================
    @app_commands.command(name="servericon", description="Shows this server’s icon.")
    async def servericon(self, interaction: discord.Interaction):

        if not interaction.guild.icon:
            return await interaction.response.send_message("⚠️ This server has no icon.", ephemeral=True)

        embed = make_embed(
            title=f"🏙️ Server Icon — {interaction.guild.name}",
            description=f"[Open Full Image]({interaction.guild.icon.url})",
            guild=interaction.guild.id
        )
        embed.set_image(url=interaction.guild.icon.url)

        await interaction.response.send_message(embed=embed)

    # =========================================================
    # 📘 Help Menu (Demon UI)
    # =========================================================
    @app_commands.command(name="help", description="Demon Edition help menu.")
    async def help(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🟡 EternalMC MultiBot — Help Menu",
            description=(
                "**Utility Commands**\n"
                "`/ping`, `/uptime`, `/about`, `/avatar`, `/banner`, `/servericon`\n"
                "\n**Emoji System**\n"
                "`/emoji_add`, `/emoji_import`, `/emoji_format`, `/emoji_formatall`, `/emoji_list`\n"
                "\n**Moderation**\n"
                "`/warn`, `/kick`, `/ban`, `/mute`, `/unmute`, `/purge`, `/massrole`, `/massban`\n"
                "\n**Autorole**\n"
                "`/autorole_set`, `/autorole_bot`, `/autorole_mute`, `/autorole_boost`\n"
                "\n**Fun**\n"
                "`/meme`, `/joke`, `/8ball`\n"
                "\n**Systems**\n"
                "Leveling, Invites, Entrance, Premium, Backup"
            ),
            color=discord.Color.gold()
        )

        embed.set_footer(text="EternalMC Multi Bot • Demon Edition")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))
