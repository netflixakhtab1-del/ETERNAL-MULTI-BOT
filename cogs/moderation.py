# =========================================================
#  EternalMC Multi Bot - Moderation & Anti-Abuse System V4
#  Created by GameTime_Studies ❤️ Demon
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands
import re
import asyncio
import json
from utils import embeds, permissions
from pathlib import Path
from datetime import timedelta

PROTECT_PATH = Path("data/protection.json")


# =========================================================
#  DATA HELPERS
# =========================================================
def load_data():
    if not PROTECT_PATH.exists():
        PROTECT_PATH.write_text(json.dumps({}, indent=4))
    return json.loads(PROTECT_PATH.read_text())


def save_data(data):
    PROTECT_PATH.write_text(json.dumps(data, indent=4))


class Moderation(commands.Cog):
    """🛡️ EternalMC Moderation & Protection System"""

    def __init__(self, bot):
        self.bot = bot
        self.spam_cache = {}

    # =========================================================
    #  SETUP COMMANDS
    # =========================================================
    @app_commands.command(name="setlog", description="Set log channel for moderation actions.")
    async def setlog(self, interaction: discord.Interaction, channel: discord.TextChannel):

        if not permissions.has_level(interaction, 10):
            return await interaction.response.send_message("❌ You need Access Level 10.", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        if gid not in data:
            data[gid] = {}

        data[gid]["log"] = channel.id
        save_data(data)

        embed = await embeds.make_embed(
            title="📘 Log Channel Set",
            description=f"Log channel updated to {channel.mention}",
            guild=interaction.guild
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ---------------------------------------------------------
    @app_commands.command(name="setaction", description="Configure anti-link / anti-ip actions.")
    async def setaction(
        self,
        interaction: discord.Interaction,
        filter: str,
        action: str
    ):

        if not permissions.has_level(interaction, 20):
            return await interaction.response.send_message("❌ Access Level 20 required.", ephemeral=True)

        valid_filters = ["antilink", "antiip", "antispam"]
        valid_actions = ["delete", "warn", "timeout", "mute"]

        if filter not in valid_filters or action not in valid_actions:
            return await interaction.response.send_message("⚠️ Invalid filter or action.", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        if gid not in data:
            data[gid] = {}

        if "actions" not in data[gid]:
            data[gid]["actions"] = {}

        data[gid]["actions"][filter] = action
        save_data(data)

        embed = await embeds.make_embed(
            title="⚙️ Action Updated",
            description=f"**{filter}** will now **{action}** the user.",
            guild=interaction.guild
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ---------------------------------------------------------
    @app_commands.command(name="linkallow", description="Allow a role to send YouTube / https links.")
    async def linkallow(self, interaction: discord.Interaction, role: discord.Role):

        if not permissions.has_level(interaction, 30):
            return await interaction.response.send_message("❌ Access Level 30 required.", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        if gid not in data:
            data[gid] = {}

        if "allowed_roles" not in data[gid]:
            data[gid]["allowed_roles"] = []

        data[gid]["allowed_roles"].append(role.id)
        save_data(data)

        embed = await embeds.make_embed(
            title="🔗 Link Allow Updated",
            description=f"Role **{role.name}** can now send YouTube / https links.",
            guild=interaction.guild
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================================================
    #  LISTENERS (Anti-Link / Anti-IP / Anti-Spam)
    # =========================================================
    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):

        if not msg.guild:
            return
        if msg.author.bot:
            return

        data = load_data()
        gid = str(msg.guild.id)

        if gid not in data:
            return

        actions = data[gid].get("actions", {})
        allowed_roles = data[gid].get("allowed_roles", [])
        log_channel_id = data[gid].get("log")

        # ROLE ALLOW-CHECK
        for r in msg.author.roles:
            if r.id in allowed_roles:
                return

        # YT ALLOW-CHECK
        if (
            msg.content.startswith("https://youtube.com")
            or msg.content.startswith("https://youtu.be")
        ):
            perms = msg.author.guild_permissions
            if perms.administrator or perms.manage_messages or perms.manage_roles or perms.mention_everyone:
                return  # allowed

        # --- ANTI LINK ---
        link_pattern = re.compile(r"(https?://|discord\.gg|\.com|\.net|\.org)", re.IGNORECASE)
        if link_pattern.search(msg.content) and actions.get("antilink"):
            await self.apply_action(msg, msg.author, actions["antilink"], "Posted forbidden link")
            return

        # --- ANTI IP ---
        ip_pattern = re.compile(r"\b(\d{1,3}\.){3}\d{1,3}\b")
        if ip_pattern.search(msg.content) and actions.get("antiip"):
            await self.apply_action(msg, msg.author, actions["antiip"], "Posted blocked IP")
            return

        # --- ANTI SPAM ---
        key = f"{msg.guild.id}:{msg.author.id}"
        self.spam_cache[key] = self.spam_cache.get(key, 0) + 1

        await asyncio.sleep(3)
        self.spam_cache[key] -= 1

        if self.spam_cache[key] >= 6 and actions.get("antispam"):
            await self.apply_action(msg, msg.author, actions["antispam"], "Spamming messages")

    # =========================================================
    #  ACTION HANDLER
    # =========================================================
    async def apply_action(self, msg, user, action, reason):

        log_id = load_data().get(str(msg.guild.id), {}).get("log")
        log_channel = msg.guild.get_channel(log_id) if log_id else None

        # DELETE
        if action == "delete":
            try:
                await msg.delete()
            except:
                pass

        # WARN
        if action == "warn":
            try:
                await user.send(f"⚠️ **Warning in {msg.guild.name}**\nReason: {reason}")
            except:
                pass

        # TIMEOUT
        if action == "timeout":
            try:
                await user.timeout_for(timedelta(seconds=60), reason=reason)
            except:
                pass

        # MUTE
        if action == "mute":
            mute_role = discord.utils.get(msg.guild.roles, name="Muted")
            if not mute_role:
                mute_role = await msg.guild.create_role(name="Muted")
                for ch in msg.guild.channels:
                    await ch.set_permissions(mute_role, send_messages=False, speak=False)
            await user.add_roles(mute_role)

        # LOG EMBED
        if log_channel:
            embed = await embeds.make_embed(
                title="🛡️ Protection Triggered",
                description=(
                    f"👤 **User:** {user.mention}\n"
                    f"📌 **Reason:** {reason}\n"
                    f"⚙️ **Action:** `{action}`"
                ),
                guild=msg.guild
            )
            await log_channel.send(embed=embed)

    # =========================================================
    #  MODERATION BASICS
    # =========================================================
    @app_commands.command(name="warn", description="Warn a user.")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):

        if not permissions.has_level(interaction, 10):
            return await interaction.response.send_message("❌ Access Level 10 required.", ephemeral=True)

        try:
            await user.send(f"⚠️ You were warned in **{interaction.guild.name}**.\nReason: {reason}")
        except:
            pass

        embed = await embeds.make_embed(
            title="⚠️ User Warned",
            description=f"{user.mention} has been warned.\nReason: {reason}",
            guild=interaction.guild
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ---------------------------------------------------------
    @app_commands.command(name="kick", description="Kick a member.")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str):

        if not permissions.has_level(interaction, 20):
            return await interaction.response.send_message("❌ Access Level 20 required.", ephemeral=True)

        await member.kick(reason=reason)

        embed = await embeds.make_embed(
            title="👢 User Kicked",
            description=f"{member.mention} kicked.\nReason: {reason}",
            guild=interaction.guild
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ---------------------------------------------------------
    @app_commands.command(name="ban", description="Ban a member.")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str):

        if not permissions.has_level(interaction, 50):
            return await interaction.response.send_message("❌ Access Level 50 required.", ephemeral=True)

        await member.ban(reason=reason)

        embed = await embeds.make_embed(
            title="⛔ User Banned",
            description=f"{member.mention} banned.\nReason: {reason}",
            guild=interaction.guild
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
