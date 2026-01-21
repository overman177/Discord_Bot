from features._import_ import *

@bot.tree.command(name="tabor", description="Zobrazí nebo spravuje tábor týmu")
@app_commands.describe(
    action="add / remove",
    category="co bude upraveno",
    value="Hodnota (číslo nebo text)",
    team="Tým (jen admin)"
)
@app_commands.choices(action=ACTION_CHOICES)
async def tabor(
    interaction: discord.Interaction,
    action: Optional[app_commands.Choice[str]] = None,
    category: Optional[str] = None,
    value: Optional[str] = None,
    team: Optional[discord.Role] = None
) -> None:
    # ADMIN override
    if team:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Jen admin může spravovat cizí tábor.", ephemeral=True)
            return
        if team.name not in TEAM_ROLES:
            await interaction.response.send_message("❌ Zvolená role není tým.", ephemeral=True)
            return
        team_role = team
    else:
        team_role = get_team_role(interaction.user)
        if not team_role:
            await interaction.response.send_message("❌ Nejsi členem žádného týmu.", ephemeral=True)
            return

    camp = get_or_create_camp(interaction.guild.id, team_role)

    # ===== VIEW ONLY =====
    if not action:
        embed = build_camp_embed(camp, team_role)
        await interaction.response.send_message(embed=embed)
        return
    
    # mapování kategorií na DB klíče
    resource_map = {"dřevo": "wood", "kámen": "stone", "scrap": "scrap"}
    list_map = {"vylepšení": "upgrades", "sklad": "storage", "blueprints": "blueprints"}
    
    if category in resource_map:
        # === RESOURCES ===
        try:
            amount = int(value)
        except ValueError:
            await interaction.response.send_message("❌ Musíš zadat číslo.", ephemeral=True)
            return
        op = 1 if action.value == "add" else -1
        camps_col.update_one(
            {"_id": camp["_id"]},
            {"$inc": {f"resources.{resource_map[category]}": amount * op}}
        )
        msg = f"{'Přidáno' if op > 0 else 'Odebráno'} {category} {abs(amount)}x"

    elif category in list_map:
        # === LISTS ===
        key = list_map[category]
        if action.value == "add":
            camps_col.update_one(
                {"_id": camp["_id"]},
                {"$addToSet": {key: value}}
            )
            msg = f"{category.capitalize()}: {value} přidáno"
        else:
            camps_col.update_one(
                {"_id": camp["_id"]},
                {"$pull": {key: value}}
            )
            msg = f"{category.capitalize()}: {value} odebráno"
    else:
        await interaction.response.send_message("❌ Neznámá kategorie.", ephemeral=True)
        return

    # ===== SEND FEEDBACK + EMBED =====
    camp = get_or_create_camp(interaction.guild.id, team_role)
    embed = build_camp_embed(camp, team_role)
    await interaction.response.send_message(msg)
    await interaction.followup.send(embed=embed)

@tabor.autocomplete("category")
async def tabor_category_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]:

    current = current.lower()

    choices = []
    for c in TABOR_CATEGORIES:
        if current in c.lower():
            emoji = TABOR_CATEGORY_EMOJIS.get(c, "❓")
            choices.append(
                app_commands.Choice(
                    name=f"{emoji} {c}",
                    value=c
                )
            )

    return choices[:25]

@tabor.autocomplete("value")
async def tabor_value_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]:

    # === získáme zadané options ===
    options = {
        opt["name"]: opt.get("value")
        for opt in interaction.data.get("options", [])
    }

    category = options.get("category")
    if not category:
        return []

    category = category.lower()

    # === zjistíme tým ===
    team_role = None
    team_id = options.get("team")

    if team_id and interaction.user.guild_permissions.administrator:
        team_role = interaction.guild.get_role(int(team_id))
    else:
        team_role = get_team_role(interaction.user)

    if not team_role:
        return []

    camp = get_or_create_camp(interaction.guild.id, team_role)

    # === AUTOCOMPLETE LOGIKA ===

    # 📦 SKLAD
    if category == "sklad":
        return [
            app_commands.Choice(name=f"📦 {i}", value=i)
            for i in camp.get("storage", [])
            if current.lower() in i.lower()
        ][:25]

    # 🏗️ VYLEPŠENÍ
    if category == "vylepšení":
        return [
            app_commands.Choice(name=f"🏗️ {u}", value=u)
            for u in camp.get("upgrades", [])
            if current.lower() in u.lower()
        ][:25]

    # 📜 BLUEPRINTS
    if category == "blueprints":
        return [
            app_commands.Choice(name=f"📜 {b}", value=b)
            for b in camp.get("blueprints", [])
            if current.lower() in b.lower()
        ][:25]

    return []