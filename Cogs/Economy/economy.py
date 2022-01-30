from discord.ext import commands
from utils.files import FileJson
from utils.new_discord import new_guild, new_member
from utils.get_member import get_member
from utils.check import can_convert_to_int
import discord

class Economy(commands.Cog):
    def __init__(self, bot: discord.Client, data_file: FileJson) -> None:
        self.bot = bot
        self.data_file = data_file
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        author = message.author
        guild = message.guild
        channel = message.channel

        # On vérifie si le membre n'est pas un bot
        if author.bot: return
        # On charge la DATA
        self.data_file = new_guild(self.data_file, guild)
        self.data_file = new_member(self.data_file, guild, author)
        data = self.data_file.load()

        # On récupère dans des variables la data du membre et de la guild
        guild_data = data[str(guild.id)]
        prefix = guild_data["prefix"]

        if message.content.lower().startswith(prefix + "lustres"):
            message_split = message.content.lower().split()
            member = None
            member_data = None

            # Commandes pour l'édite de level d'un membre
            if message_split[1].lower() in ["set", "remove", "add"]:
                if not author.guild_permissions.administrator:
                    await channel.send("Tu n'as pas la permission d'utiliser cette commande")
                    return
                member = await get_member(message, prefix + f"lustres {message_split[1]}", error=True)

                if member != None:
                    self.data_file = new_member(self.data_file, guild, member)
                    data = self.data_file.load()
                    guild_data = data[str(guild.id)]
                    member_data = guild_data["members"][str(member.id)]
                else:
                    return
            
            count = message_split.pop()
            if not can_convert_to_int(count):
                await channel.send(f"`{count}` n'est pas un nombre")
                return
            if message_split[1] == "set":
                    member_data["coins"] = int(count)
                    await channel.send(f"Le nombre lustres de {member} est maintenant à {count}")
            if message_split[1] == "add":
                    member_data["coins"] += int(count)
                    await channel.send(f"Tu as rajouté {count} lustres à {member}, qui a maintenant {member_data['coins']} lustres")
            if message_split[1] == "remove":
                    member_data["coins"] -= int(count)
                    await channel.send(f"Tu as enlevé {count} lustres à {member}, qui a maintenant {member_data['coins']} lustres")
            
        self.data_file.save(data)