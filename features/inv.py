from utils._import_ import *

@bot.tree.command(name="inv", description="Zobrazí nebo upraví inventář hráče")
@app_commands.describe(
    action="add / remove",
    item="Název itemu",
    desc="Popis itemu",
    amount="počet",
    member="Cílový hráč (jen admin)"
)
@app_commands.choices(action=ACTION_CHOICES)
async def inv(
    interaction: discord.Interaction,
    action: app_commands.Choice[str] | None = None,
    item: str | None = None,
    desc: str | None = None,
    amount: int | None = None,
    member: discord.Member | None = None
) -> None:
    # ===== target =====
    target = await resolve_target(interaction, member)
    if not target:
        return

    user = get_or_create_user(target)

    # ===== INVENTÁŘ (FULL BACKWARD COMPATIBILITY) =====
    raw_inventory = user.get("inventory", {})

    inventory: dict[str, dict] = {}

    # starý list
    if isinstance(raw_inventory, list):
        for i in raw_inventory:
            inventory[i] = {
                "count": inventory.get(i, {}).get("count", 0) + 1,
                "desc": None
            }

    # dict[str, int]
    elif raw_inventory and isinstance(next(iter(raw_inventory.values())), int):
        for name, count in raw_inventory.items():
            inventory[name] = {"count": count, "desc": None}

    # nový formát
    else:
        inventory = raw_inventory.copy()

    # ===== ZOBRAZENÍ INVENTÁŘE =====
    if action is None:
        if not inventory:
            items = "*Prázdný*"
        else:
            lines = []
            for name, data in inventory.items():
                line = f"• **{name}**"
                if data["count"] > 1:
                    line += f" ×{data['count']}"
                if data.get("desc"):
                    line += f"\n  _{data['desc']}_"
                lines.append(line)

            items = "\n".join(lines)

        embed = discord.Embed(
            title=f"----- 🎒 Inventář hráče {target.display_name} -----",
            description=items,
            color=target.color
        )
        await interaction.response.send_message(embed=embed)
        return

    # ===== ADD / REMOVE vyžaduje item =====
    if action.value in ("add", "remove") and not item:
        await interaction.response.send_message("❌ Musíš zadat název itemu.",ephemeral=True)
        return

    # ===== AMOUNT =====
    amount = amount or 1
    if amount <= 0:
        await interaction.response.send_message("❌ Počet musí být větší než 0.",ephemeral=True)
        return
    
    msg = ""
    # ===== ADD =====
    if action.value == "add":
        if item not in inventory:
            inventory[item] = {"count": 0, "desc": desc}

        inventory[item]["count"] += amount

        # desc se nastaví / přepíše jen pokud je zadán
        if desc:
            inventory[item]["desc"] = desc

        msg = (f"✅ **{item}** přidán ×{amount} "
               f"(**celkem {inventory[item]['count']}×**) hráči **{target.display_name}**")
    # ===== REMOVE =====
    elif action.value == "remove":
        if item not in inventory:
            await interaction.response.send_message(
                f"⚠️ **{item}** není v inventáři.",
                ephemeral=True
            )
            return

        if amount > inventory[item]["count"]:
            await interaction.response.send_message(
                f"⚠️ Nemůžeš odebrat {amount}× **{item}**, "
                f"hráč má jen {inventory[item]['count']}×.",
                ephemeral=True
            )
            return

        inventory[item]["count"] -= amount

        if inventory[item]["count"] <= 0:
            del inventory[item]
            msg = f"🗑️ **{item}** zcela odebrán z inventáře **{target.display_name}**"
        else:
            msg = (
                f"➖ **{item}** odebrán ×{amount} "
                f"(**zbývá {inventory[item]['count']}×**) u **{target.display_name}**"
            )

    # ===== Uložení do DB =====
    update_user(target, {"inventory": inventory})

    # ===== Embed =====
    embed = discord.Embed(description=msg, color=target.color)
    await interaction.response.send_message(embed=embed)


# ===== Autocomplete pro item =====
@inv.autocomplete("item")
async def inv_item_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    target = await resolve_target(interaction, getattr(interaction.namespace, "member", None))
    if not target:
        return []

    user = get_or_create_user(target)
    raw_inventory = user.get("inventory", [])

    if isinstance(raw_inventory, list):
        items = set(raw_inventory)
    elif raw_inventory and isinstance(next(iter(raw_inventory.values())), int):
        items = raw_inventory.keys()
    else:
        items = raw_inventory.keys()

    return [
        app_commands.Choice(name=name, value=name)
        for name in items
        if current.lower() in name.lower()
    ][:50]