from discord.ext import commands
from discord.utils import get
from utils.new_discord import new_guild, new_member
from utils.get_member import get_member
from utils.check import can_convert_to_int
from random import randint
from utils.files import FileJson
import discord
import asyncio
import time

class Salary(commands.Cog):
    def __init__(self, bot, data_file):
        self.bot: discord.Client = bot
        self.data_file = data_file
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        # On récupère les id
        message_id = payload.message_id
        guild_id = str(payload.guild_id)
        channel_id = str(payload.channel_id)
        # On récupère les objects
        guild: discord.Guild = self.bot.get_guild(int(guild_id))
        channel: discord.channel = guild.get_channel(int(channel_id))
        message: discord.Message = await channel.fetch_message(str(payload.message_id))
        emoji: discord.Emoji = payload.emoji
        member: discord.Member = payload.member
        # On charge la data
        self.data_file = new_guild(self.data_file, guild)
        data = self.data_file.load()
        guild_data = data[str(payload.guild_id)]
        if member.bot:
            return

        if message_id == guild_data["react"]["salary_list"]["id"]:
            await message.remove_reaction(emoji, member)
            pos = guild_data["react"]["salary_list"]["pos"]
            calc = "+"
            if emoji.name == "⬅️":
                calc = "-"
            elif emoji.name == "🔄":
                calc = "+1-"

            salarys_list: list = int(len(guild_data["salarys"])/10)+1
            new_pos = eval(f"{pos}{calc}1")
            
            if new_pos >= salarys_list:
                new_pos = 0
            elif new_pos < 0:
                new_pos = salarys_list-1

            guild_data["react"]["salary_list"]["pos"] = new_pos

            await message.edit(embed=SalarysListEmbed(guild, guild_data, new_pos))

        self.data_file.save(data)


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
        guild_data: dict = data[str(guild.id)]
        author_data: dict = guild_data["members"][str(author.id)]
        prefix: str = guild_data["prefix"]
        message_split = message.content.lower().split()

        if message.content.lower().startswith(prefix + "salary "):
            if message_split[1] in ["add", "remove", "set"]:
                if not author.guild_permissions.administrator:
                    await channel.send("Tu n'as pas la permission d'utiliser cette commande")
                    return
                if message_split[1] == "add":
                    if len(message_split) >= 4:
                        role_id = " ".join(message_split[2:-1]).replace("<", "").replace(">", "").replace("@", "").replace("&", "")
                        salary: int = message_split[-1]
                        if not can_convert_to_int(role_id):
                            role_name = role_id
                            for role in guild.roles:
                                if role.name == role_name:
                                    role_id = role.id
                            if not can_convert_to_int(role_id):
                                await channel.send("Ce role n'existe pas")
                                return
                        elif int(role_id) not in [i.id for i in guild.roles]:
                            await channel.send("Ce role n'existe pas")
                            return
                        if not can_convert_to_int(salary):
                            await channel.send("Tu dois mettre un nombre pour le salaire")
                            return
                        role_id = int(role_id)
                        salary = int(salary)

                        guild_data["salarys"].setdefault(str(salary), [])
                        if str(role_id) in guild_data["salarys"][str(salary)]:
                            await channel.send("Ce role à déjà un salaire qui lui est attribué, pour changer son salaire, utilise la command `salary set` et pour le supprimer utilise la command `salary remove`")
                        else:
                            guild_data["salarys"][str(salary)].append(str(role_id))
                            await channel.send(f"Chaque personne qui a le role {get(guild.roles, id=role_id).name} gagne maintenant {salary} coins tout les lundi 8h")
                        
                        
                elif message_split[1] == "remove":
                    if len(message_split) >= 3:
                        role_id = " ".join(message_split[2:]).replace("<", "").replace(">", "").replace("@", "").replace("&", "")
                        
                        if not can_convert_to_int(role_id):
                            role_name = role_id
                            for role in guild.roles:
                                if role.name == role_name:
                                    role_id = role.id
                            if not can_convert_to_int(role_id):
                                await channel.send("Ce role n'existe pas")
                                return
                        elif int(role_id) not in [i.id for i in guild.roles]:
                            await channel.send("Ce role n'existe pas")
                            return
                        role_id = int(role_id)
                        found = False
                        for salary in guild_data["salarys"]:
                            for salary_role_id in guild_data["salarys"][salary]:
                                
                                if str(salary_role_id) == str(role_id):
                                    guild_data["salarys"][salary].remove(str(salary_role_id))
                                    role = get(guild.roles, id=int(role_id))
                                    await channel.send(f"Le role {role} n'a maintenant plus de salaire qui lui est assigné")
                                    found = True
                                    break
                        if not found:
                            await channel.send("Ce role n'a pas été trouvé dans la liste des salaires")

                elif message_split[1] == "set":
                    if len(message_split) >= 4:
                        role_id = " ".join(message_split[2:-1]).replace("<", "").replace(">", "").replace("@", "").replace("&", "")
                        salary: int = message_split[-1]
                        if not can_convert_to_int(role_id):
                            role_name = role_id
                            for role in guild.roles:
                                if role.name == role_name:
                                    role_id = role.id
                            if not can_convert_to_int(role_id):
                                await channel.send("Ce role n'existe pas")
                                return
                        elif int(role_id) not in [i.id for i in guild.roles]:
                            await channel.send("Ce role n'existe pas")
                            return
                        
                        last_salary = False
                        for s in guild_data["salarys"]:
                            if str(role_id) in guild_data["salarys"][s]:
                                last_salary = s
                        if not last_salary:
                            await channel.send("Ce role n'existe pas dans la liste des salaires, tu dois d'abord lui assigner un salaire avant de pouvoir le modifier")
                            return
                        if not can_convert_to_int(salary):
                            await channel.send("Tu dois mettre un nombre pour le salaire")
                            return
                        role_id = int(role_id)
                        salary = int(salary)

                        guild_data["salarys"].setdefault(str(salary), [])
                        if str(role_id) in guild_data["salarys"][str(salary)]:
                            await channel.send("Ce role à déjà un salaire qui lui est attribué, pour changer son salaire, utilise la command `salary set` et pour le supprimer utilise la command `salary remove`")
                        else:
                            guild_data["salarys"][last_salary].remove(str(role_id))
                            guild_data["salarys"][str(salary)].append(str(role_id))
                            await channel.send(f"Chaque personne qui a le role {get(guild.roles, id=role_id).name} gagne maintenant {salary} coins tout les lundi 8h")  
                
        
        elif message.content.lower() == prefix + "salarys":
            msg: discord.Message = await channel.send(embed=SalarysListEmbed(guild, guild_data, 0))
            await msg.add_reaction("⬅️")
            await msg.add_reaction("➡️")
            await msg.add_reaction("🔄")
            guild_data["react"]["salary_list"]["id"] = int(msg.id)
            guild_data["react"]["salary_list"]["pos"] = 0
        self.data_file.save(data)

    async def give_salary(self, data_file):
        data = data_file.load()
        for guild in self.bot.guilds:
            if str(guild.id) not in data:
                data_file = new_guild(data_file, guild)
                data = data_file.load()
            
            for member in guild.members:
                member_salarys: list = []
                for s in data[str(guild.id)]["salarys"]:
                    for r in data[str(guild.id)]["salarys"][s]:
                        if str(r) in [str(mr.id) for mr in member.roles]:
                            if str(member.id) not in data[str(guild.id)]["members"]:
                                data_file = new_member(data_file, guild, member)
                                data = data_file.load()
                            member_salarys.append(s)
                member_salarys.sort()
                
                if len(member_salarys) > 0:
                    data[str(guild.id)]["members"][str(member.id)]["coins"] += int(member_salarys[-1])
            data_file.save(data)

        return data_file


