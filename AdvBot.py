import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List

import logging
import os
import random

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from dotenv import load_dotenv

from keep_alive import keep_alive

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
url = os.getenv('MONGODB_SERVER')

keep_alive()
# ===== SEZNAMY ===========================================================================================================
STAT_EMOJIS = {
    "xp": "⭐",
    "hp": "❤️",
    "def": "🛡️",
    "mana": "🔮",
    "furioku": "🪄",
    "hunger": "🍗",
    "str": "💪",
    "dex": "🤸",
    "int": "🧠",
    "cha": "🗣️",
    "stealth": "🥷",
    "survival": "🌲",
}
CHECK_STAT_KEYS = ["str","dex","int","cha","stealth","survival"]
MAIN_STAT_KEYS = ["hp", "def", "mana", "furioku", "hunger", "xp"]
STAT_KEYS = CHECK_STAT_KEYS + MAIN_STAT_KEYS

STAT_CHOICES = [
    app_commands.Choice(name=f"{STAT_EMOJIS[key]}{key.upper()}", value=key)
    for key in STAT_KEYS
]
CHECK_STAT_CHOICES = [
    choice for choice in STAT_CHOICES if choice.value in CHECK_STAT_KEYS
]

DEFAULT_STATS = {key: 0 for key in STAT_KEYS}
DEFAULT_STATS["hp"] = 50  # default HP

STATUS_EFFECTS = {
    "bleeding": "🩸 Bleeding",
    "poisoned": "☠️ Poisoned",
    "cold": "❄️ Cold",
    "hot": "🔥 Hot",
    "concussed": "💫 Concussed",
}
STATUS_CHOICES = [
    app_commands.Choice(name=label, value=key)
    for key, label in STATUS_EFFECTS.items()
]

ACTION_CHOICES = [
    app_commands.Choice(name="➕Add", value="add"),
    app_commands.Choice(name="❌Remove", value="remove"),
]

PERK_USES_CHOICES = [
    app_commands.Choice(name="Pasivní", value="passive")
]

TEAM_EMOJIS = {
    "Unda": "🌊",
    "Ignis": "🔥",
    "Aeris": "🌪️",
    "Terra": "🌱",
}
TEAM_ROLES = ["Unda", "Ignis", "Aeris", "Terra"]
DEAD_ROLE_NAME = "Duch"

TABOR_CATEGORY_EMOJIS = {
    "dřevo": "🪵",
    "kámen": "🪨",
    "scrap": "🔩",
    "vylepšení": "🏗️",
    "sklad": "📦",
    "blueprints": "📜",
}
TABOR_CATEGORIES = ["dřevo","kámen","scrap","vylepšení","sklad","blueprints",]

# ===== DATABASE ===========================================================================================================
client = MongoClient(url, server_api=ServerApi('1'))

db = client["discord_bot"]
users_col = db["users"]
camps_col = db["camps"]

# připojení k databázi
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# ===== DISCORD =============================================================================================================
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready() -> None:
    print(f"Přihlášen jako {bot.user}")
    # Synchrinizacevslash commandu s discordem
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# ===== FUNCTIONS =============================================================================================================
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

def get_team_role(member: discord.Member):
    for role in member.roles:
        if role.name in TEAM_ROLES:
            return role
    return None

def get_or_create_camp(guild_id: int, team_role: discord.Role):
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

def add_xp(member: discord.Member, amount: int) -> tuple[int, int]:
    user = get_or_create_user(member)
    xp = user.get("xp", 0) + amount
    level = user.get("level", 1)

    if xp < 0:
        xp = 0

    # Level up
    while xp >= 5:
        xp -= 5
        level += 1

    # Uložení do DB
    users_col.update_one(
        {"user_id": member.id, "guild_id": member.guild.id},
        {"$set": {"xp": xp, "level": level}}
    )
    return xp, level

