from discord.ext import commands
from utils.files import FileJson
from utils.new_discord import new_guild, new_member
from utils.get_member import get_member
from random import randint
import discord, asyncio, colorsys, glob

class Everyone(commands.Cog):
    def __init__(self, bot: discord.Client, bot_info: dict, data: FileJson):
        self.bot: discord.Client = bot
        self.data_file: FileJson = data
        self.bot_info = bot_info

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        guild = message.guild
        channel = message.channel

        # On vérifie si le membre n'est pas un bot
        if author.bot: return
        # On charge la DATA
        self.data = new_guild(self.data_file, guild)
        self.data = new_member(self.data_file, guild, author)
        data = self.data_file.load()

        # On récupère dans des variables la data du membre et de la guild
        guild_data = data[str(guild.id)]
        prefix = guild_data["prefix"]

        if message.content.lower().startswith(prefix + "profil"):
            member = await get_member(message, prefix + "profil", pop_back=False, error=False)

            if member == None:
                member = author
            else:
                self.data = new_member(self.data, guild, member)
                data_json = self.data.load()
                guild_data = data_json[str(guild.id)]


            member_data = guild_data["members"][str(member.id)]
            member_level = member_data["level"]
            member_coins = member_data["coins"]
            member_xp = member_data["xp"]
            member_xp_calc = eval(guild_data["level"]["calc"].format(l=member_data["level"]))

            embed = discord.Embed(title=f"**Profil de : {member}**", color=0x00ffff)
            embed.add_field(name="__Level :__", value=str(member_level), inline=True)
            embed.add_field(name="__XP :__", value=f"{member_xp}/{member_xp_calc}", inline=True)
            embed.add_field(name="__Lustres :__", value=f"{member_coins}", inline=False)
            await channel.send(embed=embed)

        elif message.content.lower() == prefix + "creatures":
            image_list = glob.glob("datas/images/Creatures/*")            
            image = discord.File(image_list[randint(0, len(image_list)-1)])

            await channel.send(file=image)

        elif message.content.lower() == prefix + "places":
            image_list = glob.glob("datas/images/Places/*")
            image = discord.File(image_list[randint(0, len(image_list)-1)])

            await channel.send(file=image)

        elif message.content.lower() == prefix + "characters":
            image_list = glob.glob("datas/images/Characters/*")
            image = discord.File(image_list[randint(0, len(image_list)-1)])

            await channel.send(file=image)

        elif message.content.lower().startswith(prefix + "report "):
            report_channel: discord.channel = self.bot.get_channel(self.bot_info["report_channel_id"])
            report_message = f"Report de **{author.id}** dans le salon __{channel.id}__ : \n\n{' '.join(message.content.split()[1:])}"
            if report_channel != None:
                await report_channel.send(report_message)
            else:
                creator: discord.Member = discord.utils.get(self.bot.get_all_members(), id=self.bot_info["creator_id"])
                
                await creator.send(report_message)
            
            await channel.send("Rapport envoyé")

        elif message.content.lower().startswith(prefix + "suggest "):
            suggest_channel: discord.channel = self.bot.get_channel(self.bot_info["suggest_channel_id"])
            suggest_message = f"Suggestion de **{author.id}** dans le salon __{channel.id}__ : \n\n{' '.join(message.content.split()[1:])}"
            if suggest_channel != None:
                await suggest_channel.send(suggest_message)
            else:
                creator: discord.Member = discord.utils.get(self.bot.get_all_members(), id=self.bot_info["creator_id"])
                
                await creator.send(suggest_message)

            await channel.send("Suggestion envoyé")

        self.data_file.save(data)