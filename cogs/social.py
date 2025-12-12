# =========================================================
#  EternalMC Multi Bot - Social Commands
#  Demon Edition (Cleaned + Non-Conflicting)
# =========================================================

import discord
import random
from discord.ext import commands
from utils.embeds import make_embed


class Social(commands.Cog):
    """🎉 Fun & Social Commands"""

    def __init__(self, bot):
        self.bot = bot

    # =========================================================
    # 🎱 8Ball
    # =========================================================
    @commands.hybrid_command(name="8ball", description="Ask the magic 8Ball a question.")
    async def _8ball(self, ctx, *, question: str):
        responses = [
            "Absolutely yes!", "Nope.", "Ask again later.", "Without a doubt.",
            "Possibly.", "You know the truth already.", "Definitely not.",
            "Most likely.", "Outlook good!", "Hmm… try again soon."
        ]
        choice = random.choice(responses)

        embed = make_embed(
            title="🎱 Magic 8Ball",
            description=f"**Question:** {question}\n**Answer:** {choice}",
            guild=ctx.guild.id
        )

        await ctx.reply(embed=embed)

    # =========================================================
    # 😂 Joke
    # =========================================================
    @commands.hybrid_command(name="joke", description="Get a random clean joke.")
    async def joke(self, ctx):
        jokes = [
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "Parallel lines have so much in common. It's a shame they'll never meet.",
            "Why don’t skeletons fight? They don’t have the guts.",
            "I told my computer I needed a break, and it said 'No problem — going to sleep.'",
            "Why do bees have sticky hair? Because they use honeycombs."
        ]

        embed = make_embed(
            title="😂 Random Joke",
            description=random.choice(jokes),
            guild=ctx.guild.id
        )
        await ctx.reply(embed=embed)

    # =========================================================
    # 💬 Say
    # =========================================================
    @commands.hybrid_command(name="say", description="Repeat your message in a styled embed.")
    async def say(self, ctx, *, message: str):
        embed = make_embed(
            title="💬 EternalMC Broadcast",
            description=message,
            guild=ctx.guild.id
        )
        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.send(embed=embed)

    # =========================================================
    # 👤 Simple User Info (Social Version) — Renamed
    # =========================================================
    @commands.hybrid_command(name="social_userinfo", description="Simple user information card.")
    async def social_userinfo(self, ctx, user: discord.User = None):

        user = user or ctx.author

        embed = make_embed(
            title=f"👤 User Info — {user}",
            description=f"**ID:** `{user.id}`\n**Created:** <t:{int(user.created_at.timestamp())}:R>",
            guild=ctx.guild.id
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        await ctx.reply(embed=embed)

    # =========================================================
    # 🖼️ Simple Avatar (Social Version) — Renamed
    # =========================================================
    @commands.hybrid_command(name="social_avatar", description="Show avatar (simple social version).")
    async def social_avatar(self, ctx, user: discord.User = None):

        user = user or ctx.author

        embed = make_embed(
            title=f"🖼️ Avatar — {user}",
            description=f"[Open Full Image]({user.display_avatar.url})",
            guild=ctx.guild.id
        )

        embed.set_image(url=user.display_avatar.url)

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Social(bot))
