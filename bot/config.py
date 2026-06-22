"""Central config: loads .env and resolves the ffmpeg binary."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID")) if os.getenv("GUILD_ID") else None
WELCOME_CHANNEL_ID = (
    int(os.getenv("WELCOME_CHANNEL_ID")) if os.getenv("WELCOME_CHANNEL_ID") else None
)


def _resolve_ffmpeg() -> str:
    """Prefer the local bundled binary (bin/ffmpeg.exe), otherwise fall back to
    ffmpeg on PATH (e.g. on a Linux host where you `apt install ffmpeg`)."""
    name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    local = BASE_DIR / "bin" / name
    return str(local) if local.exists() else "ffmpeg"


FFMPEG_PATH = _resolve_ffmpeg()
