# =========================================================
#  EternalMC MultiBot - Entrance System (V4 Demon Edition)
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands
import json
from pathlib import Path
from utils import embeds, permissions

ENTRANCE_PATH = Path("data/entrance.json")


# =========================================================
#  HELPERS
# =========================================================
def load_data():
    if not ENTRANCE_PATH.exists():
        ENTRANCE_PATH.write_text(json.dumps({}, indent=4))
    return json.loads(ENTRANCE_PATH.read_text())


def save_data(data):
    ENTRANCE_PATH.write_text(json.dumps(data, indent=4))


def apply_placeholders(raw: str, user: discord.Member):
    """Replaces placeholders with user/server data."""
    if not raw:
        return raw

    guild = user.guild

    return (
        raw.replace("{user}", user.mention)
        .replace("{user(proper)}", user.name)
        .replace("{user(avatar)}", user.display_avatar.url)
        .replace("{server}", guild.name)
        .replace("{server(icon)}", guild.icon.url if guild.icon else "")
    )


async def build_dynamic_embed(template_data, member: discord.Member):
    """
    Converts JSON template into a real embed.
    Supports:
    - title
    - description
    - image
    - thumbnail
    - color
    - author
    """

    # Base embed
    embed = discord.Embed()

    # Title
    if "title" in template_data:
        embed.title = apply_placeholders(template_data["title"], member)

    # Description
    if "description" in template_data:
        embed.description = apply_placeholders(template_data["description"], member)

    # Color
    if "color" in template_data:
        embed.color = discord.Color(template_data.get("color", 16773376))
    else:
        embed.color = discord.Color.gold()

    # Thumbnail
    thumb = template_data.get("thumbnail", {})
    if thumb.get("url"):
        embed.set_thumbnail(url=thumb["url"])

    # Image
    img = template_data.get("image", {})
    if img.get("url"):
        embed.set_image(url=img["url"])

    # Author
    auth = template_data.get("author", {})
    if auth:
        name = apply_placeholders(auth.get("name", ""), member)
        icon = apply_placeholders(auth.get("icon_url", ""), member)
        embed.set_author(name=name, icon_url=icon)

    # Footer (returned based on premium)
    if not template_data.get("premium_footer_removed"):
        embed.set_footer(text="EternalMC Entrance System | GameTime_Studies")

    return embed


class EntranceCog(commands.Cog):
    """✨ Entrance System"""

    def __init__(self, bot):
        self.bot = bot

    # =========================================================
    #  SETUP JOIN / LEAVE / BAN-DM
    # =========================================================
    @app_commands.command(name="entrance_setup", description="Setup join/leave/ban-dm message.")
    async def entrance_setup(
        self,
        interaction: discord.Interaction,
        type: str,
        channel: discord.TextChannel = None
    ):

        if not permissions.has_level(interaction, 20):
            return await interaction.response.send_message("❌ Access Level 20 required.", ephemeral=True)

        if type not in ["join", "leave", "ban_dm"]:
            return await interaction.response.send_message("⚠️ Invalid type: join / leave / ban_dm", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        if gid not in data:
            data[gid] = {"templates": {}}

        if type != "ban_dm" and channel is None:
            return await interaction.response.send_message("⚠️ Channel is required for join/leave.", ephemeral=True)

        data[gid][type] = {
            "channel": channel.id if channel else None,
            "template": data[gid].get("templates", {}).get(f"{type}_default", None)
        }

        save_data(data)

        embed = await embeds.make_embed(
            title="✨ Entrance Updated",
            description=f"**{type}** system is now configured.",
            guild=interaction.guild
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================================================
    #  TEMPLATE SAVE
    # =========================================================
    @app_commands.command(name="entrance_save", description="Save a custom template.")
    async def entrance_save(
        self,
        interaction: discord.Interaction,
        name: str,
        template_json: str
    ):

        if not permissions.has_level(interaction, 20):
            return await interaction.response.send_message("❌ Access Level 20 required.", ephemeral=True)

        try:
            template = json.loads(template_json)
        except:
            return await interaction.response.send_message("❌ Invalid JSON.", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        if gid not in data:
            data[gid] = {"templates": {}}

        data[gid]["templates"][name] = template
        save_data(data)

        embed = await embeds.make_embed(
            title="📁 Template Saved",
            description=f"Template **{name}** saved successfully.",
            guild=interaction.guild
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================================================
    #  TEMPLATE LOAD
    # =========================================================
    @app_commands.command(name="entrance_load", description="Load a template for join/leave/ban-dm.")
    async def entrance_load(
        self,
        interaction: discord.Interaction,
        name: str,
        type: str
    ):

        if not permissions.has_level(interaction, 20):
            return await interaction.response.send_message("❌ Access Level 20 required.", ephemeral=True)

        data = load_data()
        gid = str(interaction.guild.id)

        template = data.get(gid, {}).get("templates", {}).get(name)

        if not template:
            return await interaction.response.send_message("❌ Template not found.", ephemeral=True)

        if type not in ["join", "leave", "ban_dm"]:
            return await interaction.response.send_message("⚠️ Type must be join / leave / ban_dm.", ephemeral=True)

        data[gid][type]["template"] = template
        save_data(data)

        embed = await embeds.make_embed(
            title="📥 Template Applied",
            description=f"Template **{name}** applied to **{type}**.",
            guild=interaction.guild
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================================================
    #  TEMPLATE LIST
    # =========================================================
    @app_commands.command(name="entrance_templates", description="List saved templates.")
    async def entrance_templates(self, interaction: discord.Interaction):

        data = load_data()
        gid = str(interaction.guild.id)
        templates = data.get(gid, {}).get("templates", {})

        if not templates:
            return await interaction.response.send_message("ℹ️ No templates saved yet.", ephemeral=True)

        desc = "\n".join([f"• `{name}`" for name in templates])

        embed = await embeds.make_embed(
            title="📚 Saved Templates",
            description=desc,
            guild=interaction.guild
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================================================
    #  TEST MESSAGE
    # =========================================================
    @app_commands.command(name="entrance_test", description="Test your entrance setup.")
    async def entrance_test(self, interaction: discord.Interaction, type: str):

        data = load_data()
        gid = str(interaction.guild.id)

        if type not in ["join", "leave", "ban_dm"]:
            return await interaction.response.send_message("⚠️ Invalid type.", ephemeral=True)

        config = data.get(gid, {}).get(type, {})
        template = config.get("template")

        if not template:
            return await interaction.response.send_message("❌ No template set.", ephemeral=True)

        embed = await build_dynamic_embed(template, interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================================================
    #  ACTUAL JOIN/LEAVE EVENTS
    # =========================================================
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        data = load_data()
        gid = str(member.guild.id)

        cfg = data.get(gid, {}).get("join")
        if not cfg:
            return

        channel = member.guild.get_channel(cfg.get("channel"))
        template = cfg.get("template")

        if not channel or not template:
            return

        embed = await build_dynamic_embed(template, member)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        data = load_data()
        gid = str(member.guild.id)

        cfg = data.get(gid, {}).get("leave")
        if not cfg:
            return

        channel = member.guild.get_channel(cfg.get("channel"))
        template = cfg.get("template")

        if not channel or not template:
            return

        embed = await build_dynamic_embed(template, member)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):

        data = load_data()
        gid = str(guild.id)

        cfg = data.get(gid, {}).get("ban_dm")
        if not cfg:
            return

        template = cfg.get("template")
        if not template:
            return

        try:
            embed = await build_dynamic_embed(template, member)
            await member.send(embed=embed)
        except:
            pass


async def setup(bot):
    await bot.add_cog(EntranceCog(bot))
