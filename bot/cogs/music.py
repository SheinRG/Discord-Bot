"""Music: play / skip / stop. Uses yt-dlp for extraction (the reliable part)
and FFmpeg to stream audio into the voice channel.

Per-guild state lives in self.queues:
    guild_id -> {"queue": [Track, ...], "text": <channel>}
queue[0] is the track currently playing.
"""
import asyncio
from dataclasses import dataclass

import discord
import yt_dlp
from discord import app_commands
from discord.ext import commands

from config import FFMPEG_PATH

YTDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch1",   # plain text -> top YouTube result
    "source_address": "0.0.0.0",
    "skip_download": True,
}

FFMPEG_OPTS = {
    # -reconnect flags keep the stream alive through brief network hiccups.
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


@dataclass
class Track:
    title: str
    url: str          # YouTube watch URL (re-resolved to a fresh stream at play time)
    requester: str


def _blocking_extract(query: str) -> dict:
    with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
        info = ydl.extract_info(query, download=False)
    if info and "entries" in info:        # search result / playlist wrapper
        info = info["entries"][0]
    return info


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues: dict[int, dict] = {}

    async def _extract(self, query: str) -> dict:
        return await asyncio.to_thread(_blocking_extract, query)

    # --- playback engine -------------------------------------------------

    def _after(self, guild_id: int, error):
        """Runs in FFmpeg's thread when a track ends (or is stopped). Hop back
        onto the event loop to advance the queue."""
        if error:
            print("player error:", error)
        fut = asyncio.run_coroutine_threadsafe(self._advance(guild_id), self.bot.loop)
        try:
            fut.result()
        except Exception as e:
            print("advance error:", e)

    async def _advance(self, guild_id: int):
        q = self.queues.get(guild_id)
        if not q:
            return
        if q["queue"]:
            q["queue"].pop(0)   # drop the track that just finished
        await self._play_next(guild_id)

    async def _play_next(self, guild_id: int):
        q = self.queues.get(guild_id)
        guild = self.bot.get_guild(guild_id)
        vc = guild.voice_client if guild else None

        if not q or not q["queue"]:
            if vc:
                await vc.disconnect()
            self.queues.pop(guild_id, None)
            return

        track = q["queue"][0]
        try:
            info = await self._extract(track.url)       # fresh stream URL
            source = discord.FFmpegPCMAudio(
                info["url"], executable=FFMPEG_PATH, **FFMPEG_OPTS
            )
            vc.play(source, after=lambda e: self._after(guild_id, e))
        except Exception as e:
            print("failed to stream", track.url, e)
            ch = q.get("text")
            if ch:
                await ch.send(f"⚠️ couldn't play **{track.title}**, skipping")
            q["queue"].pop(0)
            await self._play_next(guild_id)

    # --- commands --------------------------------------------------------

    @app_commands.command(name="play", description="play a song from YouTube")
    @app_commands.describe(query="YouTube URL or search")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()

        voice_state = interaction.user.voice
        if not voice_state or not voice_state.channel:
            return await interaction.followup.send("join a voice channel first")
        channel = voice_state.channel

        try:
            info = await self._extract(query)
        except Exception as e:
            print("search failed:", e)
            return await interaction.followup.send("nothing found")
        if not info:
            return await interaction.followup.send("nothing found")

        track = Track(
            title=info.get("title", "unknown"),
            url=info.get("webpage_url") or info.get("original_url") or query,
            requester=str(interaction.user),
        )

        # connect / move into the caller's voice channel
        vc = interaction.guild.voice_client
        if not vc:
            vc = await channel.connect()
        elif vc.channel != channel:
            await vc.move_to(channel)

        q = self.queues.setdefault(interaction.guild.id, {"queue": [], "text": interaction.channel})
        q["text"] = interaction.channel
        q["queue"].append(track)

        if len(q["queue"]) == 1:
            await self._play_next(interaction.guild.id)
            await interaction.followup.send(f"🎶 now playing **{track.title}**")
        else:
            await interaction.followup.send(
                f"➕ queued **{track.title}** (position {len(q['queue']) - 1})"
            )

    @app_commands.command(name="skip", description="skip current song")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not self.queues.get(interaction.guild.id) or not vc:
            return await interaction.response.send_message("nothing playing", ephemeral=True)
        vc.stop()  # fires the after-callback -> next track
        await interaction.response.send_message("⏭️ skipped")

    @app_commands.command(name="stop", description="stop music and leave")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not self.queues.get(interaction.guild.id) or not vc:
            return await interaction.response.send_message("nothing playing", ephemeral=True)
        # Pop state first so the after-callback (fired by disconnect) no-ops.
        self.queues.pop(interaction.guild.id, None)
        await vc.disconnect()
        await interaction.response.send_message("🛑 stopped")


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
