import random
import asyncio

from utils._import_ import *

async def update_stats(interaction: discord.Interaction, win: bool, super_jackpot: bool):
    member = interaction.guild.get_member(interaction.user.id) if interaction.guild else None
    update = {
        "$inc": {
            "uses": 1,
            "jackpots": 1 if win else 0,
            "super_jackpots": 1 if super_jackpot else 0
        },
        "$set": {
            "username": interaction.user.name,
            "nickname": member.display_name if member else interaction.user.name
        }
    }

    db_leaderboards.update_one({"_id": str(interaction.user.id)}, update, upsert=True)

@app_commands.choices(leaderboard=[app_commands.Choice(name="🏆 show", value="leaderboard")])
@bot.tree.command(name="gamba", description="Točíme maty")
async def gamba(
    interaction: discord.Interaction,
    leaderboard: Optional[str] = None
) -> None:
    target = interaction.user

    if leaderboard == "leaderboard":
        await interaction.response.defer()
        top = db_leaderboards.find().sort([
            ("super_jackpots", -1),
            ("jackpots", -1),
            ("uses", -1)
        ]).limit(25)

        leaderboard_text = ""
        medals = ["🥇", "🥈", "🥉"]

        global_super_jackpots = 0
        global_jackpots = 0
        global_uses = 0
        for i, user in enumerate(top):
            medal = medals[i] if i < 3 else f"#{i+1}"

            member = interaction.guild.get_member(int(user["_id"])) if interaction.guild else None
            name = member.display_name if member else user.get("nickname", user.get("username", "Unknown"))

            leaderboard_text += (
                f"{medal} **{name}**\n"
                f"💎 {user.get('super_jackpots', 0)} | "
                f"🏆 {user.get('jackpots', 0)} | "
                f"🎰 {user.get('uses', 0)}\n\n"
            )
            global_uses += user.get('uses', 0)
            global_super_jackpots += user.get('super_jackpots', 0)
            global_jackpots += user.get('jackpots', 0)

        embed = discord.Embed(
            title="🏆 GAMBA Leaderboard",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="🏅 Top hráči",
            value=leaderboard_text,
            inline=True
        )

        embed.add_field(
            name="🌍 Globální statistiky",
            value=(
                f"🎰 Spiny: **{global_uses}**\n"
                f"🏆 Jackpoty: **{global_jackpots}**\n"
                f"💎 Super jackpoty: **{global_super_jackpots}**"
            ),
            inline=True
        )

        await interaction.followup.send(embed=embed)
        return

    def spin_grid():
        return [[random.choice(SYMBOLS) for _ in range(3)] for _ in range(3)]
    
    def render(grid):
        return f"""
                **-----------**
                **|{grid[0][0]}|{grid[0][1]}|{grid[0][2]}|**
                **|{grid[1][0]}|{grid[1][1]}|{grid[1][2]}|<-**
                **|{grid[2][0]}|{grid[2][1]}|{grid[2][2]}|**
                **-----------**
            """

    # první náhodný grid
    grid = spin_grid()
    embed = discord.Embed(
        title="🎰 GAMBA 🎰",
        description=render(grid),
        color=target.color if target.color.value != 0 else discord.Color.gold()
    )

    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()

    # animace
    for _ in range(4):
        await asyncio.sleep(0.3)
        grid = spin_grid()
        embed.description = render(grid)
        await message.edit(embed=embed)

    # finální výsledek
    middle = grid[1]
    win = len(set(middle)) == 1
    all_symbols = [s for row in grid for s in row]
    super_jackpot = len(set(all_symbols)) == 1

    if super_jackpot:
        embed.add_field(
            name="💎 SUPER JACKPOT! 💎",
            value=f"Všechny symboly jsou {all_symbols[0]}!",
            inline=False
        )
    elif win:
        embed.add_field(
            name="🏆 JACKPOT! 🏆",
            value=f"**{' '.join(middle)}**\nJackpot padl!",
            inline=False
        )
    else:
        embed.add_field(
            name="❌ Smůla ❌",
            value="Zkus to znovu…",
            inline=False
        )

    await update_stats(interaction, win, super_jackpot)
    await message.edit(embed=embed)