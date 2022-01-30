from os import stat
from discord import embeds
from discord.ext import commands
from utils.files import FileJson
from utils.new_discord import new_guild, new_member
from utils.get_member import get_member
import discord, datetime, time, asyncio

help_file = FileJson("datas/help.json", None)
stats_file = FileJson("datas/stats.json", {})

top_emoji = [
    "<:First:798229195549179915>",
    "<:Second:798266104761024582>",
    "<:Third:798229194743611434>"
]

class Stats(commands.Cog):
    def __init__(self, bot: discord.Client, data: FileJson):
        self.bot: discord.Client = bot
        self.data_file: FileJson = data


    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        guild = message.guild
        channel = message.channel

        # On vérifie si le membre n'est pas un bot
        if author.bot: return
        # On charge la DATA
        self.data_file = new_guild(self.data_file, guild)
        self.data_file = new_member(self.data_file, guild, author)
        data = self.data_file.load()
        help_data: dict = help_file.load()
        stats_data: dict = stats_file.load()

        # On récupère dans des variables la data du membre et de la guild
        guild_data = data[str(guild.id)]
        prefix = guild_data["prefix"]
        
        for categorie in help_data:
            for cmd in categorie["commands"]:
                if message.content.lower().startswith(prefix + cmd):
                    stats_data.setdefault(cmd, 0)
                    stats_data[cmd] += 1
        
        if message.content.lower() == prefix + "stats":
            await channel.send(embed=StatsEmbed(self.bot, stats_data, self.data_file))

        stats_file.save(stats_data)
        self.data_file.save(data)


    async def reset_stats(self):
        global stats_file

        stats_data = stats_file.load()
        stats_data = stats_data.fromkeys(stats_data, 0)
        stats_file.save(stats_data)

class StatsEmbed(discord.Embed):
    def __init__(self, bot: dict, stats_data: dict, data_file: FileJson, **kwargs):
        super().__init__(**kwargs)
        
        self.title = "Stats du bot"
        self.color = 0x0000ff
        self.add_field(name="Nombre de serveurs où le bot est :", value=f"{len(bot.guilds)}/100", inline=False)

        cmds: list = list(stats_data.keys())
        total_number_used_cmds: list = list(stats_data.values())

        top_used: list = total_number_used_cmds.copy()
        top_used.sort()
        top_used.reverse()

        top_commands_message: str = ""
        for i in range(3):
            top_commands_message += f"{top_emoji[i]} {cmds[total_number_used_cmds.index(top_used[i])]} - {round(top_used[i]/(datetime.datetime.today().weekday()+1), 1)}/j \n"
            cmds.pop(total_number_used_cmds.index(top_used[i]))
            total_number_used_cmds.remove(top_used[i])

        total_top_used = 0
        for ele in top_used:
            total_top_used += ele

        top_commands_message += f"\nTotal : **{round(total_top_used/(datetime.datetime.today().weekday()+1), 1)}/j**\n*stats reset chaque début de semaines*"

        self.add_field(name="Top 3 des commandes les plus utilisé :", value=top_commands_message, inline=False)
        num_lines = sum(1 for line in open(data_file.filename, "r"))

        self.add_field(name="Nombres de lignes dans la data : ", value=str(num_lines), inline=False)