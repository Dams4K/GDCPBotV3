from discord.ext import commands
from utils.files import FileJson
from utils.new_discord import new_guild, new_member
from utils.get_member import get_member
from utils.check import can_convert_to_int
import discord, asyncio

class Owner(commands.Cog):
    def __init__(self, bot: discord.Client, data_file: FileJson) -> None:
        self.bot = bot
        self.data_file = data_file
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        author: discord.Member = message.author
        guild: discord.Guild = message.guild
        channel: discord.channel = message.channel

        # On vérifie si le membre n'est pas un bot
        if author.bot: return
        # On charge la DATA
        self.data_file = new_guild(self.data_file, guild)
        self.data_file = new_member(self.data_file, guild, author)
        data = self.data_file.load()

        # On récupère dans des variables la data du membre et de la guild
        guild_data = data[str(guild.id)]
        prefix = guild_data["prefix"]
        message_split = message.content.split()

        # if message.content.lower().startswith(prefix + "reset "):
        #     if guild.owner_id != author.id:
        #         await channel.send("Tu dois être l'owner de ce serveur pour pouvoir utiliser cette commande")
        #         return
                
        #     member = await get_member(message, prefix + "reset", False, False,)

        #     if member == None:
        #         await channel.send("Ce membre n'existe pas")
        #     else:
        #         if str(member.id) in guild_data["members"]:
        #             await channel.send("Veuillez confirmer la suppression de la data de ce membre en ecrivant `confirm`")
                
        #             def check(m):
        #                 return m.content == "confirm" and m.author == author and m.channel == message.channel

        #             try:
        #                 await self.bot.wait_for("message", check=check, timeout=30)
        #             except asyncio.TimeoutError:
        #                 await channel.send("Suppression annulé")
        #             else:
        #                 guild_data["members"].pop(str(member.id))
        #                 await channel.send("Ce joueur a bien été reset")

        #         else:
        #             await channel.send("Ce joueur n'existe pas dans la data de ce serveur")
    
        self.data_file.save(data)