def xp_bar(xp: int) -> str:
    total = 5
    chunks = 5
    per_chunk = total // chunks

    filled = xp // per_chunk
    empty = chunks - filled

    bar = "■" * filled + "□" * empty
    return f"[{bar}] {xp}/{total} XP"

async def resolve_target(interaction: discord.Interaction, member: discord.Member | None):
    target = member or interaction.user

    if member and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Nemáš oprávnění upravovat inventář ostatních!",
            ephemeral=True
        )
        return None

    return target

# ===== COMMANDS =============================================================================================================

@bot.tree.command(name="ping", description="Kontrola odezvy bota")
async def ping(interaction: discord.Interaction) -> None:
    latency = round(bot.latency * 1000)  # v ms
    await interaction.response.send_message(f"🏓 Pong! Latence: {latency} ms")

@bot.tree.command(name="stats", description="Zobrazí nebo upraví statistiky hráče")
@app_commands.describe(
    stat="Stat který chceš změnit",
    amount="Kolik chceš přidat nebo ubrat",
    member="Cílový hráč (jen admin)"
)
@app_commands.choices(stat=STAT_CHOICES)
async def stats(
    interaction: discord.Interaction,
    stat: Optional[app_commands.Choice[str]] = None,
    amount: Optional[int] = None,
    member: Optional[discord.Member] = None
):
    # ===== TARGET =====
    target = member or interaction.user
    if member and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Nemáš oprávnění upravovat statistiky ostatních!",
            ephemeral=True
        )
        return

    guild = await get_guild(interaction)
    if not guild:
        return

    user = get_or_create_user(target)
    stats_data = user.get("stats", {})
    xp = user.get("xp", 0)
    level = user.get("level", 1)
    name = target.nick or target.name

    # 📊 JEN ZOBRAZENÍ PROFILU
    if stat is None:
        embed = discord.Embed(
            title=f"----- 📊 Profil hráče {name} -----",
            color=target.color
        )

        embed.set_thumbnail(url=target.avatar.url if target.avatar else None)

        embed.add_field(name="⭐ Level", value=level, inline=True)
        embed.add_field(name="📈 XP", value=xp_bar(xp), inline=False)

        embed.add_field(
            name="Staty",
            value=(
                f"❤️ HP: {stats_data.get('hp', 0)}\n"
                f"🛡️ DEF: {stats_data.get('def', 0)}\n"
                f"🔮 MANA: {stats_data.get('mana', 0)}\n"
                f"🪄 FURIOKU: {stats_data.get('furioku', 0)}\n"
                f"🍗 HUNGER: {stats_data.get('hunger', 0)}\n\n"
                f"💪 STR: {stats_data.get('str', 0)}\n"
                f"🤸 DEX: {stats_data.get('dex', 0)}\n"
                f"🧠 INT: {stats_data.get('int', 0)}\n"
                f"🗣️ CHA: {stats_data.get('cha', 0)}\n"
                f"🥷 STEALTH: {stats_data.get('stealth', 0)}\n"
                f"🌲 SURVIVAL: {stats_data.get('survival', 0)}"
            ),
            inline=False
        )

        embed.set_footer(text="Profil uložen v MongoDB")
        await interaction.response.send_message(embed=embed)
        return

    # ✏️ ÚPRAVA STATU
    if amount is None:
        await interaction.response.send_message(
            "❌ Pokud chceš upravit stat, musíš zadat i `amount`.",
            ephemeral=True
        )
        return

    stat_name = stat.value

    # ===== XP =====
    if stat_name == "xp":
        xp, level = add_xp(target, amount)

        embed = discord.Embed(color=target.color)
        embed.description = (
            f"⭐ XP upraveno o **{amount}**\n"
            f"XP: **{xp}/5**\n"
            f"Level: **{level}**"
        )
        embed.set_footer(text=f"Hráč: {name}", icon_url=target.avatar.url if target.avatar else None)

        await interaction.response.send_message(embed=embed)
        return

    # ===== OSTATNÍ STATY =====
    old_value = stats_data.get(stat_name, 0)
    new_value = old_value + amount
    stats_data[stat_name] = new_value

    users_col.update_one(
        {"user_id": target.id, "guild_id": guild.id},
        {"$set": {"stats": stats_data}}
    )

    embed = discord.Embed(color=target.color)
    embed.description = f"📊 **{stat.name}**: {old_value} → **{new_value}**"
    embed.set_footer(text=f"Hráč: {name}", icon_url=target.avatar.url if target.avatar else None)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="check", description="Hod D20 + bonus ze statu")
