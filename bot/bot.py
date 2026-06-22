"""Friends Bot — Python edition (discord.py + yt-dlp).

Entry point: loads cogs, syncs slash commands to the guild (instant), and runs.
Run with:  .venv/Scripts/python.exe bot.py
"""
import sys
import traceback

# Windows consoles default to cp1252, which chokes on emoji in print(). Force
# UTF-8 so our log lines (🤖, ✅, ⚠️) don't crash the bot on startup.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", line_buffering=True)
    except (AttributeError, ValueError):
        pass

import discord
from discord import app_commands
from discord.ext import commands

from config import DISCORD_TOKEN, GUILD_ID

intents = discord.Intents.default()
intents.message_content = True   # for inside-joke triggers
intents.members = True           # for welcomes
intents.voice_states = True      # for music

COGS = ("cogs.fun", "cogs.mod", "cogs.music", "cogs.events", "cogs.economy")


class FriendsBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        for ext in COGS:
            await self.load_extension(ext)

        # Guild-scoped sync = commands appear instantly (global sync takes ~1h).
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            print(f"✅ synced {len(synced)} commands to guild {GUILD_ID}")


bot = FriendsBot()


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    # Mirror of the old interactionCreate try/catch: log it, tell the user once,
    # and never let a failed reply crash the process.
    print("app command error:", error)
    traceback.print_exception(type(error), error, error.__traceback__)
    msg = "💀 something broke. yell at raghav."
    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception as e:
        print("failed to send error reply:", e)


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
