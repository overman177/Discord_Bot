# Discord Bot

Discord bot pro správu hráčských statistik, inventáře, perků, táborů, iniciativy a kostkových hodů.

## Požadavky

- Python 3.11+
- MongoDB databáze
- Discord bot token

## Nastavení

1. Vytvoř `.env` podle `.env.example`.
2. Nainstaluj závislosti:
   `pip install -r requirements.txt`
3. Spusť bota:
   `python main.py`

## Prostředí

- `DISCORD_TOKEN` - token Discord bota
- `MONGODB_SERVER` - MongoDB connection string

## Hlavní slash příkazy

- `/ping` - ověření odezvy bota
- `/players` - přehled hráčů v týmech
- `/roll` - hod kostkami podle vzorce
- `/check` - d20 check se stat bonusy
- `/stats` - profil a úprava statistik
- `/inv` - inventář hráče
- `/perks` - správa perků
- `/tabor` - týmový tábor
- `/iniciative` - iniciativa v boji
- `/status` - status efekty pro admina
- `/newday` - nový den pro admina

## Poznámky

- Týmové příkazy očekávají role `Unda`, `Ignis`, `Aeris`, `Terra`.
- Přehled mrtvých hráčů používá roli `Duch`.
- Status příkaz pracuje s rolemi `bleeding`, `poisoned`, `cold`, `hot`, `concussed`.
- Lze jednoduše přidat další do listu nebo změnit názvy v `config.py`.
