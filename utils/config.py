from discord import app_commands
#==========================================================================================================================
#===== EMOJI ==============================================================================================================
#==========================================================================================================================
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

TEAM_EMOJIS = {
    "Unda": "🌊",
    "Ignis": "🔥",
    "Aeris": "🌪️",
    "Terra": "🌱",
}

TABOR_CATEGORY_EMOJIS = {
    "dřevo": "🪵",
    "kámen": "🪨",
    "scrap": "🔩",
    "vylepšení": "🏗️",
    "sklad": "📦",
    "blueprints": "📜",
}
#==========================================================================================================================
#===== SEZNAMY ============================================================================================================
#==========================================================================================================================
CHECK_STAT_KEYS = ["str","dex","int","cha","stealth","survival"]
MAIN_STAT_KEYS = ["hp", "def", "mana", "furioku", "hunger", "xp"]
STAT_KEYS = CHECK_STAT_KEYS + MAIN_STAT_KEYS
DEFAULT_STATS = {key: 0 for key in STAT_KEYS}
DEFAULT_STATS["hp"] = 50  # default HP


TABOR_CATEGORIES = ["dřevo","kámen","scrap","vylepšení","sklad","blueprints",]
CATEGORY_MAP = {
    "dřevo": ("resources.wood", int),
    "kámen": ("resources.stone", int),
    "scrap": ("resources.scrap", int),
    "vylepšení": ("upgrades", str),
    "sklad": ("storage", str),
    "blueprints": ("blueprints", str)
}

TEAM_ROLES = ["Unda", "Ignis", "Aeris", "Terra"]
DEAD_ROLE_NAME = "Duch"

SYMBOLS = ["🍒", "🍋", "🔔", "💎", "⭐"]

STATUS_EFFECTS = {
    "bleeding": "🩸 Bleeding",
    "poisoned": "☠️ Poisoned",
    "cold": "❄️ Cold",
    "hot": "🔥 Hot",
    "concussed": "💫 Concussed",
}
#==========================================================================================================================
#===== Choices ============================================================================================================
#==========================================================================================================================
STAT_CHOICES = [
    app_commands.Choice(name=f"{STAT_EMOJIS[key]}{key.upper()}", value=key)
    for key in STAT_KEYS
]

CHECK_STAT_CHOICES = [
    choice for choice in STAT_CHOICES if choice.value in CHECK_STAT_KEYS
]

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