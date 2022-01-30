# a juste servi pour traduire la data de la version 2.0 à la version 3.0
from re import L

from discord.ext.commands.core import cooldown
from utils.files import FileJson

last_data_file = FileJson("last_data.json", {})
new_data_file = FileJson("new_data.json", {})
last_data = last_data_file.load()
new_data = {}

for guild_id in last_data:
    new_data[guild_id] = {
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
            "inv" : {
                "id": None,
                "pos": 0
            }
        },
        "shops": {
            "number": last_data[guild_id]["shops"]["counter"]
        },
        "level": {
            "message": last_data[guild_id]["new_level"].replace("user", "member"),
            "enable": last_data[guild_id]["level"] == "on",
            "banned_channels": last_data[guild_id]["none_xp"]["channels"],
            "calc": "15*({l}+1)",
            "coins_won": [20, 30]
        },
        "salarys": {},
        "prefix": last_data[guild_id]["prefix"]
    }

    for shop in last_data[guild_id]["shops"]:
        if shop == "counter": continue
        
        shop_name = last_data[guild_id]["shops"][shop]["name"]
        shop_desc = last_data[guild_id]["shops"][shop]["description"]
        shop_price = last_data[guild_id]["shops"][shop]["price"]
        shop_cooldown = str(last_data[guild_id]["shops"][shop]["cooldown"])
        if last_data[guild_id]["shops"][shop]["type"] == None:
            shop_article_type = None
            shop_article_name = None
        else:
            shop_article_type = last_data[guild_id]["shops"][shop]["type"][0]
            shop_article_name = last_data[guild_id]["shops"][shop]["type"][1]


        if shop_desc == None:
            shop_desc = ""

        new_data[guild_id]["shops"][shop] = {
            "name": shop_name,
            "desc": shop_desc,
            "price": shop_price,
            "object": {
                "type": shop_article_type,
                "name": shop_article_name
            },
            "cooldown": shop_cooldown
        }
    
    for member in last_data[guild_id]["members"]:
        new_data[guild_id]["members"][member] = {
            "xp": last_data[guild_id]["members"][member]["xp"],
            "level": last_data[guild_id]["members"][member]["level"],
            "coins": last_data[guild_id]["members"][member]["coins"],
            "inv": last_data[guild_id]["members"][member]["inventory"],
            "shops": {}
        }

new_data_file.save(new_data)
