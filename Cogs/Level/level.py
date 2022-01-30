from discord.ext import commands
from utils.new_discord import new_guild, new_member
from utils.get_member import get_member
from utils.check import can_convert_to_int
import discord

class Level(commands.Cog):
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        author = message.author
        guild = message.guild
        channel = message.channel

        # On vérifie si le membre n'est pas un bot
        if author.bot: return
        # On charge la DATA
        self.data = new_guild(self.data, guild)
        self.data = new_member(self.data, guild, author)
        data_json = self.data.load()

        # On récupère dans des variables la data du membre et de la guild
        guild_data = data_json[str(guild.id)]
        prefix = guild_data["prefix"]

        if message.content.lower().startswith(prefix + "level "):
            message_split = message.content.lower().split()
            member = None
            member_data = None

            if len(message_split) > 2:
                # Commandes pour l'édite de level d'un membre
                if message_split[1].lower() in ["set", "remove", "add"]:
                    if not author.guild_permissions.administrator:
                        await channel.send("Tu n'as pas la permission d'utiliser cette commande")
                        return
                    member = await get_member(message, prefix + f"level {message.content.split()[1]}", error=True)
                    
                    if member != None:
                        self.data = new_member(self.data, guild, member)
                        data_json = self.data.load()
                        guild_data = data_json[str(guild.id)]
                        member_data = guild_data["members"][str(member.id)]
                        
                        count = message_split.pop()
                        if not can_convert_to_int(count):
                            await channel.send(f"`{count}` n'est pas un nombre")
                            return
                        if message_split[1] == "set":
                                member_data["level"] = int(count)
                                await channel.send(f"Le level de {member} est maintenant à {count}")
                        if message_split[1] == "add":
                                member_data["level"] += int(count)
                                await channel.send(f"Tu as rajouté {count} level à {member}, il/elle est maintenant à {member_data['level']} level")
                        if message_split[1] == "remove":
                                member_data["level"] -= int(count)
                                await channel.send(f"Tu as enlevé {count} level à {member}, il/elle est maintenant à {member_data['level']} level")

                    if message_split[1] == "set":
                        # Commande pour la modif du message de gain de niveau
                        if message_split[2].lower() == "message":
                            guild_data["level"]["message"] = " ".join(message_split[3:])
                            await channel.send(f"À chaque niveau passé, le message envoyé sera celui la : \n`{' '.join(message_split[3:])}`")
                        elif message_split[2].lower() == "calc":
                            pass

            else:
                if message_split[1].lower() in ["enable", "disable", "on", "off"]:
                    if message_split[1].lower() in ["enable", "on"]:
                        guild_data["level"]["enable"] = True
                        await channel.send("Le système de level est maintenant activé")
                    else:
                        guild_data["level"]["enable"] = False
                        await channel.send("Le système de level est maintent désactivé")

        self.data.save(data_json)