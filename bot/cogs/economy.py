"""Currency economy + games (Dank Memer style).

State is persisted in SQLite (economy.db) so balances/traps/cooldowns survive
restarts. Everything is scoped per-guild via (guild_id, user_id).

Tweak the CONSTANTS block to rebalance the economy.
"""
import random
import time
from pathlib import Path

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands

# ----------------------------------------------------------------------------
# CONSTANTS — tune the economy here
# ----------------------------------------------------------------------------
COIN = "🪙"

DAILY_AMOUNT = 500
DAILY_CD = 24 * 60 * 60          # 24h

WORK_RANGE = (80, 350)
WORK_CD = 60 * 60                # 1h

BEG_RANGE = (0, 120)             # can come up empty
BEG_CD = 5 * 60                  # 5m

STEAL_CD = 30 * 60              # 30m
STEAL_MIN_TARGET_WALLET = 100    # target must have at least this to be worth it
STEAL_SUCCESS_CHANCE = 0.5
STEAL_TAKE_RANGE = (0.20, 0.60)  # fraction of target wallet stolen on success
STEAL_FINE_RANGE = (0.10, 0.30)  # fraction of YOUR wallet lost on failure

TRAP_MIN = 50                    # min coins to arm a trap
TRAP_PAYOUT_MULT = 2             # robber pays owner this * trap cost

WORK_FLAVOR = [
    "you debugged prod and somehow didn't make it worse",
    "you delivered food in the rain like a champ",
    "you sold a sketchy NFT to a stranger",
    "you fixed your chacha's wifi",
    "you streamed for 6 hours, 2 people watched",
    "you did a freelance gig and actually got paid",
]
BEG_GOOD = [
    "a kind stranger took pity on you",
    "you found coins under the couch",
    "someone Venmo'd you by mistake",
    "a uncle gave you chai money",
]
BEG_BAD = [
    "everyone ignored you. embarrassing.",
    "a pigeon stole your sign.",
    "you got a lecture instead of cash.",
]


def fmt(amount: int) -> str:
    return f"{COIN} **{amount:,}**"


