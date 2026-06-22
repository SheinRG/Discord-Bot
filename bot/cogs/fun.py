"""Fun commands: 8ball, dice, meme, roast."""
import random

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

EIGHTBALL = [
    "yes 💯", "absolutely not", "maybe lol", "ask again when sober",
    "signs point to yes", "big no from me", "bhai sochke bata raha hu... haan",
    "nope, cope", "100% certified yes", "mat kar yaar",
]

ROASTS = [
    "you write code like git blame is gonna find someone else",
    "your commit messages are 'fix' and somehow that's the most accurate part",
    "bro deploys to prod on friday and wonders why weekends are stressful",
    "tu LeetCode easy ko bhi 'tomorrow' bolta hai",
    "your VS Code has more extensions than your project has users",
    "you Ctrl+S like the file is gonna run away",
]


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="8ball", description="ask the magic 8-ball")
    @app_commands.describe(question="your question")
    async def eightball(self, interaction: discord.Interaction, question: str):
        await interaction.response.send_message(
            f"🎱 **Q:** {question}\n**A:** {random.choice(EIGHTBALL)}"
        )

    @app_commands.command(name="dice", description="roll dice")
    @app_commands.describe(sides="number of sides (default 6)", count="how many dice (default 1)")
    async def dice(
        self,
        interaction: discord.Interaction,
        sides: app_commands.Range[int, 2, 1000] = 6,
        count: app_commands.Range[int, 1, 20] = 1,
    ):
        rolls = [random.randint(1, sides) for _ in range(count)]
        joined = ", ".join(str(r) for r in rolls)
        await interaction.response.send_message(
            f"🎲 rolled `{joined}` — total **{sum(rolls)}**"
        )

    @app_commands.command(name="meme", description="fetch a random meme from r/memes")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://meme-api.com/gimme") as res:
                    m = await res.json()
            embed = discord.Embed(title=m["title"], url=m["postLink"])
            embed.set_image(url=m["url"])
            embed.set_footer(text=f"👍 {m['ups']} • r/{m['subreddit']}")
            await interaction.followup.send(embed=embed)
        except Exception:
            await interaction.followup.send("meme api ded rn, try again")

    @app_commands.command(name="roast", description="roast someone (lovingly)")
    @app_commands.describe(target="victim")
    async def roast(self, interaction: discord.Interaction, target: discord.Member):
        await interaction.response.send_message(f"{target.mention}, {random.choice(ROASTS)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
