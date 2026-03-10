from utils._import_ import *
from utils.config import INICIATIVE_CHOICES

@bot.tree.command(name="iniciative", description="Správa iniciativy")
@app_commands.describe(
    name="Nazev Iniciativy",
    action="Create/Finish/add/remove/eot",
    member="jmano hrace",
    creature="nazev nestvury"
)
@app_commands.choices(action=INICIATIVE_CHOICES)
async def stats(
    interaction: discord.Interaction,
    name: Optional[str] = None,
    action: Optional[app_commands.Choice[str]] = None,
    member: Optional[discord.Member] = None,
    creature: Optional[str] = None
) -> None:
    if action is None:
        initiative = db_initiative.find_one({"order": {"$elemMatch": {"type": "player", "id": interaction.user.id}}})

        if not initiative:
            await interaction.response.send_message("? Nenach�z� se v ��dn� iniciative",ephemeral=True)
            return

        embed = discord.Embed(
            title=f"---{initiative['name']}---",
            color=interaction.guild.me.color
        )

        if initiative["order"]:
            order_text = ""
            turn_idx = initiative["turn_index"]
            for idx, entry in enumerate(initiative["order"]):
                pos = idx + 1
                if entry["type"] == "player":
                    name_display = f"<@{entry['id']}>"
                else:
                    name_display = entry["name"]

                if idx == turn_idx:
                    order_text += f"**{pos}. {name_display}**\n"
                else:
                    order_text += f"-# {pos}. {name_display}\n"

            embed.description = order_text
        else:
            embed.description = "��dn� �castn�ci"

        await interaction.response.send_message(embed=embed)
        return

    if action.value == "create":

        existing = db_initiative.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
        if existing:
            await interaction.response.send_message(f"? Iniciativa **{name}** u� existuje",ephemeral=True)
            return

        initiative = {
            "name": name,
            "round": 1,
            "turn_index": 0,
            "order": [],
        }

        db_initiative.insert_one(initiative)

        embed = discord.Embed(
            title="? Iniciativa vytvorena",
            description=f"N�zev: **{name}**",
            color=interaction.guild.me.color
        )
        await interaction.response.send_message(embed=embed)
        return
    
    if action.value == "finish":
        result = db_initiative.delete_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
        
        if result.deleted_count == 0:
            await interaction.response.send_message(f"? Iniciativa **{name}** neexistuje",ephemeral=True)
            return
        
        await interaction.response.send_message(f"??? Iniciativa **{name}** byla ukoncena a smaz�na",ephemeral=True)
        return
    
    if action.value == "add":
        initiative = db_initiative.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
        if not initiative:
            await interaction.response.send_message(f"? Iniciativa **{name}** neexistuje",ephemeral=True)
            return

        if member:
            new_entry = {"type": "player", "id": member.id}
            display_name = member.mention
        elif creature:
            new_entry = {"type": "creature", "name": creature}
            display_name = creature
        else:
            await interaction.response.send_message("? Mus� zadat hr�ce nebo nestvuru",ephemeral=True)
            return

        for o in initiative["order"]:
            if (o["type"] == "player" and member and o["id"] == member.id) \
            or (o["type"] == "creature" and creature and o["name"].lower() == creature.lower()):
                await interaction.response.send_message(f"? **{display_name}** je u� v iniciative",ephemeral=True)
                return

        db_initiative.update_one(
            {"_id": initiative["_id"]},
            {"$push": {"order": new_entry}}
        )

        await interaction.response.send_message(f"? **{display_name}** prid�n/a do iniciativy **{initiative['name']}**")
        return
    
    if action.value == "remove":
        initiative = db_initiative.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
        if not initiative:
            await interaction.response.send_message(f"? Iniciativa **{name}** neexistuje",ephemeral=True)
            return

        if member:
            filter_entry = {"type": "player", "id": member.id}
            display_name = member.mention
        elif creature:
            filter_entry = {"type": "creature", "name": {"$regex": f"^{creature}$", "$options": "i"}}
            display_name = creature
        else:
            await interaction.response.send_message("? Mus� zadat hr�ce nebo nestvuru",ephemeral=True)
            return

        result = db_initiative.update_one(
            {"_id": initiative["_id"]},
            {"$pull": {"order": filter_entry}}
        )

        if result.modified_count == 0:
            await interaction.response.send_message(f"? **{display_name}** nebyl/a nalezen/a v iniciative",ephemeral=True)
            return

        await interaction.response.send_message(f"? **{display_name}** odstranen/a z iniciativy **{initiative['name']}**")
        return
    
    if action.value == "eot":
        is_admin = interaction.user.guild_permissions.administrator

        if is_admin:
            if not name:
                await interaction.response.send_message("? Admin mus� zadat n�zev iniciativy",ephemeral=True)
                return
            initiative = db_initiative.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
            if not initiative:
                await interaction.response.send_message(f"? Iniciativa **{name}** neexistuje",ephemeral=True)
                return
        else:
            initiative = db_initiative.find_one({"order": {"$elemMatch": {"type": "player", "id": interaction.user.id}}})
            if not initiative:
                await interaction.response.send_message("? Nenach�z� se ��dn� tvoje aktivn� iniciativa",ephemeral=True)
                return

            turn_idx = initiative["turn_index"]
            current = initiative["order"][turn_idx]
            if not (current["type"] == "player" and current["id"] == interaction.user.id):
                await interaction.response.send_message("? Nen� tv� kolo, nemu�e� passnout",ephemeral=True)
                return

        turn_idx = initiative["turn_index"] + 1
        if turn_idx >= len(initiative["order"]):
            turn_idx = 0
            round_num = initiative["round"] + 1
        else:
            round_num = initiative["round"]

        db_initiative.update_one(
            {"_id": initiative["_id"]},
            {"$set": {"turn_index": turn_idx, "round": round_num}}
        )

        next_entry = initiative["order"][turn_idx]
        if next_entry["type"] == "player":
            next_name = f"<@{next_entry['id']}>"
        else:
            next_name = next_entry["name"]

        await interaction.response.send_message(f"?? eot. Nyn� je na tahu: {next_name}")
        return
    return
