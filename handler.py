import discord
from discord.ext import commands

import logging
# ===== DISCORD =============================================================================================================
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready() -> None:
    print(f"Přihlášen jako {bot.user}")
    # Synchrinizacevslash commandu s discordem
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")