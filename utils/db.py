# =========================================================
#  EternalMC Multi Bot - Database Handler (SQLite)
#  Demon Edition V4
# =========================================================

import aiosqlite
import asyncio

DB_PATH = "storage.sqlite3"


async def initialize():
    """Creates all required database tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS prefixes (
                guild_id INTEGER PRIMARY KEY,
                prefix TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS premium (
                guild_id INTEGER PRIMARY KEY,
                is_premium INTEGER DEFAULT 0,
                is_botpremium INTEGER DEFAULT 0
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS bot_welcome (
                guild_id INTEGER PRIMARY KEY,
                welcomed INTEGER DEFAULT 0
            )
        """)

        await db.commit()


# -----------------------------------------
# PREFIX SYSTEM
# -----------------------------------------

async def get_prefix(guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT prefix FROM prefixes WHERE guild_id = ?", (guild_id,))
        row = await cursor.fetchone()
        return row[0] if row else None


async def set_prefix(guild_id: int, prefix: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "REPLACE INTO prefixes (guild_id, prefix) VALUES (?, ?)",
            (guild_id, prefix)
        )
        await db.commit()


# -----------------------------------------
# PREMIUM SYSTEM
# -----------------------------------------

async def set_premium(guild_id: int, state: bool):
    value = 1 if state else 0
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "REPLACE INTO premium (guild_id, is_premium, is_botpremium) VALUES (?, ?, COALESCE((SELECT is_botpremium FROM premium WHERE guild_id = ?), 0))",
            (guild_id, value, guild_id)
        )
        await db.commit()


async def set_botpremium(guild_id: int, state: bool):
    value = 1 if state else 0
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE premium SET is_botpremium = ? WHERE guild_id = ?",
            (value, guild_id)
        )
        await db.commit()


async def is_premium(guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT is_premium FROM premium WHERE guild_id = ?", (guild_id,)
        )
        row = await cursor.fetchone()
        return row and row[0] == 1


async def is_botpremium(guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT is_botpremium FROM premium WHERE guild_id = ?", (guild_id,)
        )
        row = await cursor.fetchone()
        return row and row[0] == 1


# -----------------------------------------
# BOT WELCOME TRACKER
# -----------------------------------------

async def has_welcomed(guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT welcomed FROM bot_welcome WHERE guild_id = ?", (guild_id,))
        row = await cursor.fetchone()
        return row and row[0] == 1


async def set_welcomed(guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("REPLACE INTO bot_welcome (guild_id, welcomed) VALUES (?, 1)", (guild_id,))
        await db.commit()