class SalarysListEmbed(discord.Embed):
    def __init__(self, guild: discord.Guild, guild_data: dict, page: int = 0, **kwargs) -> None:
        super().__init__(**kwargs)

        max_page = int(len(guild_data["salarys"])/10)+1
        self.title = f"__List des salaires__ [{page+1}/{max_page}]"
        self.color = 0x00ff00

        salarys_sort: list = list(guild_data["salarys"].keys())
        salarys_sort.sort()

        self.description = "Il n'y a aucun salaire"
        if len(salarys_sort) >= 1:
            self.description = ""
        
        for salary in salarys_sort:
            for role_id in guild_data["salarys"][salary]:
                salary_role = get(guild.roles, id=int(role_id))

                if salary_role != None:
                    self.description += f"{salary_role.name} -> {salary} coins\n"
                else:
                    self.description += f"deleted role -> {salary} coins\n"

        # salarys_keys: list = list(guild_data["salarys"].keys())
        # print(salarys_keys)
        # for salary_value in salarys_values_sort[page*10:page*10+10]:
        #     a = list(guild_data["salarys"].values()).index(salary_value)
        #     print(a)
        #     print(salarys_keys[4])
        #     salary_role_id: str = salarys_keys[ list( guild_data["salarys"].values() ).index(salary_value) ]
        #     salarys_keys.remove(salary_role_id)
            
        #     salary_role = get(guild.roles, id=int(salary_role_id))

        #     