def human_time(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if s and not h:
        parts.append(f"{s}s")
    return " ".join(parts) or "0s"


SCHEMA = """
CREATE TABLE IF NOT EXISTS economy (
    guild_id INTEGER NOT NULL,
    user_id  INTEGER NOT NULL,
    wallet   INTEGER NOT NULL DEFAULT 0,
    bank     INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (guild_id, user_id)
);
CREATE TABLE IF NOT EXISTS cooldowns (
    guild_id INTEGER NOT NULL,
    user_id  INTEGER NOT NULL,
    command  TEXT    NOT NULL,
    used_at  REAL    NOT NULL,
    PRIMARY KEY (guild_id, user_id, command)
);
CREATE TABLE IF NOT EXISTS traps (
    guild_id   INTEGER NOT NULL,
    owner_id   INTEGER NOT NULL,
    cost       INTEGER NOT NULL,
    created_at REAL    NOT NULL,
    PRIMARY KEY (guild_id, owner_id)
);
"""


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: aiosqlite.Connection | None = None

    async def cog_load(self):
        path = Path(__file__).resolve().parent.parent / "economy.db"
        self.db = await aiosqlite.connect(path)
        self.db.row_factory = aiosqlite.Row
        await self.db.executescript(SCHEMA)
        await self.db.commit()

    async def cog_unload(self):
        if self.db:
            await self.db.close()

    # --- balance helpers -------------------------------------------------

    async def _ensure(self, gid: int, uid: int):
        await self.db.execute(
            "INSERT OR IGNORE INTO economy (guild_id, user_id) VALUES (?, ?)", (gid, uid)
        )

    async def _get(self, gid: int, uid: int) -> tuple[int, int]:
        await self._ensure(gid, uid)
        async with self.db.execute(
            "SELECT wallet, bank FROM economy WHERE guild_id=? AND user_id=?", (gid, uid)
        ) as cur:
            row = await cur.fetchone()
        return row["wallet"], row["bank"]

    async def _add(self, gid: int, uid: int, wallet: int = 0, bank: int = 0):
        await self._ensure(gid, uid)
        await self.db.execute(
            "UPDATE economy SET wallet = wallet + ?, bank = bank + ? "
            "WHERE guild_id=? AND user_id=?",
            (wallet, bank, gid, uid),
        )

    # --- cooldown helpers ------------------------------------------------

    async def _cd_remaining(self, gid: int, uid: int, cmd: str, period: int) -> float:
        async with self.db.execute(
            "SELECT used_at FROM cooldowns WHERE guild_id=? AND user_id=? AND command=?",
            (gid, uid, cmd),
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return 0.0
        elapsed = time.time() - row["used_at"]
        return max(0.0, period - elapsed)

    async def _cd_set(self, gid: int, uid: int, cmd: str):
        await self.db.execute(
            "INSERT INTO cooldowns (guild_id, user_id, command, used_at) VALUES (?,?,?,?) "
            "ON CONFLICT(guild_id, user_id, command) DO UPDATE SET used_at=excluded.used_at",
            (gid, uid, cmd, time.time()),
        )

    # --- earning ---------------------------------------------------------

    @app_commands.command(name="daily", description="claim your daily coins")
    async def daily(self, interaction: discord.Interaction):
        gid, uid = interaction.guild.id, interaction.user.id
        left = await self._cd_remaining(gid, uid, "daily", DAILY_CD)
        if left:
            return await interaction.response.send_message(
                f"⏳ already claimed. come back in **{human_time(left)}**", ephemeral=True
            )
        await self._add(gid, uid, wallet=DAILY_AMOUNT)
        await self._cd_set(gid, uid, "daily")
        await self.db.commit()
        await interaction.response.send_message(f"📅 daily claimed! +{fmt(DAILY_AMOUNT)} to your wallet")

    @app_commands.command(name="work", description="work a shift for some coins")
    async def work(self, interaction: discord.Interaction):
        gid, uid = interaction.guild.id, interaction.user.id
        left = await self._cd_remaining(gid, uid, "work", WORK_CD)
        if left:
            return await interaction.response.send_message(
                f"😮‍💨 you're tired. rest for **{human_time(left)}**", ephemeral=True
            )
        earned = random.randint(*WORK_RANGE)
        await self._add(gid, uid, wallet=earned)
        await self._cd_set(gid, uid, "work")
        await self.db.commit()
        await interaction.response.send_message(
            f"💼 {random.choice(WORK_FLAVOR)} — earned {fmt(earned)}"
        )

    @app_commands.command(name="beg", description="beg for spare change")
    async def beg(self, interaction: discord.Interaction):
        gid, uid = interaction.guild.id, interaction.user.id
        left = await self._cd_remaining(gid, uid, "beg", BEG_CD)
        if left:
            return await interaction.response.send_message(
                f"🙏 have some dignity. wait **{human_time(left)}**", ephemeral=True
            )
        earned = random.randint(*BEG_RANGE)
        await self._cd_set(gid, uid, "beg")
        if earned <= 0:
            await self.db.commit()
            return await interaction.response.send_message(f"😔 {random.choice(BEG_BAD)}")
        await self._add(gid, uid, wallet=earned)
        await self.db.commit()
        await interaction.response.send_message(
            f"🤲 {random.choice(BEG_GOOD)} — got {fmt(earned)}"
        )

    # --- money management ------------------------------------------------

    @app_commands.command(name="balance", description="check your (or someone's) coins")
    @app_commands.describe(user="whose balance to check")
    async def balance(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        wallet, bank = await self._get(interaction.guild.id, target.id)
        embed = discord.Embed(title=f"{target.display_name}'s balance", color=0xF1C40F)
        embed.add_field(name="wallet", value=fmt(wallet))
        embed.add_field(name="bank", value=fmt(bank))
        embed.add_field(name="net worth", value=fmt(wallet + bank), inline=False)
        embed.set_thumbnail(url=target.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="give", description="give coins to someone")
    @app_commands.describe(user="recipient", amount="how much")
    async def give(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: app_commands.Range[int, 1, None],
    ):
        gid = interaction.guild.id
        if user.bot or user.id == interaction.user.id:
            return await interaction.response.send_message(
                "pick an actual other person", ephemeral=True
            )
        wallet, _ = await self._get(gid, interaction.user.id)
        if amount > wallet:
            return await interaction.response.send_message(
                f"you only have {fmt(wallet)} in your wallet", ephemeral=True
            )
        await self._add(gid, interaction.user.id, wallet=-amount)
        await self._add(gid, user.id, wallet=amount)
        await self.db.commit()
        await interaction.response.send_message(
            f"🤝 {interaction.user.mention} gave {fmt(amount)} to {user.mention}"
        )

    @app_commands.command(name="deposit", description="move coins wallet → bank (safe from robbers)")
    @app_commands.describe(amount="how much (leave empty for all)")
    async def deposit(
        self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, None] = None
    ):
        gid, uid = interaction.guild.id, interaction.user.id
        wallet, _ = await self._get(gid, uid)
        amount = amount or wallet
        if wallet <= 0:
            return await interaction.response.send_message("your wallet is empty", ephemeral=True)
        if amount > wallet:
            return await interaction.response.send_message(
                f"you only have {fmt(wallet)} on hand", ephemeral=True
            )
        await self._add(gid, uid, wallet=-amount, bank=amount)
        await self.db.commit()
        await interaction.response.send_message(f"🏦 deposited {fmt(amount)} to your bank")

    @app_commands.command(name="withdraw", description="move coins bank → wallet")
    @app_commands.describe(amount="how much (leave empty for all)")
    async def withdraw(
        self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, None] = None
    ):
        gid, uid = interaction.guild.id, interaction.user.id
        _, bank = await self._get(gid, uid)
        amount = amount or bank
        if bank <= 0:
            return await interaction.response.send_message("your bank is empty", ephemeral=True)
        if amount > bank:
            return await interaction.response.send_message(
                f"you only have {fmt(bank)} in the bank", ephemeral=True
            )
        await self._add(gid, uid, wallet=amount, bank=-amount)
        await self.db.commit()
        await interaction.response.send_message(f"💸 withdrew {fmt(amount)} to your wallet")

    # --- robbery & traps -------------------------------------------------

    @app_commands.command(name="trap", description="arm a trap; a robber triggers it and pays you double")
    @app_commands.describe(amount=f"coins to invest in the trap (min {TRAP_MIN})")
    async def trap(
        self, interaction: discord.Interaction, amount: app_commands.Range[int, TRAP_MIN, None]
    ):
        gid, uid = interaction.guild.id, interaction.user.id
        async with self.db.execute(
            "SELECT 1 FROM traps WHERE guild_id=? AND owner_id=?", (gid, uid)
        ) as cur:
            if await cur.fetchone():
                return await interaction.response.send_message(
                    "you already have a trap armed", ephemeral=True
                )
        wallet, _ = await self._get(gid, uid)
        if amount > wallet:
            return await interaction.response.send_message(
                f"you only have {fmt(wallet)} in your wallet", ephemeral=True
            )
        await self._add(gid, uid, wallet=-amount)
        await self.db.execute(
            "INSERT INTO traps (guild_id, owner_id, cost, created_at) VALUES (?,?,?,?)",
            (gid, uid, amount, time.time()),
        )
        await self.db.commit()
        await interaction.response.send_message(
            f"🪤 trap armed for {fmt(amount)}. next person who robs you pays "
            f"{fmt(amount * TRAP_PAYOUT_MULT)}.",
            ephemeral=True,
        )

    @app_commands.command(name="steal", description="try to rob someone's wallet (risky!)")
    @app_commands.describe(user="your victim")
    async def steal(self, interaction: discord.Interaction, user: discord.Member):
        gid, robber = interaction.guild.id, interaction.user.id
        if user.bot or user.id == robber:
            return await interaction.response.send_message(
                "rob a real person, not yourself or a bot", ephemeral=True
            )

        left = await self._cd_remaining(gid, robber, "steal", STEAL_CD)
        if left:
            return await interaction.response.send_message(
                f"🚓 lay low for **{human_time(left)}**", ephemeral=True
            )
        await self._cd_set(gid, robber, "steal")

        # 1) Trap check — does the victim have one armed?
        async with self.db.execute(
            "SELECT cost FROM traps WHERE guild_id=? AND owner_id=?", (gid, user.id)
        ) as cur:
            trap_row = await cur.fetchone()

        if trap_row:
            r_wallet, _ = await self._get(gid, robber)
            penalty = min(r_wallet, trap_row["cost"] * TRAP_PAYOUT_MULT)
            await self._add(gid, robber, wallet=-penalty)
            await self._add(gid, user.id, wallet=penalty)
            await self.db.execute(
                "DELETE FROM traps WHERE guild_id=? AND owner_id=?", (gid, user.id)
            )
            await self.db.commit()
            return await interaction.response.send_message(
                f"💥 {interaction.user.mention} stepped on {user.mention}'s trap and "
                f"paid them {fmt(penalty)}! 🪤"
            )

        # 2) Normal robbery attempt.
        t_wallet, _ = await self._get(gid, user.id)
        if t_wallet < STEAL_MIN_TARGET_WALLET:
            await self.db.commit()
            return await interaction.response.send_message(
                f"{user.mention} has barely any cash on hand. not worth it.", ephemeral=True
            )

        if random.random() < STEAL_SUCCESS_CHANCE:
            stolen = int(t_wallet * random.uniform(*STEAL_TAKE_RANGE))
            stolen = max(1, stolen)
            await self._add(gid, user.id, wallet=-stolen)
            await self._add(gid, robber, wallet=stolen)
            await self.db.commit()
            return await interaction.response.send_message(
                f"🦝 {interaction.user.mention} robbed {fmt(stolen)} from {user.mention}!"
            )
        else:
            r_wallet, _ = await self._get(gid, robber)
            fine = int(r_wallet * random.uniform(*STEAL_FINE_RANGE))
            await self._add(gid, robber, wallet=-fine)
            await self._add(gid, user.id, wallet=fine)
            await self.db.commit()
            return await interaction.response.send_message(
                f"🚨 {interaction.user.mention} got caught robbing {user.mention} and "
                f"paid them {fmt(fine)} in damages!"
            )

    # --- leaderboard -----------------------------------------------------

    @app_commands.command(name="leaderboard", description="richest people in the server")
    async def leaderboard(self, interaction: discord.Interaction):
        async with self.db.execute(
            "SELECT user_id, wallet + bank AS total FROM economy "
            "WHERE guild_id=? ORDER BY total DESC LIMIT 10",
            (interaction.guild.id,),
        ) as cur:
            rows = await cur.fetchall()
        if not rows:
            return await interaction.response.send_message("nobody has any money yet 💀")
        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for idx, row in enumerate(rows):
            member = interaction.guild.get_member(row["user_id"])
            name = member.display_name if member else f"user {row['user_id']}"
            rank = medals[idx] if idx < 3 else f"`#{idx + 1}`"
            lines.append(f"{rank} **{name}** — {fmt(row['total'])}")
        embed = discord.Embed(
            title="💰 richest in the server", description="\n".join(lines), color=0xF1C40F
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
