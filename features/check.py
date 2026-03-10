from utils._import_ import *

from utils.config import DICE_DIR


@bot.tree.command(name="check", description="Hod D20 + bonus ze statu")
@app_commands.describe(stat="Stat na který chceš hodit check")
@app_commands.choices(stat=CHECK_STAT_CHOICES)
async def check(interaction: discord.Interaction, stat: app_commands.Choice[str]) -> None:
    team_role = get_team_role(interaction.user)
    if not team_role:
        await interaction.response.send_message(
            "❌ Nejsi členem žádného týmu.",
            ephemeral=True,
        )
        return

    dice_dir = os.path.join(str(DICE_DIR), team_role.name)

    member = interaction.user
    name = member.nick or member.name
    stat_name = stat.value

    user = get_or_create_user(member)
    stats = user.get("stats", {})
    bonus = stats.get(stat_name, 0)

    dice = roll_d(20)
    total = dice + bonus

    embed = discord.Embed(title=f"🎲 {stat.name} - Check", color=member.color)
    description = (
        f"**Hod kostkou:** {dice}\n"
        f"**Bonus ({stat.name}):** {bonus}\n"
        f"**Celkem:** {total}"
    )

    if dice == 20:
        description += "\n\n🎉 **NATURAL 20!!**"
        add_xp(member, 1)
        description += "\n⭐ +1 XP"

    image_path = get_dice_image(20, dice, dice_dir)
    file = discord.File(image_path, filename="dice.png")
    embed.set_thumbnail(url="attachment://dice.png")
    embed.description = description
    embed.set_footer(text=f"Hráč: {name}", icon_url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed, file=file)
