# Friends Bot 🤖

Personal Discord bot — slash commands, music, moderation, welcomes, inside-joke triggers. Built with discord.js v14.

## Project structure

```
src/
├── index.js              # entry — auto-loads commands + events
├── deploy-commands.js    # registers slash commands to your guild
├── commands/
│   ├── fun/              # 8ball, roast, dice, meme
│   ├── mod/              # kick, ban, clear
│   └── music/            # play, skip, stop
└── events/
    ├── ready.js
    ├── interactionCreate.js
    ├── guildMemberAdd.js  # welcomes
    └── messageCreate.js   # inside-joke auto-replies
```

Adding a new command = drop a new `.js` file in any `commands/*` folder. No registration code to touch — auto-loaded on boot.

---

## 1. Create the bot on Discord

1. Go to https://discord.com/developers/applications → **New Application**
2. **Bot** tab → reset token → copy it (this is `DISCORD_TOKEN`)
3. Enable these **Privileged Gateway Intents**: `SERVER MEMBERS`, `MESSAGE CONTENT`
4. **OAuth2 → URL Generator**: scopes = `bot` + `applications.commands`; permissions = Administrator (easiest for a friends server). Open the URL → invite to your server.
5. Copy **Application ID** from General Info → that's `CLIENT_ID`
6. In Discord, enable Developer Mode (Settings → Advanced) → right-click your server → Copy Server ID → that's `GUILD_ID`
7. Right-click the welcome channel → Copy Channel ID → that's `WELCOME_CHANNEL_ID`

## 2. Local setup

```bash
npm install
cp .env.example .env   # fill in the 4 values
npm run deploy         # registers slash commands (run once, or after adding commands)
npm start
```

Slash commands appear instantly because they're registered per-guild (not global, which takes up to an hour).

## 3. Deploy to Railway (free)

1. Push this folder to a GitHub repo (private is fine)
2. https://railway.app → New Project → Deploy from GitHub repo
3. Variables tab → add the 4 env vars from your `.env`
4. Settings → Start Command: `npm start`
5. Run `npm run deploy` locally once to register commands (or add it as a one-off deploy command)

Railway gives you ~500 hrs/month free. Bot stays online 24/7 within that. Alternatives: **Fly.io** (similar), **Render** (worker service, also free tier).

## 4. Customize

**Inside-joke triggers** → `src/events/messageCreate.js`, edit the `triggers` array.
**Welcome messages** → `src/events/guildMemberAdd.js`, edit the `lines` array.
**Roasts / 8ball answers** → `src/commands/fun/*.js`.

## Music caveat

Uses `play-dl` which scrapes YouTube. YouTube periodically breaks it → run `npm update play-dl` if music stops working. Long-term, switch to a **Lavalink** server (more setup, way more reliable).

Railway's free tier should run music fine for a small server. If audio stutters, the host CPU is the bottleneck — upgrade or move to Fly.io.

## Commands cheatsheet

| Command | What |
|---|---|
| `/8ball question:` | magic 8-ball |
| `/roast target:` | roast a friend |
| `/dice sides: count:` | roll dice |
| `/meme` | random reddit meme |
| `/play query:` | play YouTube audio |
| `/skip` `/stop` | music control |
| `/kick` `/ban` `/clear` | mod (perm-gated) |
