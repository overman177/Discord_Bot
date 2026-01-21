from features._import_ import *

@bot.tree.command(name="status", description="Přidá nebo odebere status efekt hráči")
@app_commands.describe(action="Přidat nebo odebrat status", status="Status efekt")
@app_commands.choices(action=ACTION_CHOICES, status=STATUS_CHOICES)
@app_commands.checks.has_permissions(administrator=True)
async def status(
    interaction: discord.Interaction,
    action: app_commands.Choice[str],
    status: app_commands.Choice[str],
    member: discord.Member
) -> None:
    guild = await get_guild(interaction)
    if not guild:
        return  # příkaz nelze spustit mimo server

    role_name = status.value

    # najdi roli podle jména
    role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), guild.roles)

    if not role:
        await interaction.response.send_message(f"❌ Role `{role_name}` na serveru neexistuje.", ephemeral=True)
        return

    # === ADD ===
    if action.value == "add":
        if role in member.roles:
            await interaction.response.send_message(
                f"⚠️ **{member.display_name}** is already **{STATUS_EFFECTS[role_name]}**",
                ephemeral=True
            )
            return

        await member.add_roles(role)
        await interaction.response.send_message(
            f"✅ **{member.display_name}** is now **{STATUS_EFFECTS[role_name]}**"
        )

    # === REMOVE ===
    elif action.value == "remove":
        if role not in member.roles:
            await interaction.response.send_message(
                f"⚠️ **{member.display_name}** is not **{STATUS_EFFECTS[role_name]}**",
                ephemeral=True
            )
            return

        await member.remove_roles(role)
        await interaction.response.send_message(
            f"🧹 **{member.display_name}** is no longer **{STATUS_EFFECTS[role_name]}**"
        )