# =========================================================
#  EternalMC Multi Bot - Emoji System (FIXED TYPE ANNOTATION)
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import make_embed
from utils.permissions import has_level, get_level


class EmojiCog(commands.Cog):
    """😎 Emoji / Sticker / Soundboard tools"""

    def __init__(self, bot):
        self.bot = bot

    # =========================================================
    # /emoji_format - Single emoji to <a:name:id>
    # =========================================================
    @app_commands.command(name="emoji_format", description="Convert an emoji to Nitro-bypass format.")
    async def emoji_format(self, interaction: discord.Interaction, emoji: str):

        try:
            # emoji must be parsed as custom emoji
            parsed = await commands.EmojiConverter().convert(interaction, emoji)
        except:
            return await interaction.response.send_message("❌ Invalid emoji.", ephemeral=True)

        fmt = f"<{'a' if parsed.animated else ''}:{parsed.name}:{parsed.id}>"

        embed = make_embed(
            title="✨ Emoji Format",
            description=f"**Input:** {emoji}\n**Output:** `{fmt}`",
            guild_id=interaction.guild.id
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================================================
    # /emoji_formatall - All emojis formatted with pagination
    # =========================================================
    @app_commands.command(name="emoji_formatall", description="Format ALL emojis in server with pagination.")
    async def emoji_formatall(self, interaction: discord.Interaction):

        emojis = interaction.guild.emojis

        if not emojis:
            return await interaction.response.send_message("⚠️ No emojis in this server.", ephemeral=True)

        pages = []
        chunk = 25  # Discord safe

        for i in range(0, len(emojis), chunk):
            part = emojis[i:i+chunk]
            text = "\n".join(
                f"`<{ 'a' if e.animated else ''}:{e.name}:{e.id }>`" for e in part
            )
            pages.append(text)

        current = 0

        embed = make_embed(
            title="📦 Emoji Format (Page 1)",
            description=pages[current],
            guild_id=interaction.guild.id
        )

        view = EmojiPageView(pages, current, interaction.guild.id)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class EmojiPageView(discord.ui.View):
    def __init__(self, pages, index, gid):
        super().__init__(timeout=300)
        self.pages = pages
        self.index = index
        self.guild_id = gid

    @discord.ui.button(label="⬅️ Back", style=discord.ButtonStyle.gray)
    async def back(self, interaction: discord.Interaction, button):
        if self.index == 0:
            return await interaction.response.defer()

        self.index -= 1
        embed = make_embed(
            title=f"📦 Emoji Format (Page {self.index+1})",
            description=self.pages[self.index],
            guild_id=self.guild_id
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="➡️ Next", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button):
        if self.index >= len(self.pages) - 1:
            return await interaction.response.defer()

        self.index += 1
        embed = make_embed(
            title=f"📦 Emoji Format (Page {self.index+1})",
            description=self.pages[self.index],
            guild_id=self.guild_id
        )
        await interaction.response.edit_message(embed=embed, view=self)


async def setup(bot):
    await bot.add_cog(EmojiCog(bot))
