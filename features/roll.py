from utils._import_ import *

from utils.JoinImg import *
from utils.config import DICE_DIR, TEMP_DIR
import re

DICE_REGEX = re.compile(r'(?:(\d*)d(\d+))([+-]\d+)?')


def roll_expression(expr: str):
    match = DICE_REGEX.fullmatch(expr)
    if not match:
        return None

    count_str, die_str, bonus_str = match.groups()

    count = int(count_str) if count_str else 1
    die = int(die_str)
    bonus = int(bonus_str) if bonus_str else 0

    rolls = [roll_d(die) for _ in range(count)]
    total = sum(rolls) + bonus

    return {
        "expr": expr,
        "rolls": rolls,
        "die": die,
        "bonus": bonus,
        "total": total,
    }


@bot.tree.command(name="roll", description="Hod kostkami")
@app_commands.describe(formula="Napr. 2d4 3d6+1 d8 d12+3 1d20")
async def roll(interaction: discord.Interaction, formula: str):
    team_role = get_team_role(interaction.user)
    if not team_role:
        await interaction.response.send_message(
            "❌ Nejsi členem žádného týmu.",
            ephemeral=True,
        )
        return

    current_dice_dir = os.path.join(str(DICE_DIR), team_role.name)

    member = interaction.user
    name = member.nick or member.name

    tokens = formula.lower().split()
    all_image_paths = []
    grand_total = 0

    for token in tokens:
        result = roll_expression(token)
        if result is None:
            await interaction.response.send_message(
                f"❌ Neplatný výraz: `{token}`",
                ephemeral=True,
            )
            return

        grand_total += result["total"]

        die_type = result["die"]
        for roll_value in result["rolls"]:
            img_path = get_dice_image(die_type, roll_value, current_dice_dir)
            if os.path.exists(img_path):
                all_image_paths.append(img_path)

    embed = discord.Embed(
        title="🎲 Dice Roll",
        description=f"**Formula:** `{formula}`",
        color=member.color,
    )

    embed.add_field(name="🎯 Celkem", value=f"**{grand_total}**", inline=False)
    embed.set_footer(text=f"Hráč: {name}", icon_url=interaction.user.display_avatar.url)

    os.makedirs(TEMP_DIR, exist_ok=True)

    if all_image_paths:
        combined_path = combine_dice_images(all_image_paths, output_dir=str(TEMP_DIR))
        file = discord.File(combined_path, filename="dice.png")
        embed.set_image(url="attachment://dice.png")
        await interaction.response.send_message(embed=embed, file=file)
    else:
        await interaction.response.send_message(embed=embed)
