# =========================================================
#  EternalMC Multi Bot - Invite Tracker (V4 Demon Edition)
#  Clean Falcon-Style Tracking (No Falcon references)
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands
from utils import embeds, permissions
from pathlib import Path
import json

INVITE_PATH = Path("data/invites.json")


# ---------------------------------------------------------
# LOAD/SAVE HELPERS
# ---------------------------------------------------------
def load_data():
    if not INVITE_PATH.exists():
        INVITE_PATH.write_text(json.dumps({}, indent=4))
    return json.loads(INVITE_PATH.read_text())


def save_data(data):
    INVITE_PATH.write_text(json.dumps(data, indent=4))


class InviteTracker(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cached = {}  # guild_id : [invite objects]
        self.bot.loop.create_task(self.cache_all())

    # =========================================================
    #  CACHE ALL INVITES ON READY
    # =========================================================
    async def cache_all(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            try:
                self.cached[guild.id] = await guild.invites()
            except:
                self.cached[guild.id] = []

    # =========================================================
    #  TRACK JOIN
    # =========================================================
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        try:
            new_invites = await guild.invites()
        except:
            return

        old_invites = self.cached.get(guild.id, [])
        used = None

        for old in old_invites:
            match = discord.utils.get(new_invites, code=old.code)
            if match and match.uses > old.uses:
                used = match
                break

        self.cached[guild.id] = new_invites

        data = load_data()
        gid = str(guild.id)

        if gid not in data:
            data[gid] = {}

        uid = str(member.id)

        if uid not in data[gid]:
            data[gid][uid] = {"inviter": None, "fake": 0, "real": 0, "left": 0, "joins": 0}

        # Vanity check
        if guild.vanity_url_code:
            vanity_url = guild.vanity_url_code
            if used is None:
                inviter = "VANITY"
            else:
                inviter = used.inviter.id
        else:
            inviter = used.inviter.id if used else None

        # Track inviter
        if inviter:
            data[gid][uid]["inviter"] = inviter

            # Stats
            inv_id = str(inviter)
            if inv_id not in data[gid]:
                data[gid][inv_id] = {"inviter": None, "fake": 0, "real": 0, "left": 0, "joins": 0}

            data[gid][inv_id]["joins"] += 1

        save_data(data)

    # =========================================================
    #  TRACK LEAVE
    # =========================================================
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild

        data = load_data()
        gid = str(guild.id)
        uid = str(member.id)

        if gid not in data or uid not in data[gid]:
            return

        inviter = data[gid][uid].get("inviter")
        if inviter:
            inv_id = str(inviter)
            if inv_id in data[gid]:
                data[gid][inv_id]["left"] += 1

        save_data(data)

    # =========================================================
    #  /INVITES
    # =========================================================
    @app_commands.command(name="invites", description="View your invite stats.")
    async def invites(self, interaction: discord.Interaction, user: discord.Member = None):

        user = user or interaction.user
        guild = interaction.guild

        data = load_data()
        gid = str(guild.id)
        uid = str(user.id)

        stats = data.get(gid, {}).get(uid, None)

        if not stats:
            return await interaction.response.send_message(
                "ℹ️ No invite data found for this user.",
                ephemeral=True
            )

        real = stats.get("joins", 0)
        left = stats.get("left", 0)
        fake = stats.get("fake", 0)
        total = max(real - left, 0)

        inviter = stats.get("inviter")
        inviter_text = f"<@{inviter}>" if inviter else "Unknown"

        embed = await embeds.make_embed(
            title=f"📨 Invite Stats — {user.name}",
            description=(
                f"👤 **User:** {user.mention}\n"
                f"🔗 **Invited by:** {inviter_text}\n\n"
                f"✨ **Total Invites:** `{total}`\n"
                f"🟢 Real Joins: `{real}`\n"
                f"🔴 Left: `{left}`\n"
                f"⚪ Fake: `{fake}`\n"
            ),
            guild=guild
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.response.send_message(embed=embed, ephemeral=False)

    # =========================================================
    #  /INVITES LEADERBOARD
    # =========================================================
    @app_commands.command(name="invite_leaderboard", description="Top inviters of the server.")
    async def invite_leaderboard(self, interaction: discord.Interaction):

        guild = interaction.guild
        data = load_data()
        gid = str(guild.id)

        if gid not in data:
            return await interaction.response.send_message("ℹ️ No invite data yet.", ephemeral=True)

        lb = []

        for uid, stats in data[gid].items():
            real = stats.get("joins", 0)
            left = stats.get("left", 0)
            total = max(real - left, 0)
            lb.append((uid, total))

        lb = sorted(lb, key=lambda x: x[1], reverse=True)[:10]

        desc = ""
        for i, (uid, total) in enumerate(lb, start=1):
            user = guild.get_member(int(uid))
            if user:
                desc += f"**{i}. {user.mention} — `{total}` invites**\n"

        embed = await embeds.make_embed(
            title="🏆 Invite Leaderboard",
            description=desc or "No data.",
            guild=guild
        )

        await interaction.response.send_message(embed=embed)

    # =========================================================
    #  /INVITES RESET (Owner or Access Level 50)
    # =========================================================
    @app_commands.command(name="invite_reset", description="Reset all invite data.")
    async def invite_reset(self, interaction: discord.Interaction):

        if not permissions.has_level(interaction, 50):
            return await interaction.response.send_message("❌ Access Level 50 required.", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        if gid in data:
            data[gid] = {}
            save_data(data)

        embed = await embeds.make_embed(
            title="🧹 Invites Reset",
            description="All invite data has been cleared.",
            guild=interaction.guild
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(InviteTracker(bot))
