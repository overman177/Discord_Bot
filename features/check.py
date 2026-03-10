from utils._import_ import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@bot.tree.command(name="check", description="Hod D20 + bonus ze statu")
@app_commands.describe(stat="Stat na který chceš hodit check")
@app_commands.choices(stat=CHECK_STAT_CHOICES)
async def check(interaction: discord.Interaction, stat: app_commands.Choice[str]) -> None:
    Dice_Dir = os.path.join(BASE_DIR, "..", "Dice", get_team_role(interaction.user).name)

    member = interaction.user
    name = member.nick or member.name

    stat_name = stat.value

    # získej profil
    user = get_or_create_user(member)
    stats = user.get("stats", {})
    bonus = stats.get(stat_name, 0)

    # hod D20
    dice = roll_d(20)
    total = dice + bonus

    embed = discord.Embed(title=f"🎲 {stat.name} – Check", color=member.color)

    description = (
        f"**Hod kostkou:** {dice}\n"
        f"**Bonus ({stat.name}):** {bonus}\n"
        f"**Celkem:** {total}"
    )

    # ===== NATURAL 20 =====
    if dice == 20:
        description += "\n\n🎉 **NATURAL 20!!**"
        add_xp(member, 1)
        description += "\n⭐ +1 XP a Náhodný perk"

    image_path = get_dice_image(20, dice, Dice_Dir)
    file = discord.File(image_path, filename="dice.png")
    embed.set_thumbnail(url="attachment://dice.png")

    embed.description = description
    embed.set_footer(text=f"Hráč: {name}", icon_url=member.avatar.url if member.avatar else None)

    await interaction.response.send_message(embed=embed, file=file)