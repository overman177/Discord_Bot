from utils._import_ import *

@bot.tree.command(name="ping", description="Kontrola odezvy bota")
async def ping(interaction: discord.Interaction) -> None:
    latency = round(bot.latency * 1000)  # v ms
    await interaction.response.send_message(f"🏓 Pong! Latence: {latency} ms")