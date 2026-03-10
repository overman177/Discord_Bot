# Debug
import logging
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Bot necessities
from core.bot_instance import *
from core.MongoDB import *

# Functionality
from utils import *
from features import *


@bot.event
async def on_ready() -> None:
    print(f"Přihlášen jako {bot.user}")
    # Synchronizace slash commandů s Discordem
    try:
        synced = await bot.tree.sync()
        print(f"Synchronizováno {len(synced)} příkazů")
    except Exception as e:
        print(f"Chyba synchronizace: {e}")


bot.run(token, log_handler=log_handler, log_level=logging.DEBUG)