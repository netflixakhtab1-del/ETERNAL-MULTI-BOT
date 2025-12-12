# =========================================================
#  EternalMC Multi Bot – Role Info (V4 Demon Edition)
#  Created by GameTime_Studies ❤️ Demon
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from utils import embeds
from datetime import datetime


# =========================================================
#  PAGE VIEW (Members + Permissions)
# =========================================================
class RolePageView(View):
    def __init__(self, pages, user):
        super().__init__(timeout=60)
        self.pages = pages
        self.user = user
        self.index = 0

    async def update(self, interaction):
        embed = self.pages[self.index]
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⬅ Back", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ This is not your menu.", ephemeral=True)
        if self.index > 0:
            self.index -= 1
        await self.update(interaction)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ This is not your menu.", ephemeral=True)
        if self.index < len(self.pages) - 1:
            self.index += 1
        await self.update(interaction)



# =========================================================
#  MAIN COG
# =========================================================
class RoleInfo(commands.Cog):
    """🎭 Premium WOW Role Info"""

    def __init__(self, bot):
        self.bot = bot

    # =========================================================
    #  /roleinfo COMMAND
    # =========================================================
    @app_commands.command(name="roleinfo", description="Show detailed information about a role.")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):

        guild = interaction.guild

        created = discord.utils.format_dt(role.created_at, "F")
        created_rel = discord.utils.format_dt(role.created_at, "R")

        members_with_role = [m for m in guild.members if role in m.roles]

        # BASE EMBED
        embed = discord.Embed(
            title=f"🎭 Role Information — {role.name}",
            color=role.color if role.color.value != 0 else discord.Color.gold()
        )

        embed.add_field(name="🆔 Role ID", value=f"`{role.id}`", inline=True)
        embed.add_field(name="📌 Position", value=f"`{role.position}`", inline=True)
        embed.add_field(name="🔔 Mentionable", value="Yes" if role.mentionable else "No", inline=True)
        embed.add_field(name="🛠️ Managed", value="Yes" if role.managed else "No", inline=True)
        embed.add_field(name="📅 Created", value=f"{created}\n({created_rel})", inline=False)
        embed.add_field(name="👥 Members", value=f"`{len(members_with_role)}` users", inline=True)

        embed.add_field(
            name="🎨 Color",
            value=f"`{role.color}`" if role.color.value != 0 else "`None`",
            inline=True
        )

        embed.add_field(name="🔒 Hoisted", value="Yes" if role.hoist else "No", inline=True)

        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)

        embed = embeds.apply_footer(embed, guild.id)

        # SEND MAIN PANEL
        await interaction.response.send_message(embed=embed)

        # =========================================================
        #  PAGINATED MEMBER LIST
        # =========================================================
        if len(members_with_role) == 0:
            await interaction.followup.send("👥 No members have this role.")
        else:
            pages = []
            chunk = ""

            for i, m in enumerate(members_with_role, start=1):
                chunk += f"{m.mention} — `{m.id}`\n"

                if i % 15 == 0:
                    pages.append(discord.Embed(
                        title=f"🎭 Members with {role.name}",
                        description=chunk,
                        color=discord.Color.gold()
                    ))
                    chunk = ""

            if chunk:
                pages.append(discord.Embed(
                    title=f"🎭 Members with {role.name}",
                    description=chunk,
                    color=discord.Color.gold()
                ))

            view = RolePageView(pages, interaction.user)
            await interaction.followup.send(embed=pages[0], view=view)

        # =========================================================
        #  PERMISSIONS PANEL
        # =========================================================
        perms = [p.replace("_", " ").title() for p, v in role.permissions if v]

        if not perms:
            await interaction.followup.send("🔐 This role has **no permissions**.")
        else:
            pages = []
            chunk = ""

            for i, perm in enumerate(perms, start=1):
                chunk += f"• {perm}\n"

                if i % 15 == 0:
                    pages.append(discord.Embed(
                        title=f"🔐 Permissions — {role.name}",
                        description=chunk,
                        color=discord.Color.gold()
                    ))
                    chunk = ""

            if chunk:
                pages.append(discord.Embed(
                    title=f"🔐 Permissions — {role.name}",
                    description=chunk,
                    color=discord.Color.gold()
                ))

            view = RolePageView(pages, interaction.user)
            await interaction.followup.send(embed=pages[0], view=view)



async def setup(bot):
    await bot.add_cog(RoleInfo(bot))
