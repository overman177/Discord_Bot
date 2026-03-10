import discord
from typing import Optional
import random

from MongoDB import *
from utils.config import *

def roll_d(d: int) -> int:
    return random.randint(1, d)

async def get_guild(interaction: discord.Interaction) -> Optional[discord.Guild]:
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("❌ Tento příkaz lze použít pouze na serveru.",ephemeral=True)
        return None
    return guild

def get_or_create_user(member: discord.Member) -> dict:
    user = db_users.find_one({"user_id": member.id, "guild_id": member.guild.id})
    if not user:
        user = {
            "user_id": member.id,
            "guild_id": member.guild.id,
            "nickname": member.display_name,
            "username": member.name,
            "xp": 0,
            "level": 1,
            "stats": DEFAULT_STATS.copy(),
            "inventory": []
        }
        db_users.insert_one(user)
        print(f"🆕 Vytvořen profil pro {member}")
    else:
        # aktualizace jména a přezdívky
        db_users.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "username": member.name,
                "nickname": member.display_name
            }}
        )
        user["username"] = member.name
        user["nickname"] = member.display_name
        
    return user

def get_team_role(member: discord.Member) -> Optional[discord.Role]:
    for role in member.roles:
        if role.name in TEAM_ROLES:
            return role
    return None

def get_or_create_camp(guild_id: int, team_role: discord.Role) -> dict:
    camp = db_camps.find_one({
        "guild_id": guild_id,
        "team": team_role.name
    })

    if not camp:
        camp = {
            "guild_id": guild_id,
            "team": team_role.name,
            "resources": {
                "wood": 0,
                "stone": 0,
                "scrap": 0
            },
            "upgrades": {},
            "storage": {},
            "blueprints": {}
        }
        db_camps.insert_one(camp)

    return camp

def format_dict_items(items: dict):
    if not items:
        return "*Prázdný*"

    lines = []
    for name, data in items.items():
        count = data.get("count", 1)
        desc = data.get("desc")

        line = f"• {name} ({count}x)"
        if desc and str(desc).lower() != "bsonnull":
            line += f"\n> ╰➤ _{desc}_"

        lines.append(line)

    return "\n".join(lines)

def build_camp_embed(camp: dict, team_role: discord.Role) -> discord.Embed:
    team_name = team_role.name
    team_emoji = TEAM_EMOJIS.get(team_name, "🏕️")
    r = camp["resources"]

    storage = format_dict_items(camp.get("storage", {}))
    upgrades = format_dict_items(camp.get("upgrades", {}))
    blueprints = format_dict_items(camp.get("blueprints", {}))

    embed = discord.Embed(
        title=f"----- 🏕️ Tábor týmu {team_emoji} {team_name} -----",
        color=team_role.color
    )

    # ===== Suroviny a Sklad vedle sebe =====
    resources_text = (
        f"🪵Dřevo: `{r.get('wood',0)}`\n"
        f"🪨Kámen: `{r.get('stone',0)}`\n"
        f"🔩Scrap: `{r.get('scrap',0)}`"
    )
    embed.add_field(name="**💎Suroviny**", value=resources_text, inline=True)
    embed.add_field(name="**📦Sklad**", value=storage, inline=True)
    embed.add_field(name="**🏗️Vylepšení**", value=upgrades, inline=False)
    embed.add_field(name="**📜Blueprinty**", value=blueprints, inline=False)

    return embed

def update_user(member: discord.Member, data: dict) -> None:
    db_users.update_one(
        {"user_id": member.id, "guild_id": member.guild.id},
        {"$set": data}
    )

def add_xp(member: discord.Member, amount: int) -> tuple[int, int]:
    user = get_or_create_user(member)
    xp = max(user.get("xp",0) + amount, 0)
    level = user.get("level",1) + xp // 5
    xp %= 5
    update_user(member, {"xp": xp, "level": level})
    return xp, level

async def resolve_target(interaction: discord.Interaction, member: Optional[discord.Member]) -> Optional[discord.Member]:
    # Pokud není member zadán, cílem je autor příkazu
    if member is None:
        return interaction.user
    
    # Pokud je member zadán, musím být admin, abych ho mohl ovlivnit
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Nemáš oprávnění upravovat ostatní hráče!", ephemeral=True)
        return None
        
    return member

def get_dice_image(die_type: int, number: int, Dice_Dir) -> str:
    folder = f"d{die_type}"  # např. d6
    filename = f"{number}.png"
    return os.path.join(Dice_Dir, folder, filename)