@app_commands.describe(stat="Stat na který chceš hodit check")
@app_commands.choices(stat=CHECK_STAT_CHOICES)
async def check(interaction: discord.Interaction, stat: app_commands.Choice[str]) -> None:
    member = interaction.user
    name = member.nick or member.name

    stat_name = stat.value

    # získej profil
    user = get_or_create_user(member)
    stats = user.get("stats", {})
    bonus = stats.get(stat_name, 0)

    # hod D20
    dice = roll_d20()
    total = dice + bonus

    embed = discord.Embed(title=f"🎲 {stat.name} – Check", color=member.color)

    description = (
        f"**Hod kostkou:** {dice}\n"
        f"**Bonus ({stat.name}):** {bonus}\n"
        f"**Celkem:** {total}"
    )

    # ===== NATURAL 20 =====
    if dice == 20:
        description += "\n\n🎉 **NATURAL 20!!**"
        add_xp(member, 1)
        description += "\n⭐ +1 XP a Náhodný perk"

    embed.description = description
    embed.set_footer(text=f"Hráč: {name}", icon_url=member.avatar.url if member.avatar else None)

    await interaction.response.send_message(embed=embed)

# ===== ADMIN ==================================================================================================================

@bot.tree.command(name="newday", description="Spustí nový den (hunger / HP / reset perků)")
@app_commands.checks.has_permissions(administrator=True)
async def newday(interaction: discord.Interaction):
    guild = await get_guild(interaction)
    if not guild:
        return  # příkaz nelze spustit mimo server

    for member in guild.members:
        if member.bot:
            continue

        user = get_or_create_user(member)
        stats = user.get("stats", {})
        perks_list = user.get("perks", [])

        # ===== HUNGER / HP =====
        hunger = stats.get("hunger", 0)
        hp = stats.get("hp", 100)

        if hunger >= 10:
            stats["hunger"] = hunger - 10
        else:
            stats["hunger"] = 0
            stats["hp"] = max(0, hp - 10)

        # ===== RESET AKTIVNÍCH PERKŮ =====
        for perk in perks_list:
            if perk["uses"] != "passive":
                perk["used"] = 0

        # ===== ULOŽENÍ DO DB =====
        users_col.update_one(
            {"user_id": member.id, "guild_id": guild.id},
            {"$set": {"stats": stats, "perks": perks_list}}
        )

    # ===== ZPRÁVA =====
    embed = discord.Embed(
        title="🌞 Nový den začal!",
        description="Hodnoty hunger a HP hráčů byly upraveny.\n\n🔄 Všechny aktivní perky byly resetovány.",
        color=interaction.guild.me.color
    )

    await interaction.response.send_message(embed=embed)

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

