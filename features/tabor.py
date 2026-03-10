from utils._import_ import *

@bot.tree.command(name="tabor", description="Zobrazí nebo spravuje tábor týmu")
@app_commands.describe(
    action="add / remove",
    category="kategorie tábora",
    item="Název položky",
    amount="Počet",
    desc="Popis položky",
    team="Tým (jen admin)"
)
@app_commands.choices(action=ACTION_CHOICES)
async def tabor(
    interaction: discord.Interaction,
    action: Optional[app_commands.Choice[str]] = None,
    category: Optional[str] = None,
    item: str | None = None,
    amount: int | None = None,
    desc: str | None = None,
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
        if amount is None:
            await interaction.response.send_message(
                "❌ Musíš zadat počet.",
                ephemeral=True
            )
            return

        if amount <= 0:
            await interaction.response.send_message(
                "❌ Počet musí být větší než 0.",
                ephemeral=True
            )
            return

        op = 1 if action.value == "add" else -1

        db_camps.update_one(
            {"_id": camp["_id"]},
            {"$inc": {f"resources.{resource_map[category]}": amount * op}}
        )

        msg = f"{'Přidáno' if op > 0 else 'Odebráno'} {category} {amount}x"

    elif category in list_map:
        if not item:
            await interaction.response.send_message(
                "❌ Musíš zadat název položky.",
                ephemeral=True
            )
            return

        amount = amount or 1
        if amount <= 0:
            await interaction.response.send_message(
                "❌ Počet musí být větší než 0.",
                ephemeral=True
            )
            return

        key = list_map[category]
        camp_items = camp.get(key, {})

        msg = ""

        # ===== ADD =====
        if action.value == "add":

            if item not in camp_items:
                db_camps.update_one(
                    {"_id": camp["_id"]},
                    {
                        "$set": {
                            f"{key}.{item}": {
                                "count": amount,
                                "desc": desc
                            }
                        }
                    }
                )
                total = amount
            else:
                db_camps.update_one(
                    {"_id": camp["_id"]},
                    {
                        "$inc": {f"{key}.{item}.count": amount}
                    }
                )

                if desc:
                    db_camps.update_one(
                        {"_id": camp["_id"]},
                        {"$set": {f"{key}.{item}.desc": desc}}
                    )

                total = camp_items[item]["count"] + amount

            msg = f"✅ **{item}** přidáno ×{amount} (celkem {total}×)"

        # ===== REMOVE =====
        elif action.value == "remove":

            if item not in camp_items:
                await interaction.response.send_message(
                    f"⚠️ **{item}** není v této kategorii.",
                    ephemeral=True
                )
                return

            if amount > camp_items[item]["count"]:
                await interaction.response.send_message(
                    f"⚠️ Nemůžeš odebrat {amount}×, "
                    f"tábor má jen {camp_items[item]['count']}×.",
                    ephemeral=True
                )
                return

            new_count = camp_items[item]["count"] - amount

            if new_count <= 0:
                db_camps.update_one(
                    {"_id": camp["_id"]},
                    {"$unset": {f"{key}.{item}": ""}}
                )
                msg = f"🗑️ **{item}** zcela odebrán"
            else:
                db_camps.update_one(
                    {"_id": camp["_id"]},
                    {"$inc": {f"{key}.{item}.count": -amount}}
                )
                msg = f"➖ **{item}** odebráno ×{amount} (zbývá {new_count}×)"
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

@tabor.autocomplete("item")
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
            app_commands.Choice(name=f"📦 {name} ({data.get('count',1)}x)",value=name)
            for name, data in camp.get("storage", {}).items()
            if current.lower() in name.lower()
        ][:25]

    # 🏗️ VYLEPŠENÍ    
    if category == "vylepšení":
        return [
            app_commands.Choice(name=f"🏗️ {name} ({data.get('count',1)}x)",value=name)
            for name, data in camp.get("upgrades", {}).items()
            if current.lower() in name.lower()
        ][:25]

    # 📜 BLUEPRINTS
    if category == "blueprints":
        return [
            app_commands.Choice(name=f"📜 {name} ({data.get('count',1)}x)",value=name)
            for name, data in camp.get("blueprints", {}).items()
            if current.lower() in name.lower()
        ][:25]
    

    return []