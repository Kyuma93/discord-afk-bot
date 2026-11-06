
import discord
from discord.ext import commands, tasks
import time
import os

TOKEN = os.getenv("DISCORD_TOKEN")
AFK_CHANNEL_NAME = "AFK"
INACTIVITY_SECONDS = 600

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_activity = {}

@bot.event
async def on_ready():
    print(f"Bejelentkezve: {bot.user}")
    check_inactivity.start()

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    if after.channel is None:
        last_activity.pop(member.id, None)
        return

    if before.channel != after.channel:
        last_activity[member.id] = time.time()

    if before.self_mute != after.self_mute:
        last_activity[member.id] = time.time()

@tasks.loop(seconds=15)
async def check_inactivity():
    for guild in bot.guilds:
        afk_channel = discord.utils.get(
            guild.voice_channels,
            name=AFK_CHANNEL_NAME
        )

        if afk_channel is None:
            continue

        for channel in guild.voice_channels:
            if channel == afk_channel:
                continue

            for member in channel.members:
                if member.bot:
                    continue

                last = last_activity.setdefault(
                    member.id, time.time()
                )

                if time.time() - last >= INACTIVITY_SECONDS:
                    try:
                        await member.move_to(afk_channel)
                        last_activity[member.id] = time.time()
                    except discord.Forbidden:
                        print(f"Nincs jogosultság: {member}")

bot.run(TOKEN)