@bot.tree.command(name="players", description="Zobrazí hráče podle týmů")
async def players(interaction: discord.Interaction):

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
    await interaction.response.send_message(embed=embed)


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
):
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
    users_col.update_one(
        {"user_id": target.id, "guild_id": interaction.guild.id},
        {"$set": {"inventory": inventory}}
    )

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
):
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

        users_col.update_one(
            {"user_id": target.id, "guild_id": interaction.guild.id},
            {"$set": {"perks": perks_list}}
        )

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

        users_col.update_one(
            {"user_id": target.id, "guild_id": interaction.guild.id},
            {"$set": {"perks": perks_list}}
        )

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

        users_col.update_one(
            {"user_id": target.id, "guild_id": interaction.guild.id},
            {"$set": {"perks": perks_list}}
        )

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
):
    # ADMIN override
    if team:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Jen admin může spravovat cizí tábor.",
                ephemeral=True
            )
            return

        if team.name not in TEAM_ROLES:
            await interaction.response.send_message(
                "❌ Zvolená role není tým.",
                ephemeral=True
            )
            return

        team_role = team

    else:
        team_role = get_team_role(interaction.user)
        if not team_role:
            await interaction.response.send_message(
                "❌ Nejsi členem žádného týmu.",
                ephemeral=True
            )
            return

    camp = get_or_create_camp(interaction.guild.id, team_role)

    if not action:
        embed = build_camp_embed(camp, team_role)
        await interaction.response.send_message(embed=embed)
        return
    
    if action.value == "add":
        if not category or not value:
            await interaction.response.send_message("❌ Chybí parametr.", ephemeral=True)
            return

        if category in ["dřevo", "kámen", "scrap"]:
            key = {"dřevo": "wood", "kámen": "stone", "scrap": "scrap"}[category]

            try:
                amount = int(value)
            except ValueError:
                await interaction.response.send_message("❌ Musíš zadat číslo.", ephemeral=True)
                return

            camps_col.update_one(
                {"_id": camp["_id"]},
                {"$inc": {f"resources.{key}": amount}}
            )
            await interaction.response.send_message(f"Bylo přidáno {category} {amount}x")

        elif category.lower() == "vylepšení":
            camps_col.update_one(
                {"_id": camp["_id"]},
                {"$addToSet": {"upgrades": value}}
            )
            await interaction.response.send_message(f"Vylepšení: {value} bylo postaveno")

        elif category.lower() == "sklad":
            camps_col.update_one(
                {"_id": camp["_id"]},
                {"$addToSet": {"storage": value}}
            )
            await interaction.response.send_message(f"Do skladu bylo přidáno: {value}")

        elif category.lower() == "blueprints":
            camps_col.update_one(
                {"_id": camp["_id"]},
                {"$addToSet": {"blueprints": value}}
            )
            await interaction.response.send_message(f"Nový Blueprint nalezen: {value}")

        camp = get_or_create_camp(interaction.guild.id, team_role)
        embed = build_camp_embed(camp, team_role)

        await interaction.followup.send(embed=embed)
        return
    
    if action.value == "remove":
        if not category or not value:
            await interaction.response.send_message("❌ Chybí parametr.", ephemeral=True)
            return

        if category in ["dřevo", "kámen", "scrap"]:
            key = {"dřevo": "wood", "kámen": "stone", "scrap": "scrap"}[category]

            try:
                amount = int(value)
            except ValueError:
                await interaction.response.send_message("❌ Musíš zadat číslo.", ephemeral=True)
                return

            camps_col.update_one(
                {"_id": camp["_id"]},
                {"$inc": {f"resources.{key}": -amount}}
            )
            await interaction.response.send_message(f"Bylo odebráno {category} {amount}x")

        elif category.lower() == "vylepšení":
            camps_col.update_one(
                {"_id": camp["_id"]},
                {"$pull": {"upgrades": value}}
            )
            await interaction.response.send_message(f"Vylepšení: {value} bylo zničeno")

        elif category.lower() == "sklad":
            camps_col.update_one(
                {"_id": camp["_id"]},
                {"$pull": {"storage": value}}
            )
            await interaction.response.send_message(f"Ze skladu bylo odebráno: {value}")

        elif category.lower() == "blueprints":
            camps_col.update_one(
                {"_id": camp["_id"]},
                {"$pull": {"blueprints": value}}
            )
            await interaction.response.send_message(f"Blueprint ztracen: {value}")

        camp = get_or_create_camp(interaction.guild.id, team_role)
        embed = build_camp_embed(camp, team_role)

        await interaction.followup.send(embed=embed)
        return

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
# ===== RUN ==================================================================================================================
bot.run(token, log_handler=handler, log_level=logging.DEBUG)