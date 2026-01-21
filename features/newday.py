from features._import_ import *

@bot.tree.command(name="newday", description="Spustí nový den (hunger / HP / reset perků)")
@app_commands.checks.has_permissions(administrator=True)
async def newday(interaction: discord.Interaction) -> None:
    guild = await get_guild(interaction)
    if not guild:
        return  # příkaz nelze spustit mimo server

    for member in guild.members:
        if member.bot:
            continue

        user = get_or_create_user(member)
        stats = user.get("stats", {})
        perks_list = user.get("perks", [])

        # ===== HUNGER / HP =====
        hunger = stats.get("hunger", 0)
        hp = stats.get("hp", 100)

        if hunger >= 10:
            stats["hunger"] = hunger - 10
        else:
            stats["hunger"] = 0
            stats["hp"] = max(0, hp - 10)

        # ===== RESET AKTIVNÍCH PERKŮ =====
        for perk in perks_list:
            if perk["uses"] != "passive":
                perk["used"] = 0

        # ===== ULOŽENÍ DO DB =====
        update_user(member, {"stats": stats, "perks": perks_list})

    # ===== ZPRÁVA =====
    embed = discord.Embed(
        title="🌞 Nový den začal!",
        description="Hodnoty hunger a HP hráčů byly upraveny.\n\n🔄 Všechny aktivní perky byly resetovány.",
        color=interaction.guild.me.color
    )

    await interaction.response.send_message(embed=embed)