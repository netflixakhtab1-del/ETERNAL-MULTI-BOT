# =========================================================
#  EternalMC Multi Bot - User Info (Ultimate Demon V4 UI)
#  Created by GameTime_Studies | Demon Edition
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import make_embed
from datetime import datetime


class UserInfo(commands.Cog):
    """👤 Demon Edition User Profile Viewer"""

    def __init__(self, bot):
        self.bot = bot

    # =========================================================
    # /userinfo — WOW Version
    # =========================================================
    @app_commands.command(
        name="userinfo",
        description="Show detailed information about a user (Demon Edition)."
    )
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):

        member = member or interaction.user
        user = member

        # Fetch banner (API call)
        try:
            user_api = await self.bot.fetch_user(user.id)
            banner_url = user_api.banner.url if user_api.banner else None
        except:
            banner_url = None

        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        roles_display = ", ".join(roles) if roles else "None"

        badges = []
        if user.bot:
            badges.append("🤖 Bot")
        if member.premium_since:
            badges.append("💎 Booster")
        if member.guild_permissions.administrator:
            badges.append("🛡️ Admin")
        if member.guild_permissions.manage_guild:
            badges.append("⚙️ Manager")

        badge_display = " ".join(badges) if badges else "—"

        embed = discord.Embed(
            title=f"👤 User Information — {user.name}",
            color=discord.Color.gold(),
            description=(
                f"✨ Viewing profile of **{user.mention}**\n"
                f"━━━━━━━━━━━━━━ 🟡 ━━━━━━━━━━━━━━\n"
                f"**Display Name:** `{member.display_name}`\n"
                f"**ID:** `{user.id}`\n"
                f"**Badges:** {badge_display}\n"
                f"━━━━━━━━━━━━━━ 🟡 ━━━━━━━━━━━━━━\n"
                f"**Account Created:** <t:{int(user.created_at.timestamp())}:R>\n"
                f"**Joined Server:** <t:{int(member.joined_at.timestamp())}:R>\n"
                f"━━━━━━━━━━━━━━ 🟡 ━━━━━━━━━━━━━━\n"
                f"**Top Role:** {member.top_role.mention}\n"
                f"**Roles ({len(roles)}):**\n{roles_display}\n"
            )
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        if banner_url:
            embed.set_image(url=banner_url)

        embed.set_footer(
            text=f"Requested by {interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(UserInfo(bot))
