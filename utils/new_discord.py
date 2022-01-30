import discord
from utils.files import FileJson

base_guild = {
    "members": {},
    "react": {
        "help": {
            "id": None,
            "pos": 0
        },
        "shops": {
            "id": None,
            "pos": 0
        },
        "shops_list": {
            "id": None,
            "pos": 0
        },
        "tops": {
            "id": None,
            "pos": 0
        },
        "salary_list": {
            "id": None,
            "pos": 0
        },
        "updates": {
            "id": None,
            "pos": 0
        },
        "inv": {
            "id": None,
            "pos": 0
        }
    },
    "shops": {
        "number": 0
    },
    "level": {
        "message": "Bravo {member.mention}, tu es passé niveau {level}, et tu as gagné {coins} coins !!",
        "enable": True,
        "banned_channels": [],
        "calc": "20*({l}+1)",
        "coins_won": [20, 30]
    },
    "salarys": {
    },
    "prefix": "+"
}

base_user = {
    "xp" : 0,
    "level": 0,
    "coins": 0,
    "inv": {},
    "shops": {}
}

# On créer une data pour un serveur si il n'y est pas déjà
def new_guild(data: FileJson, guild: discord.Guild) -> FileJson:
    data_json = data.load()

    if str(guild.id) not in data_json:
        data_json[str(guild.id)] = base_guild
        data.save(data_json)

    return data

# On créer une data pour un membre si il n'y est pas déjà
def new_member(data: FileJson, guild: discord.Guild, member: discord.Member) -> FileJson:
    data_json = data.load()
    guild_data = data_json[str(guild.id)]
    
    if str(member.id) not in guild_data["members"]:
        guild_data["members"][str(member.id)] = base_user
        data.save(data_json)
    
    return data