"""Passive behaviour: ready/presence, inside-joke auto-replies, welcomes."""
import random
import re

import discord
from discord.ext import commands

from config import WELCOME_CHANNEL_ID

# Edit freely — (compiled regex, list of possible replies). First match wins.
TRIGGERS = [
    (re.compile(r"\bbruh\b", re.I), ["bruh moment certified ✅", "bruh ➡️ ☠️"]),
    (re.compile(r"\bskill issue\b", re.I), ["confirmed skill issue", "L + ratio + skill issue"]),
    (re.compile(r"\bdeploy\b", re.I), ["it works on my machine 🤷", "ship it, fix it in prod"]),
    # add your friend-specific ones here, e.g.:
    # (re.compile(r"\baman\b", re.I), ["aman sote hue bhi code likhta hai"]),
]

WELCOMES = [
    "yo <@{id}> just pulled up 🫡",
    "<@{id}> entered the chat. behave.",
    "welcome <@{id}> — read #rules or don't, idc",
    "oye <@{id}> aagaya bhai, swagat hai 🎉",
]


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"🤖 Logged in as {self.bot.user}")
        await self.bot.change_presence(activity=discord.Game(name="with the homies"))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        for pattern, replies in TRIGGERS:
            if pattern.search(message.content):
                await message.reply(random.choice(replies), mention_author=False)
                return

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not WELCOME_CHANNEL_ID:
            return
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return
        await channel.send(random.choice(WELCOMES).format(id=member.id))


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
