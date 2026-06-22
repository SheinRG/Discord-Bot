# Friends Bot 🤖

Personal Discord bot — slash commands, music, moderation, welcomes, inside-joke triggers. Built with **discord.py** + **yt-dlp**.

> Rewritten from the original discord.js version. yt-dlp is the most reliable YouTube extractor going, which is why music actually works now. The old JS code is still in `src/` (legacy, not used).

## Project structure

```
bot.py                 # entry — loads cogs, syncs slash commands, runs
config.py              # loads .env + resolves the ffmpeg binary
requirements.txt
cogs/
├── fun.py             # 8ball, dice, meme, roast
├── mod.py             # ban, kick, clear  (permission-gated)
├── music.py           # play, skip, stop  (yt-dlp + ffmpeg)
└── events.py          # ready/presence, inside-joke auto-replies, welcomes
```

Adding a command = add an `@app_commands.command` method to a cog. It's synced to the guild automatically on the next boot.

---

## 1. Create the bot on Discord

1. https://discord.com/developers/applications → **New Application**
2. **Bot** tab → reset token → copy it (this is `DISCORD_TOKEN`)
3. Enable these **Privileged Gateway Intents**: `SERVER MEMBERS`, `MESSAGE CONTENT`
4. **OAuth2 → URL Generator**: scopes = `bot` + `applications.commands`; permissions = Administrator (easiest for a friends server). Open the URL → invite to your server.
5. Copy **Application ID** from General Info → that's `CLIENT_ID`
6. Discord → enable Developer Mode (Settings → Advanced) → right-click your server → Copy Server ID → that's `GUILD_ID`
7. Right-click the welcome channel → Copy Channel ID → that's `WELCOME_CHANNEL_ID`

## 2. Local setup (Windows)

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
# create .env with the 4 values below
.venv\Scripts\python.exe bot.py
```

`.env`:
```
DISCORD_TOKEN=...
CLIENT_ID=...
GUILD_ID=...
WELCOME_CHANNEL_ID=...
```

Slash commands are synced **per-guild** on every boot, so they appear instantly (global sync would take ~1h).

### ffmpeg

Music needs an `ffmpeg` binary. On this machine it reuses the one the old node setup already downloaded (`node_modules/ffmpeg-static/ffmpeg.exe`) automatically. If that folder is gone, install ffmpeg and put it on PATH — `config.py` falls back to `ffmpeg` on PATH.

## 3. Deploy (free hosts)

Push to GitHub, then on **Railway** / **Fly.io** / **Render**:
- Start command: `python bot.py`
- Add the 4 env vars
- **Install ffmpeg on the host** (Railway: add `ffmpeg` via a Nixpacks/apt config; the bundled `node_modules` binary won't exist there).

## 4. Customize

- **Inside-joke triggers** → `cogs/events.py`, edit the `TRIGGERS` list.
- **Welcome messages** → `cogs/events.py`, edit `WELCOMES`.
- **Roasts / 8ball answers** → `cogs/fun.py`.

## Commands cheatsheet

| Command | What |
|---|---|
| `/8ball question:` | magic 8-ball |
| `/roast target:` | roast a friend |
| `/dice sides: count:` | roll dice |
| `/meme` | random reddit meme |
| `/play query:` | play YouTube audio (URL or search) |
| `/skip` `/stop` | music control |
| `/kick` `/ban` `/clear` | mod (perm-gated) |

### Economy 🪙 (Dank Memer style)

State persists in `economy.db` (SQLite). Tune amounts/cooldowns/odds in the `CONSTANTS` block at the top of `cogs/economy.py`.

| Command | What |
|---|---|
| `/daily` | claim daily coins (24h) |
| `/work` | work for coins (1h cooldown) |
| `/beg` | beg for spare change (5m cooldown) |
| `/balance [user]` | wallet + bank + net worth |
| `/give user: amount:` | transfer coins |
| `/deposit [amount]` | wallet → bank (safe from robbery; empty = all) |
| `/withdraw [amount]` | bank → wallet (empty = all) |
| `/steal user:` | rob someone's wallet — 50% odds; fail = you pay a fine; 30m cooldown |
| `/trap amount:` | arm a trap; the next robber triggers it and pays you double |
| `/leaderboard` | richest in the server |

**The rob/trap loop:** only the **wallet** is stealable, so `/deposit` protects your coins. Arming a `/trap` turns the tables — a would-be robber walks into it and pays you `2×` your investment instead.
