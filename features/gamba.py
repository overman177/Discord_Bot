from features._import_ import *

@bot.tree.command(name="gamba", description="Točíme maty")
async def gamba(interaction: discord.Interaction) -> None:
    target = interaction.usere

    grid = [[random.choice(SYMBOLS) for _ in range(3)] for _ in range(3)]

    middle = grid[1]
    win = middle.count(middle[0]) == 3

    all_symbols = [symbol for row in grid for symbol in row]
    super_jackpot = all(symbol == all_symbols[0] for symbol in all_symbols)

    slot_art=f"""  
                **-----------**
                **|{grid[0][0]}|{grid[0][1]}|{grid[0][2]}|**
                **|{grid[1][0]}|{grid[1][1]}|{grid[1][2]}|<-**
                **|{grid[2][0]}|{grid[2][1]}|{grid[2][2]}|**
                **-----------**
            """

    embed = discord.Embed(title="🎰 GAMBA 🎰",description=slot_art, color=target.color)

    if super_jackpot:
        embed.add_field(
            name="💎 SUPER JACKPOT! 💎",
            value=f"Všechny symboly jsou {all_symbols[0]}!",
            inline=False
        )
    elif win:
        embed.add_field(
            name="🏆 JACKPOT! 🏆",
            value=f"**{middle[0]} {middle[1]} {middle[2]}**\nJackpot padl!",
            inline=False
        )
    else:
        embed.add_field(
            name="❌ Smůla ❌",
            value="Zkus to znovu…",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)