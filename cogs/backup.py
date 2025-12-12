# =========================================================
#  EternalMC Multi Bot - Backup & Template Manager
#  Demon Edition V4 (Stabilized + Optimized)
# =========================================================

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from pathlib import Path

from utils.embeds import make_embed
from utils.permissions import has_master, has_level, get_level

BACKUP_DIR = Path("data/backups")
DATA_DIR = Path("data")

# Ensure folder exists
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# Helper Functions
# =========================================================
def read_json(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except:
        return {}


def write_json(path, data):
    path.write_text(json.dumps(data, indent=4))


def collect_data():
    """
    Collect all bot config files inside /data and return as a template.
    Each JSON file is included.
    """
    data = {}

    for file in DATA_DIR.glob("*.json"):
        try:
            data[file.stem] = json.loads(file.read_text())
        except:
            data[file.stem] = {}

    return data


def apply_template(template: dict):
    """
    Replace contents of JSON config files with data from template.
    """
    for name, content in template.items():
        write_json(DATA_DIR / f"{name}.json", content)


# =========================================================
# Cog
# =========================================================
class BackupSystem(commands.Cog):
    """💾 Demon Backup System (Save / Load / Export / Import)"""

    def __init__(self, bot):
        self.bot = bot

    # --------------------------------------------------------
    # Permission Check (Level 100+ or Master)
    # --------------------------------------------------------
    async def check_access(self, interaction):
        if has_master(interaction):
            return True

        if not has_level(interaction, 100):
            lvl = get_level(interaction.guild, interaction.user)
            await interaction.response.send_message(
                f"❌ Access Denied\nYour Level: `{lvl}` • Required: `100`",
                ephemeral=True
            )
            return False

        return True

    # =========================================================
    # /backup_save
    # =========================================================
    @app_commands.command(
        name="backup_save",
        description="Save all EternalMC bot settings into a template. (Level 100+)"
    )
    async def backup_save(self, interaction: discord.Interaction, name: str):

        if not await self.check_access(interaction):
            return

        data = collect_data()
        file_path = BACKUP_DIR / f"{name}.json"

        write_json(file_path, data)

        embed = make_embed(
            title="💾 Backup Saved",
            description=(
                f"Backup template **`{name}`** saved successfully.\n"
                "Use `/backup_load` to restore this configuration."
            ),
            guild=interaction.guild.id
        )

        await interaction.response.send_message(embed=embed)

    # =========================================================
    # /backup_load
    # =========================================================
    @app_commands.command(
        name="backup_load",
        description="Load a backup template and apply it. (Level 100+)"
    )
    async def backup_load(self, interaction: discord.Interaction, name: str):

        if not await self.check_access(interaction):
            return

        file_path = BACKUP_DIR / f"{name}.json"

        if not file_path.exists():
            return await interaction.response.send_message(
                "⚠️ No such backup template found.",
                ephemeral=True
            )

        template = read_json(file_path)
        apply_template(template)

        embed = make_embed(
            title="📦 Backup Loaded",
            description=f"Template **`{name}`** restored successfully.",
            guild=interaction.guild.id
        )

        await interaction.response.send_message(embed=embed)

    # =========================================================
    # /backup_list
    # =========================================================
    @app_commands.command(
        name="backup_list",
        description="List all saved backup templates."
    )
    async def backup_list(self, interaction: discord.Interaction):

        files = os.listdir(BACKUP_DIR)

        if not files:
            return await interaction.response.send_message(
                "⚠️ No backups found.",
                ephemeral=True
            )

        text = "\n".join(f"`• {f.replace('.json', '')}`" for f in files)

        embed = make_embed(
            title="📁 Available Backups",
            description=text,
            guild=interaction.guild.id
        )

        await interaction.response.send_message(embed=embed)

    # =========================================================
    # /backup_remove
    # =========================================================
    @app_commands.command(
        name="backup_remove",
        description="Delete a saved backup template. (Level 100+)"
    )
    async def backup_remove(self, interaction: discord.Interaction, name: str):

        if not await self.check_access(interaction):
            return

        file_path = BACKUP_DIR / f"{name}.json"

        if not file_path.exists():
            return await interaction.response.send_message(
                "⚠️ Backup not found.",
                ephemeral=True
            )

        os.remove(file_path)

        embed = make_embed(
            title="🗑️ Backup Deleted",
            description=f"Backup **`{name}`** removed successfully.",
            guild=interaction.guild.id
        )

        await interaction.response.send_message(embed=embed)

    # =========================================================
    # /backup_export
    # =========================================================
    @app_commands.command(
        name="backup_export",
        description="Export a backup template as a downloadable JSON file."
    )
    async def backup_export(self, interaction: discord.Interaction, name: str):

        file_path = BACKUP_DIR / f"{name}.json"

        if not file_path.exists():
            return await interaction.response.send_message(
                "⚠️ Backup not found.",
                ephemeral=True
            )

        file = discord.File(file_path, filename=f"{name}.json")

        await interaction.response.send_message(
            content="📦 Backup Exported",
            file=file
        )

    # =========================================================
    # /backup_import
    # =========================================================
    @app_commands.command(
        name="backup_import",
        description="Import a backup JSON file and save as a template."
    )
    async def backup_import(self, interaction: discord.Interaction, file: discord.Attachment):

        if not await self.check_access(interaction):
            return

        if not file.filename.endswith(".json"):
            return await interaction.response.send_message(
                "❌ File must be `.json`",
                ephemeral=True
            )

        # Load data
        template = json.loads(await file.read())
        name = file.filename.replace(".json", "")

        # Save template
        write_json(BACKUP_DIR / f"{name}.json", template)

        embed = make_embed(
            title="📥 Backup Imported",
            description=(
                f"Backup template **`{name}`** imported.\n"
                "Use `/backup_load` to apply it."
            ),
            guild=interaction.guild.id
        )

        await interaction.response.send_message(embed=embed)


# =========================================================
# Setup
# =========================================================
async def setup(bot):
    await bot.add_cog(BackupSystem(bot))
