from utils._import_ import *

@bot.tree.command(name="stats", description="Zobrazí nebo upraví statistiky hráče")
@app_commands.describe(
    stat="Stat který chceš změnit",
    amount="Kolik chceš přidat nebo ubrat",
    member="Cílový hráč (jen admin)"
)
@app_commands.choices(stat=STAT_CHOICES)
async def stats(
    interaction: discord.Interaction,
    stat: Optional[app_commands.Choice[str]] = None,
    amount: Optional[int] = None,
    member: Optional[discord.Member] = None
) -> None:
    # ===== TARGET =====
    target = member or interaction.user
    if member and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Nemáš oprávnění upravovat statistiky ostatních!",
            ephemeral=True
        )
        return

    guild = await get_guild(interaction)
    if not guild:
        return

    user = get_or_create_user(target)
    stats_data = user.get("stats", {})
    xp = user.get("xp", 0)
    level = user.get("level", 1)
    name = target.nick or target.name

    # 📊 JEN ZOBRAZENÍ PROFILU
    if stat is None:
        embed = discord.Embed(
            title=f"----- 📊 Profil hráče {name} -----",
            color=target.color
        )

        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)

        embed.add_field(
            name="Staty",
            value=(
                f"❤️ HP: {stats_data.get('hp', 0)}\n"
                f"🛡️ DEF: {stats_data.get('def', 0)}\n"
                f"🔮 MANA: {stats_data.get('mana', 0)}\n"
                f"🪄 FURIOKU: {stats_data.get('furioku', 0)}\n"
                f"🍗 HUNGER: {stats_data.get('hunger', 0)}\n\n"
                f"💪 STR: {stats_data.get('str', 0)}\n"
                f"🤸 DEX: {stats_data.get('dex', 0)}\n"
                f"🧠 INT: {stats_data.get('int', 0)}\n"
                f"🗣️ CHA: {stats_data.get('cha', 0)}\n"
                f"🥷 STEALTH: {stats_data.get('stealth', 0)}\n"
                f"🌲 SURVIVAL: {stats_data.get('survival', 0)}"
            ),
            inline=False
        )

        embed.set_footer(text="Profil uložen v MongoDB")
        await interaction.response.send_message(embed=embed)
        return

    # ✏️ ÚPRAVA STATU
    if amount is None:
        await interaction.response.send_message(
            "❌ Pokud chceš upravit stat, musíš zadat i `amount`.",
            ephemeral=True
        )
        return

    stat_name = stat.value

    # ===== XP =====
    if stat_name == "xp":
        xp, level = add_xp(target, amount)

        embed = discord.Embed(color=target.color)
        embed.description = (
            f"⭐ XP upraveno o **{amount}**\n"
            f"XP: **{xp}/5**\n"
            f"Level: **{level}**"
        )
        embed.set_footer(text=f"Hráč: {name}", icon_url=target.avatar.url if target.avatar else None)

        await interaction.response.send_message(embed=embed)
        return

    # ===== OSTATNÍ STATY =====
    old_value = stats_data.get(stat_name, 0)
    new_value = old_value + amount
    stats_data[stat_name] = new_value

    update_user(target, {"stats": stats_data})

    embed = discord.Embed(color=target.color)
    embed.description = f"📊 **{stat.name}**: {old_value} → **{new_value}**"
    embed.set_footer(text=f"Hráč: {name}", icon_url=target.avatar.url if target.avatar else None)

    await interaction.response.send_message(embed=embed)