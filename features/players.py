from utils._import_ import *

@bot.tree.command(name="players", description="Zobrazí hráče podle týmů")
async def players(interaction: discord.Interaction) -> None:

    guild = interaction.guild
    if not guild:
        return

    dead_role = discord.utils.get(guild.roles, name=DEAD_ROLE_NAME)
    if not dead_role:
        await interaction.response.send_message(
            "❌ DEAD role neexistuje.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="----------👥 Hráči v týmech ----------",
        color=interaction.guild.me.color
    )

    # === TÝMY – JEN ŽIVÍ ===
    for team_name, emoji in TEAM_EMOJIS.items():
        team_role = discord.utils.get(guild.roles, name=team_name)

        if not team_role:
            embed.add_field(
                name=f"{emoji} {team_name}",
                value="❌ Role neexistuje",
                inline=True
            )
            continue

        alive_players = [
            m.display_name
            for m in team_role.members
            if dead_role not in m.roles
        ]

        embed.add_field(
            name=f"{emoji} {team_name}",
            value="\n".join(alive_players) if alive_players else "—",
            inline=True
        )
    
    ghosts = [
        m.display_name
        for m in guild.members
        if dead_role in m.roles and not m.bot
    ]

    embed.add_field(
        name="👻 Duchové",
        value="\n".join(ghosts) if ghosts else "—",
        inline=True
    )
    
    await interaction.response.send_message(embed=embed)