# Debug
import logging

# Bot necesities
from core.bot_instance import *
from core.MongoDB import *

# Functionality
from utils    import *
from features import *

@bot.event
async def on_ready() -> None:
    print(f"Přihlášen jako {bot.user}")
    # Synchrinizacevslash commandu s discordem
    try:
        synced = await bot.tree.sync()
        print(f"Synchronizováno {len(synced)} příkazů")
    except Exception as e:
        print(f"Chyba synchronizace: {e}")

bot.run(token, log_handler=log_handler, log_level=logging.DEBUG)