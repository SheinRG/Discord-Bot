"""Moderation commands: ban, kick, clear. All permission-gated."""
import discord
from discord import app_commands
from discord.ext import commands


def _outranks(me: discord.Member, target: discord.Member) -> bool:
    """True if the bot can act on the target (not the owner, below the bot's
    top role)."""
    return target != target.guild.owner and me.top_role > target.top_role


class Mod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ban", description="ban a member")
    @app_commands.default_permissions(ban_members=True)
    @app_commands.describe(target="user", reason="reason")
    async def ban(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        reason: str = "no reason given",
    ):
        if not _outranks(interaction.guild.me, target):
            return await interaction.response.send_message(
                "can't ban that user", ephemeral=True
            )
        try:
            await target.ban(reason=reason)
        except discord.Forbidden:
            return await interaction.response.send_message(
                "can't ban that user", ephemeral=True
            )
        await interaction.response.send_message(f"🔨 banned **{target}** — {reason}")

    @app_commands.command(name="kick", description="kick a member")
    @app_commands.default_permissions(kick_members=True)
    @app_commands.describe(target="user", reason="reason")
    async def kick(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        reason: str = "no reason given",
    ):
        if not _outranks(interaction.guild.me, target):
            return await interaction.response.send_message(
                "can't kick that user", ephemeral=True
            )
        try:
            await target.kick(reason=reason)
        except discord.Forbidden:
            return await interaction.response.send_message(
                "can't kick that user", ephemeral=True
            )
        await interaction.response.send_message(f"👢 kicked **{target}** — {reason}")

    @app_commands.command(name="clear", description="bulk delete messages (last 14 days only)")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(count="1-100")
    async def clear(
        self,
        interaction: discord.Interaction,
        count: app_commands.Range[int, 1, 100],
    ):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=count)
        await interaction.followup.send(
            f"🧹 deleted {len(deleted)} messages", ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Mod(bot))
