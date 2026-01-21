import discord
from typing import Optional
import random

from MongoDB import *
from utils.config import *

def roll_d20() -> int:
    return random.randint(1, 20)

async def get_guild(interaction: discord.Interaction) -> Optional[discord.Guild]:
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("❌ Tento příkaz lze použít pouze na serveru.",ephemeral=True)
        return None
    return guild

def get_or_create_user(member: discord.Member) -> dict:
    user = users_col.find_one({"user_id": member.id, "guild_id": member.guild.id})
    if not user:
        user = {
            "user_id": member.id,
            "guild_id": member.guild.id,
            "username": member.name,
            "xp": 0,
            "level": 1,
            "stats": DEFAULT_STATS.copy(),
            "inventory": []
        }
        users_col.insert_one(user)
        print(f"🆕 Vytvořen profil pro {member}")
    return user

def get_team_role(member: discord.Member) -> Optional[discord.Role]:
    for role in member.roles:
        if role.name in TEAM_ROLES:
            return role
    return None

def get_or_create_camp(guild_id: int, team_role: discord.Role) -> dict:
    camp = camps_col.find_one({
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
            "upgrades": [],
            "storage": []
        }
        camps_col.insert_one(camp)

    return camp

def build_camp_embed(camp: dict, team_role: discord.Role) -> discord.Embed:
    team_name = team_role.name
    team_emoji = TEAM_EMOJIS.get(team_name, "🏕️")
    r = camp["resources"]

    upgrades = "\n".join(f"• {u}" for u in camp["upgrades"]) or "*Žádná*"
    blueprints = "\n".join(f"• {b}" for b in camp.get("blueprints", [])) or "*Žádné*"
    storage = "\n".join(f"• {s}" for s in camp["storage"]) or "*Prázdný*"

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
    users_col.update_one(
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

def xp_bar(xp: int) -> str:
    total = 5
    chunks = 5
    per_chunk = total // chunks

    filled = xp // per_chunk
    empty = chunks - filled

    bar = "■" * filled + "□" * empty
    return f"[{bar}] {xp}/{total} XP"

async def resolve_target(interaction: discord.Interaction, member: discord.Member | None) -> Optional[discord.Member]:
    target = member or interaction.user

    if member and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Nemáš oprávnění upravovat inventář ostatních!",
            ephemeral=True
        )
        return None

    return target