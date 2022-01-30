from discord.ext import commands
from utils.files import FileJson
import discord
import os
import asyncio
import sys
import time
import gzip

#--- Cog ---#
from Cogs.Level.xp import Xp
from Cogs.Level.level import Level
from Cogs.everyone import Everyone
from Cogs.help import Help
from Cogs.Economy.economy import Economy
from Cogs.Economy.shops import Shops
from Cogs.admin import Admin
from Cogs.tops import Tops
from Cogs.owner import Owner
from Cogs.salary import Salary
from Cogs.stats import Stats
from Cogs.update import Update

token = FileJson("datas/token.json", {}).load()
bot_info = FileJson("datas/bot_info.json", {}).load()
data = FileJson("datas/data.json", {})
data_file = "datas/data.json"

intents = discord.Intents.all()
""" 
Préfix aussi lont pour pas que le bot me dise tout le temps dans la console "Ignoring exception in command None: 
discord.ext.commands.errors.CommandNotFound: Command "setxp" is not found"
"""
bot = commands.Bot(command_prefix="---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------", intents=intents)

@bot.event
async def on_ready():
    global bot_info

    activity = discord.Activity(type=discord.ActivityType.playing, name="+help pour voir la page d'aide")
    
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    bot.loop.create_task(loop())

    os.system("clear")
    print("#------------------------------------#")
    print(f"|  {bot.user} vient de demarrer  |")
    print(f"|  Version actuelle : v{bot_info['version']}         |")
    print("#------------------------------------#")
    


async def loop():
    global data
    await bot.wait_until_ready()
    while True:
        day = time.strftime("%A")
        hours = int(time.strftime("%H"))

        if day == "Monday" and hours == 8:
            data = await bot.get_cog("Salary").give_salary(data)
            await bot.get_cog("Stats").reset_stats()
            await compile_data()

            await asyncio.sleep(3600*24*3) # On attend 3 jours
        
        await asyncio.sleep(10) # On attend 10 secondes


async def compile_data():
    file_name = time.strftime("datas/backup/Data_%d-%m-%Y.zip")
    config_file = open(data_file, "rb")
    data = config_file.read()
    bindata = bytearray(data)

    if not os.path.exists(file_name):
        with gzip.open(file_name, "wb") as f:
            f.write(bindata)
    config_file.close()

bot.add_cog(Xp(bot, data))
bot.add_cog(Level(bot, data))
bot.add_cog(Everyone(bot, bot_info, data))
bot.add_cog(Help(bot, data))
bot.add_cog(Economy(bot, data))
bot.add_cog(Shops(bot, data))
bot.add_cog(Admin(bot, data))
bot.add_cog(Tops(bot, data))
bot.add_cog(Owner(bot, data))
bot.add_cog(Salary(bot, data))
bot.add_cog(Stats(bot, data))
bot.add_cog(Update(bot, data))

bot.run(token["token"])
