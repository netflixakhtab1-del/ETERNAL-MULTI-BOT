# =========================================================
#  EternalMC Multi Bot – Server Info (V4 Demon Edition)
#  Created by GameTime_Studies ❤️ Demon
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from utils import embeds, permissions
from datetime import datetime


# =========================================================
#  PAGINATION VIEW FOR ROLE / EMOTIONS
# =========================================================
class PageView(View):
    def __init__(self, embed_pages, user):
        super().__init__(timeout=60)
        self.pages = embed_pages
        self.user = user
        self.index = 0

    async def update(self, interaction):
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)

    @discord.ui.button(label="⬅ Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ This menu is not for you.", ephemeral=True)
        if self.index > 0:
            self.index -= 1
        await self.update(interaction)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ This menu is not for you.", ephemeral=True)
        if self.index < len(self.pages) - 1:
            self.index += 1
        await self.update(interaction)


# =========================================================
#  MAIN COG
# =========================================================
class ServerInfo(commands.Cog):
    """🌍 EternalMC ServerInfo with WOW UI"""

    def __init__(self, bot):
        self.bot = bot

    # =========================================================
    #  SERVER INFO COMMAND
    # =========================================================
    @app_commands.command(name="serverinfo", description="Show full server information in WOW UI.")
    async def serverinfo(self, interaction: discord.Interaction):

        guild = interaction.guild

        # Basic info
        owner = guild.owner
        humans = len([m for m in guild.members if not m.bot])
        bots = len([m for m in guild.members if m.bot])

        created = discord.utils.format_dt(guild.created_at, style="F")
        created_rel = discord.utils.format_dt(guild.created_at, style="R")

        banner = guild.banner.url if guild.banner else None
        splash = guild.splash.url if guild.splash else None

        # Boost info
        boost_count = guild.premium_subscription_count
        boost_tier = guild.premium_tier

        # Channels
        text_ch = len(guild.text_channels)
        voice_ch = len(guild.voice_channels)
        category_ch = len(guild.categories)
        stage_ch = len(guild.stage_channels)

        # Roles and Emojis (pagination)
        roles = guild.roles[::-1]  # highest first
        emojis = guild.emojis

        # Main Embed
        embed = discord.Embed(
            title=f"🌍 {guild.name}",
            description=f"✨ **Server Information Overview**",
            color=discord.Color.gold()
        )

        embed.add_field(
            name="👑 Owner",
            value=f"{owner.mention} | `{owner.id}`",
            inline=False
        )

        embed.add_field(
            name="📅 Created",
            value=f"{created}\n({created_rel})",
            inline=False
        )

        embed.add_field(
            name="👥 Members",
            value=f"**Total:** {guild.member_count}\n**Humans:** {humans}\n**Bots:** {bots}",
            inline=True
        )

        embed.add_field(
            name="📊 Channels",
            value=f"📝 Text: `{text_ch}`\n🔊 Voice: `{voice_ch}`\n📁 Categories: `{category_ch}`\n🎤 Stage: `{stage_ch}`",
            inline=True
        )

        embed.add_field(
            name="💎 Nitro",
            value=f"Boosts: `{boost_count}`\nLevel: `{boost_tier}`",
            inline=True
        )

        embed.add_field(
            name="🔒 Verification Level",
            value=str(guild.verification_level).title(),
            inline=True
        )

        embed.add_field(
            name="🆔 Server ID",
            value=f"`{guild.id}`",
            inline=True
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if banner:
            embed.set_image(url=banner)

        embed = embeds.apply_footer(embed, guild.id)

        # Pagination for roles and emojis
        role_pages = []
        chunk = ""

        # ROLES
        for i, r in enumerate(roles, start=1):
            chunk += f"{r.mention} (`{r.id}`)\n"
            if i % 15 == 0:
                role_pages.append(
                    discord.Embed(
                        title=f"🎭 Roles ({len(roles)})",
                        description=chunk,
                        color=discord.Color.gold()
                    )
                )
                chunk = ""
        if chunk:
            role_pages.append(
                discord.Embed(
                    title=f"🎭 Roles ({len(roles)})",
                    description=chunk,
                    color=discord.Color.gold()
                )
            )

        # EMOJIS
        emoji_pages = []
        chunk = ""

        for i, e in enumerate(emojis, start=1):
            fmt = f"<{'a' if e.animated else ''}:{e.name}:{e.id}>"
            chunk += f"{fmt} — `{e.name}`\n"
            if i % 15 == 0:
                emoji_pages.append(
                    discord.Embed(
                        title=f"😄 Emojis ({len(emojis)})",
                        description=chunk,
                        color=discord.Color.gold()
                    )
                )
                chunk = ""
        if chunk:
            emoji_pages.append(
                discord.Embed(
                    title=f"😄 Emojis ({len(emojis)})",
                    description=chunk,
                    color=discord.Color.gold()
                )
            )

        # Views
        role_view = PageView(role_pages, interaction.user)
        emoji_view = PageView(emoji_pages, interaction.user)

        # SEND MAIN INFO
        await interaction.response.send_message(embed=embed)

        # SEND PAGINATED ROLES
        await interaction.followup.send("🎭 **Role List:**", embed=role_pages[0], view=role_view)

        # SEND PAGINATED EMOJIS
        if emojis:
            await interaction.followup.send("😄 **Emoji List:**", embed=emoji_pages[0], view=emoji_view)
        else:
            await interaction.followup.send("😄 No emojis found.")

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
