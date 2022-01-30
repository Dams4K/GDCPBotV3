from discord.ext import commands
from utils.new_discord import new_guild, new_member
from utils.get_member import get_member
from utils.check import can_convert_to_int
from random import randint
from utils.files import FileJson
import discord

help_file = FileJson("datas/help.json", None)

class Xp(commands.Cog):
    def __init__(self, bot, data_file):
        self.bot = bot
        self.data_file = data_file
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        author = message.author
        guild: discord.Guild = message.guild
        channel = message.channel

        # On vérifie si le membre n'est pas un bot
        if author.bot: return
        # On charge la DATA
        self.data_file = new_guild(self.data_file, guild)
        self.data_file = new_member(self.data_file, guild, author)
        data = self.data_file.load()
        help_data = help_file.load()

        # On récupère dans des variables la data du membre et de la guild
        guild_data = data[str(guild.id)]
        author_data = guild_data["members"][str(author.id)]
        prefix = guild_data["prefix"]

        if message.content.lower().startswith(prefix + "xp "):
            message_split = message.content.split()
            member = None
            member_data = None
            if not author.guild_permissions.administrator:
                await channel.send("Tu n'as pas la permission d'utiliser cette commande")
                return
            
            if len(message_split) < 3:
                await channel.send("Il manque des arguments")
                return
            # Commandes pour l'édite d'xp d'un membre
            if message_split[1].lower() in ["set", "remove", "add"] and message_split[2].lower() not in ["channel"]:
                # On récup le membre à éditer
                member = await get_member(message, prefix + f"xp {message_split[1]}", error=False)

                # On lui créer un compte si il n'en a pas déjà un
                if member != None:
                    self.data_file = new_member(self.data_file, guild, member)
                    data = self.data_file.load()
                    guild_data = data[str(guild.id)]
                    member_data = guild_data["members"][str(member.id)]
                    author_data = guild_data["members"][str(author.id)]
            # Autres commandes
            else:
                if message_split[1].lower() == "set" and message_split[2].lower() == "channel":
                    if len(message_split) == 3:
                        await channel.send(f"Erreur, il manque des arguments. Rappel :\n`{prefix}xp set channel on/off`")
                    else:
                        if message_split[3].lower() in ["on", "off"]:
                            await self.switch_channel_xp(channel.id, channel, guild_data, message_split[3].lower() == "off")
                        elif message_split[4].lower() in ["on", "off"]:
                            mentionned_channel_id = message_split[3].replace("<", "").replace(">", "").replace("#", "")
                            if can_convert_to_int(mentionned_channel_id) and int(mentionned_channel_id) in guild.channels:
                                await channel.send(f"{mentionned_channel_id} n'est pas un identifiant de salon de ce serveur")
                            await self.switch_channel_xp(int(mentionned_channel_id), channel, guild_data, message_split[4].lower() == "off")

            if member != None:
                count = message_split.pop()
                if not can_convert_to_int(count):
                    await channel.send(f"`{count}` n'est pas un nombre")
                    return
                if message_split[1] == "set":
                        member_data["xp"] = int(count)
                        await channel.send(f"Le xp de {member} est maintenant à {count}")
                if message_split[1] == "add":
                        member_data["xp"] += int(count)
                        await channel.send(f"Tu as rajouté {count} xp à {member}, il/elle est maintenant à {member_data['xp']} xp")
                if message_split[1] == "remove":
                        member_data["xp"] -= int(count)
                        await channel.send(f"Tu as enlevé {count} xp à {member}, il/elle est maintenant à {member_data['xp']} xp")

        # On rajoute l'xp à la personne qui a parlé
        if guild_data["level"]["enable"] and channel.id not in guild_data["level"]["banned_channels"]:
            for a in help_data:
                for cmd in a["commands"]:
                    if message.content.lower().startswith(prefix + cmd):
                        self.data_file.save(data)
                        return
            
            len_message = len(message.content.replace(" ", ""))
            author_data["xp"] += int(len_message * 0.1)+1
            # On regarde si le joueur a toute son xp pour le niveau suivant
            # Ce bout de code n'est pas mit dans le fichier level.py, car le calcul pour le niveau suivant sera peut-être fait avant le gain d'xp. De même pour les coins
            calc_xp = eval(guild_data["level"]["calc"].format(l=author_data["level"]))

            if author_data["xp"] >= calc_xp:
                author_data["xp"] -= calc_xp
                author_data["level"] += 1
                guild_coins_won_values = guild_data["level"]["coins_won"]
                coins_won = randint(guild_coins_won_values[0], guild_coins_won_values[-1])
                author_data["coins"] += coins_won

                level_msg: str = guild_data["level"]["message"].format(
                    coins=coins_won,
                    level=author_data["level"], xp=author_data["xp"],
                    member=author
                )

                await channel.send(level_msg)

        self.data_file.save(data)
    
    async def switch_channel_xp(self, channel_id, channel, guild_data, off=None):
        banned_channels = guild_data["level"]["banned_channels"]
        if off:
            if channel_id not in banned_channels: 
                banned_channels.append(channel_id)
            await channel.send(f"L'xp a été désactivé dans le salon <#{channel_id}>")
        else:
            if channel_id in banned_channels: 
                banned_channels.remove(channel_id)
            await channel.send(f"L'xp a été activé dans le salon <#{channel_id}>")