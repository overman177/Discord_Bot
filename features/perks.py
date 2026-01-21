from features._import_ import *

@bot.tree.command(name="perks", description="Správa perků hráče")
@app_commands.describe(
    member="Cílový hráč (jen admin)",
    action="Akce (add / remove / use)",
    name="Název perku",
    description="Popis perku",
    uses="Počet použití za den nebo 'passive'"
)
@app_commands.choices(action=ACTION_CHOICES + [app_commands.Choice(name="⚡Use", value="use")])
async def perks(
    interaction: discord.Interaction,
    member: Optional[discord.Member] = None,
    action: Optional[app_commands.Choice[str]] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    uses: Optional[str] = None
) -> None:
    # ===== RESOLVE TARGET =====
    target = await resolve_target(interaction, member)
    if not target:
        return

    user = get_or_create_user(target)
    perks_list = user.get("perks", [])

    # ===== ZOBRAZENÍ (action=None) =====
    if not action:
        if not perks_list:
            description_text = "*Žádné perky*"
        else:
            passive = []
            active = []

            for p in perks_list:
                if p["uses"] == "passive":
                    passive.append(f"**{p['name']}** = {p['description']}")
                else:
                    total = int(p["uses"])
                    used = p.get("used", 0)
                    filled = "🟢" * (total - used)
                    empty = "🔴" * used
                    circles = "|".join(list(filled + empty))
                    active.append(f"**{p['name']}** ({circles}) = {p['description']}")

            description_text = ""
            if passive:
                description_text += "**♾️ Pasivní perky:**\n" + "\n".join(passive) + "\n\n"
            if active:
                description_text += "**🍄 Aktivní perky:**\n" + "\n".join(active)

        embed = discord.Embed(
            title=f"----- ✨ Perky hráče {target.display_name} -----",
            description=description_text,
            color=target.color
        )
        await interaction.response.send_message(embed=embed)  # viditelné všem
        return

    # ===== ADD =====
    if action.value == "add":
        if not all([name, description, uses]):
            await interaction.response.send_message(
                "❌ Pro přidání perku musíš zadat `name`, `description` a `uses`.",
                ephemeral=True
            )
            return

        if uses.lower() == "passive":
            uses_value = "passive"
        else:
            try:
                uses_value = int(uses)
                if uses_value <= 0:
                    raise ValueError
            except ValueError:
                await interaction.response.send_message(
                    "❌ `uses` musí být číslo větší než 0 nebo 'passive'.",
                    ephemeral=True
                )
                return

        perk = {"name": name, "description": description, "uses": uses_value, "used": 0}
        perks_list.append(perk)

        update_user(target, {"perks": perks_list})

        await interaction.response.send_message(
            f"✅ Perk **{name}** přidán hráči **{target.display_name}**"
        )
        return

    # ===== REMOVE =====
    elif action.value == "remove":
        if not name:
            await interaction.response.send_message(
                "❌ Pro odstranění perku musíš zadat `name`.",
                ephemeral=True
            )
            return

        perk_to_remove = next((p for p in perks_list if p["name"] == name), None)
        if not perk_to_remove:
            await interaction.response.send_message(
                f"⚠️ Perk **{name}** nenalezen u hráče **{target.display_name}**.",
                ephemeral=True
            )
            return

        perks_list.remove(perk_to_remove)

        update_user(target, {"perks": perks_list})

        await interaction.response.send_message(
            f"🗑️ Perk **{name}** odstraněn hráči **{target.display_name}**"
        )
        return

    # ===== USE =====
    elif action.value == "use":
        if not name:
            await interaction.response.send_message(
                "❌ Pro použití perku musíš zadat `name`.",
                ephemeral=True
            )
            return

        perk_to_use = next((p for p in perks_list if p["name"] == name), None)
        if not perk_to_use:
            await interaction.response.send_message(
                f"⚠️ Perk **{name}** nenalezen u hráče **{target.display_name}**.",
                ephemeral=True
            )
            return

        # ===== pasivní perk - jen oznámíme použití, neubíráme žádné použití =====
        if perk_to_use["uses"] == "passive":
            await interaction.response.send_message(
                f"⚡ **{target.display_name}** použil pasivní perk **{name}**."
            )
            return

        # ===== aktivní perk =====
        if perk_to_use.get("used", 0) >= perk_to_use["uses"]:
            await interaction.response.send_message(
                f"⚠️ Perk **{name}** nemá více použití dnes.",
                ephemeral=True
            )
            return

        perk_to_use["used"] = perk_to_use.get("used", 0) + 1

        update_user(target, {"perks": perks_list})

        await interaction.response.send_message(
            f"⚡ **{target.display_name}** použil aktivní perk **{name}**."
        )
        return
# ===== Autocomplete pro perk =====
@perks.autocomplete("name")
async def perks_name_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    # získáme volané options z autocomplete requestu
    options = {opt["name"]: opt.get("value") for opt in interaction.data.get("options", [])}
    
    action_value = options.get("action")
    if not action_value or action_value not in ["remove", "use"]:
        return []

    member_id = options.get("member")
    target = None
    if member_id:
        # pokud admin vybral člena
        target = interaction.guild.get_member(int(member_id))
    else:
        target = interaction.user

    if not target:
        return []

    user = get_or_create_user(target)
    perks_list = user.get("perks", [])

    return [
        app_commands.Choice(name=p["name"], value=p["name"])
        for p in perks_list
        if current.lower() in p["name"].lower()
    ][:50]