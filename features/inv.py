from features._import_ import *

@bot.tree.command(name="inv", description="Zobrazí nebo upraví inventář hráče")
@app_commands.describe(
    action="add / remove",
    item="Název itemu",
    member="Cílový hráč (jen admin)"
)
@app_commands.choices(action=ACTION_CHOICES)
async def inv(
    interaction: discord.Interaction,
    action: app_commands.Choice[str] | None = None,
    item: str | None = None,
    member: discord.Member | None = None
) -> None:
    # ===== target =====
    target = await resolve_target(interaction, member)
    if not target:
        return

    user = get_or_create_user(target)
    inventory = user.get("inventory", [])

    # ===== ZOBRAZENÍ INVENTÁŘE =====
    if action is None:
        items = "\n".join(f"• {i}" for i in inventory) or "*Prázdný*"
        embed = discord.Embed(
            title=f"----- 🎒 Inventář hráče {target.display_name} -----",
            description=items,
            color=target.color
        )
        await interaction.response.send_message(embed=embed)
        return

    # ===== ADD / REMOVE vyžaduje item =====
    if action.value in ["add", "remove"] and not item:
        await interaction.response.send_message(
            "❌ Musíš zadat název itemu, protože jsi vybral add/remove!",
            ephemeral=True
        )
        return

    msg = ""
    # ===== ADD =====
    if action.value == "add":
        inventory.append(item)
        msg = f"✅ **{item}** přidán do inventáře **{target.display_name}**"
    # ===== REMOVE =====
    elif action.value == "remove":
        if item not in inventory:
            await interaction.response.send_message(
                f"⚠️ **{item}** není v inventáři.",
                ephemeral=True
            )
            return
        inventory.remove(item)
        msg = f"🗑️ **{item}** odebrán z inventáře **{target.display_name}**"

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
    inventory = user.get("inventory", [])

    # nabídneme jen položky, které obsahují zadaný text
    return [
        app_commands.Choice(name=i, value=i)
        for i in inventory
        if current.lower() in i.lower()
    ][:50]  # max 50 položek