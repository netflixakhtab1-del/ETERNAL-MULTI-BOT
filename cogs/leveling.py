# =========================================================
#  EternalMC Multi Bot – Leveling System (V4 Demon Edition)
#  Created by GameTime_Studies ❤️ Demon
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands
from utils import embeds, permissions
from pathlib import Path
import json
import asyncio
import random
import time

LEVEL_PATH = Path("data/levels.json")


# =========================================================
#  LOAD / SAVE
# =========================================================
def load_data():
    if not LEVEL_PATH.exists():
        LEVEL_PATH.write_text(json.dumps({}, indent=4))
    return json.loads(LEVEL_PATH.read_text())


def save_data(data):
    LEVEL_PATH.write_text(json.dumps(data, indent=4))


# =========================================================
#  XP CALCULATOR
# =========================================================
def xp_needed(level: int):
    return 5 * (level ** 2) + 50 * level + 100


class Leveling(commands.Cog):
    """📈 EternalMC Leveling System"""

    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}  # anti spam cooldown

    # =========================================================
    #  LISTENER — GIVE XP
    # =========================================================
    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):

        if not msg.guild:
            return
        if msg.author.bot:
            return

        data = load_data()
        gid = str(msg.guild.id)
        uid = str(msg.author.id)

        # initialize guild entry
        if gid not in data:
            data[gid] = {
                "users": {},
                "blacklist_channels": [],
                "blacklist_roles": [],
                "boost_roles": {},
                "rewards": {},
                "level_message": "**GG {user(proper)}! You reached level {level}!**",
                "level_image": None
            }

        guild_data = data[gid]

        # blacklist channels
        if msg.channel.id in guild_data.get("blacklist_channels", []):
            return

        # blacklist roles
        for r in msg.author.roles:
            if r.id in guild_data.get("blacklist_roles", []):
                return

        # cooldown
        key = f"{gid}-{uid}"
        now = time.time()

        if key in self.cooldowns and now - self.cooldowns[key] < 10:
            return
        self.cooldowns[key] = now

        # give base xp
        xp_gain = random.randint(10, 25)

        # xp boost roles
        for role in msg.author.roles:
            boost = guild_data.get("boost_roles", {}).get(str(role.id))
            if boost:
                xp_gain *= boost

        # update user data
        if uid not in guild_data["users"]:
            guild_data["users"][uid] = {"xp": 0, "level": 0}

        guild_data["users"][uid]["xp"] += xp_gain

        # level up check
        current_level = guild_data["users"][uid]["level"]
        required = xp_needed(current_level)

        if guild_data["users"][uid]["xp"] >= required:
            guild_data["users"][uid]["level"] += 1
            new_lvl = guild_data["users"][uid]["level"]

            # announce level up
            await self.send_level_up(msg, msg.author, guild_data, new_lvl)

            # role reward check
            reward_role_id = guild_data["rewards"].get(str(new_lvl))
            if reward_role_id:
                role = msg.guild.get_role(reward_role_id)
                if role:
                    await msg.author.add_roles(role)

        save_data(data)

    # =========================================================
    #  SEND LEVEL UP MESSAGE
    # =========================================================
    async def send_level_up(self, msg, user, guild_data, level):

        raw = guild_data.get("level_message", "")
        img = guild_data.get("level_image", None)

        # placeholder replace
        text = (
            raw.replace("{user}", user.mention)
            .replace("{user(proper)}", user.name)
            .replace("{level}", str(level))
        )

        embed = discord.Embed(
            title="📈 Level Up!",
            description=text,
            color=discord.Color.gold()
        )

        if img:
            embed.set_image(url=img)

        embed.set_thumbnail(url=user.display_avatar.url)

        await msg.channel.send(embed=embed)

    # =========================================================
    #  COMMANDS
    # =========================================================

    # 1) Set Level-Up Message
    @app_commands.command(name="lvl_message", description="Set level up message.")
    async def lvl_message(self, interaction: discord.Interaction, message: str):

        if not permissions.has_level(interaction, 20):
            return await interaction.response.send_message("❌ Access Level 20 required.", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        if gid not in data:
            data[gid] = {}

        data[gid]["level_message"] = message
        save_data(data)

        await interaction.response.send_message("📨 Level-up message updated!", ephemeral=True)

    # 2) Set Level-Up Image
    @app_commands.command(name="lvl_image", description="Set level-up banner image.")
    async def lvl_image(self, interaction: discord.Interaction, image: discord.Attachment):

        if not permissions.has_level(interaction, 20):
            return await interaction.response.send_message("❌ Access Level 20 required.", ephemeral=True)

        if not image.content_type.startswith("image"):
            return await interaction.response.send_message("⚠️ File must be an image.", ephemeral=True)

        url = image.url

        data = load_data()
        gid = str(interaction.guild.id)

        data[gid]["level_image"] = url
        save_data(data)

        await interaction.response.send_message("🖼️ Level-up banner updated!", ephemeral=True)

    # 3) Add level reward
    @app_commands.command(name="lvl_reward", description="Add a role reward for a level.")
    async def lvl_reward(self, interaction: discord.Interaction, level: int, role: discord.Role):

        if not permissions.has_level(interaction, 30):
            return await interaction.response.send_message("❌ Access Level 30 required.", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        if gid not in data:
            data[gid] = {}

        if "rewards" not in data[gid]:
            data[gid]["rewards"] = {}

        data[gid]["rewards"][str(level)] = role.id
        save_data(data)

        await interaction.response.send_message(f"🎁 Reward set for level {level}: {role.mention}", ephemeral=True)

    # 4) XP Boost role
    @app_commands.command(name="lvl_boost", description="Add XP boost to a role.")
    async def lvl_boost(self, interaction: discord.Interaction, role: discord.Role, multiplier: float):

        if not permissions.has_level(interaction, 40):
            return await interaction.response.send_message("❌ Access Level 40 required.", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        if "boost_roles" not in data[gid]:
            data[gid]["boost_roles"] = {}

        data[gid]["boost_roles"][str(role.id)] = multiplier
        save_data(data)

        await interaction.response.send_message(
            f"⚡ Role {role.mention} now gives `{multiplier}x` XP!",
            ephemeral=True
        )

    # 5) Blacklist channel
    @app_commands.command(name="lvl_blacklist_channel", description="Blacklist a channel from XP.")
    async def lvl_blacklist_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):

        if not permissions.has_level(interaction, 20):
            return await interaction.response.send_message("❌ Access Level 20 required.", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        if "blacklist_channels" not in data[gid]:
            data[gid]["blacklist_channels"] = []

        data[gid]["blacklist_channels"].append(channel.id)
        save_data(data)

        await interaction.response.send_message(f"🚫 {channel.mention} blacklisted from XP.", ephemeral=True)

    # 6) Blacklist role
    @app_commands.command(name="lvl_blacklist_role", description="Blacklist a role from XP.")
    async def lvl_blacklist_role(self, interaction: discord.Interaction, role: discord.Role):

        if not permissions.has_level(interaction, 20):
            return await interaction.response.send_message("❌ Access Level 20 required.", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        if "blacklist_roles" not in data[gid]:
            data[gid]["blacklist_roles"] = []

        data[gid]["blacklist_roles"].append(role.id)
        save_data(data)

        await interaction.response.send_message(f"🚫 Role {role.mention} blacklisted from XP.", ephemeral=True)

    # 7) Leaderboard
    @app_commands.command(name="lvl_leaderboard", description="View top XP users.")
    async def lvl_leaderboard(self, interaction: discord.Interaction):

        data = load_data()
        gid = str(interaction.guild.id)
        users = data.get(gid, {}).get("users", {})

        if not users:
            return await interaction.response.send_message("ℹ️ No XP data yet.", ephemeral=True)

        lb = sorted(users.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]

        desc = ""
        for i, (uid, d) in enumerate(lb, start=1):
            user = interaction.guild.get_member(int(uid))
            if user:
                desc += f"**{i}. {user.name}** — Level `{d['level']}` | XP `{d['xp']}`\n"

        embed = await embeds.make_embed(
            title="🏆 Level Leaderboard",
            description=desc,
            guild=interaction.guild
        )

        await interaction.response.send_message(embed=embed)

    # 8) Reset XP
    @app_commands.command(name="lvl_reset", description="Reset all XP data in the server.")
    async def lvl_reset(self, interaction: discord.Interaction):

        if not permissions.has_level(interaction, 50):
            return await interaction.response.send_message("❌ Access Level 50 required.", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        data[gid]["users"] = {}
        save_data(data)

        await interaction.response.send_message("🧹 XP data wiped!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Leveling(bot))
