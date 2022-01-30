from discord.ext import commands
from utils.files import FileJson
from utils.new_discord import new_guild, new_member
from utils.get_member import get_member
from random import randint
import discord, asyncio, colorsys, glob

admin_cmds: list = [
    "setprefix",
    "reset"
]

class Admin(commands.Cog):
    def __init__(self, bot: discord.Client, data: FileJson):
        self.bot: discord.Client = bot
        self.data: FileJson = data

    @commands.Cog.listener()
    async def on_message(self, message):
        author: discord.Member = message.author
        guild: discord.Guild = message.guild
        channel: discord.channel = message.channel

        # On vérifie si le membre n'est pas un bot
        if author.bot: return
        # On charge la DATA
        self.data = new_guild(self.data, guild)
        self.data = new_member(self.data, guild, author)
        data_json = self.data.load()

        # On récupère dans des variables la data du membre et de la guild
        guild_data = data_json[str(guild.id)]
        prefix = guild_data["prefix"]

        message_split: list = message.content.lower().split()
        if [i for i in message_split if i[len(prefix):] in admin_cmds]:
            if author.guild_permissions.administrator:
                if message.content.lower().startswith(prefix + "setprefix"):
                    guild_data["prefix"] = message_split[1]
                    await channel.send("Le nouveau prefix est maintenant " + message_split[1])
                elif message.content.lower().startswith(prefix + "reset "):
                    member = await get_member(message, prefix + "reset", False, False,)
                    
                    if member == None:
                        await channel.send("Ce membre n'existe pas")
                    else:
                        if str(member.id) in guild_data["members"]:
                            await channel.send("Veuillez confirmer la suppression de la data de ce membre en ecrivant `confirm`")
                        
                            def check(m):
                                return m.content == "confirm" and m.author == author and m.channel == message.channel

                            try:
                                await self.bot.wait_for("message", check=check, timeout=30)
                            except asyncio.TimeoutError:
                                await channel.send("Suppression annulé")
                            else:
                                guild_data["members"].pop(str(member.id))
                                await channel.send("Ce membre a bien été reset")

                        else:
                            await channel.send("Ce membre n'existe pas dans la data de ce serveur")
            else:
                await channel.send("Tu n'as pas la permission requise (administrateur) pour utiliser cette commande")
        

        self.data.save(data_json)
