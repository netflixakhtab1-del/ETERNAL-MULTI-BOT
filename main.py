# =========================================================
#  EternalMC Multi Bot - Main Entry File (V4 Demon Edition)
#  Created by GameTime_Studies ❤️ Demon (Ultimate Rewrite)
# =========================================================

import os
import json
import asyncio
import discord
from discord.ext import commands
from pathlib import Path

# -----------------------------
# 🔧 BOT CONFIG
# -----------------------------
BOT_TOKEN = (
    os.environ.get("token here")
    or "token here"
)

DEFAULT_PREFIX = "!"
MASTER_ID = 1206125304116940810
MASTER_CHANNEL = 1422883199071289386  # Your master control channel

# -----------------------------
# 🧱 Ensure Folder Structure
# -----------------------------
for folder in ["cogs", "utils", "data"]:
    Path(folder).mkdir(exist_ok=True)

# -----------------------------
# ⚙️ Discord Intents
# -----------------------------
intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True

# -----------------------------
# 🧩 Prefix System
# -----------------------------
from utils import db, embeds


async def get_prefix(bot, message):
    if not message.guild:
        return DEFAULT_PREFIX

    prefix = await db.get_prefix(message.guild.id)
    return prefix or DEFAULT_PREFIX


bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=None,
    owner_id=MASTER_ID,
)

# =========================================================
# 🌌 Welcome Panel When Bot is Invited
# =========================================================
async def send_bot_welcome_panel(guild):
    """Send welcome panel when bot is added to a server."""
    channel = guild.system_channel or next(
        (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
        None,
    )
    if not channel:
        return

    embed = discord.Embed(
        title="🌟 Thanks for Adding EternalMC MultiBot!",
        description=(
            "I am **EternalMC MultiBot V4 (Demon Edition)**\n"
            "Created by **GameTime_Studies** and **Demon**.\n\n"
            "✨ I support:\n"
            "• Moderation + Anti-Nuke\n"
            "• Entrance / Welcome Templates\n"
            "• Invite Tracker\n"
            "• Leveling\n"
            "• Emoji + Stickers + Sounds\n"
            "• Autoroles\n"
            "• Status Panel (IP/Website/Bot)\n"
            "• Backup System\n"
            "• Server Premium + BotPremium\n\n"
            "➡️ Use **/setup** to configure everything.\n"
            "➡️ Use **/help** to see all commands.\n"
        ),
        color=discord.Color.gold(),
    )
    embed.set_footer(text="EternalMC MultiBot • Demon Edition")

    await channel.send(embed=embed)


# =========================================================
# 🎨 Console Banner
# =========================================================
async def startup_banner():
    print("\033[95m" + """
╔═══════════════════════════════════════════════════════╗
║           🌌 EternalMC MultiBot V4 — DEMON ⚙️          ║
║      Created by GameTime_Studies ❤️ Demon Edition     ║
║ Donate: demonislamak@fam | Eternal Family Forever     ║
╚═══════════════════════════════════════════════════════╝
""" + "\033[0m")


# =========================================================
# 🧩 Cog Loader
# =========================================================
async def load_all_cogs():
    for cog in Path("cogs").glob("*.py"):
        path = cog.as_posix().replace("/", ".").replace(".py", "")
        try:
            await bot.load_extension(path)
            print(f"✅ Loaded Cog: {path}")
        except Exception as e:
            print(f"❌ Failed to load {path}: {e}")


# =========================================================
# 🌐 On Ready
# =========================================================
@bot.event
async def on_ready():
    await startup_banner()
    await db.initialize()

    print(f"✅ Logged in as: {bot.user} ({bot.user.id})")
    print(f"🌍 Connected to {len(bot.guilds)} servers")

    try:
        await bot.tree.sync()
        print("🔁 Slash commands synced globally.")
    except Exception as e:
        print(f"⚠️ Sync failed: {e}")


# =========================================================
# 👑 MASTER -IP Shortcut
# =========================================================
async def send_eternalmc_panel(channel, ip="play.eternalmcpe.fun"):
    embed = discord.Embed(
        title="🌌 EternalMC IP Panel",
        description=(
            f"✨ **IP:** `{ip}`\n"
            f"🛠 Bedrock Port: `19132`\n"
            f"🌍 Java & Bedrock Supported\n\n"
            f"Use this IP to join EternalMC!"
        ),
        color=discord.Color.gold(),
    )
    embed.set_footer(text="EternalMC • Demon Edition")
    await channel.send(embed=embed)


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Master quick command
    if message.channel.id == MASTER_CHANNEL and message.author.id == MASTER_ID:
        if message.content.startswith("-ip"):
            parts = message.content.split(maxsplit=1)
            ip = parts[1] if len(parts) > 1 else "play.eternalmcpe.fun"
            await send_eternalmc_panel(message.channel, ip)
            return

    await bot.process_commands(message)


# =========================================================
# ⚙️ /setprefix
# =========================================================
@bot.hybrid_command(name="setprefix", description="Change the bot prefix (Admin only).")
@commands.has_permissions(administrator=True)
async def setprefix(ctx, prefix: str):
    if len(prefix) > 5:
        return await ctx.send("❌ Prefix must be 5 characters or less.")

    await db.set_prefix(ctx.guild.id, prefix)

    embed = discord.Embed(
        title="✅ Prefix Updated",
        description=f"Prefix for **{ctx.guild.name}** is now `{prefix}`",
        color=discord.Color.gold(),
    )
    await ctx.send(embed=embed)


# =========================================================
# 🚀 RUN BOT
# =========================================================
async def main():
    async with bot:
        await load_all_cogs()
        await bot.start(BOT_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"🔥 CRITICAL ERROR: {e}")
