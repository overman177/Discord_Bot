# Debug
import logging

# Bot necesities
from handler  import *
from MongoDB  import *

# Functionality
from utils    import *
from features import *

@bot.event
async def on_ready() -> None:
    print(f"Přihlášen jako {bot.user}")
    # Synchrinizacevslash commandu s discordem
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)