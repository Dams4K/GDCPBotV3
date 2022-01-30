from discord.ext import commands
from utils.files import FileJson
from utils.new_discord import new_guild, new_member
import discord, datetime

help_file = FileJson("datas/help.json", None)
stats_file = FileJson("datas/stats.json", {})

class Help(commands.Cog):
    def __init__(self, bot: discord.Client, data_file: FileJson) -> None:
        self.bot = bot
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
        help_data = help_file.load()
        guild_data = data[str(payload.guild_id)]

        if message_id == guild_data["react"]["help"]["id"] and not member.bot:
            await message.remove_reaction(emoji, member)
            pos = guild_data["react"]["help"]["pos"]
            calc = "+"
            if emoji.name == "⬅️":
                calc = "-"

            new_pos = eval(f"{pos}{calc}1")
            
            if new_pos < 0: new_pos = len(help_data)-1
            elif new_pos >= len(help_data): new_pos = 0

            guild_data["react"]["help"]["pos"] = new_pos
            await message.edit(content="", embed=HelpEmbed(guild_data))
            self.data_file.save(data)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
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

        if message.content.lower() == prefix + "help" or message.content.lower() == "+help":
            guild_data["react"]["help"]["pos"] = 0
            new_message: discord.Message = await channel.send(embed=HelpEmbed(guild_data))
            guild_data["react"]["help"]["id"] = new_message.id
            await new_message.add_reaction("⬅️")
            await new_message.add_reaction("➡️")
        elif message.content.lower().startswith(prefix + "help ") or message.content.lower().startswith("+help "):
            help_data = help_file.load()

            cmd = " ".join(message.content.lower().split()[1:])
            cmd_found = False
            for category in help_data:
                for command in category["commands"]:
                    if command.lower() == cmd:
                        cmd_found = True
                        await channel.send(embed=HelpCommandEmbed(prefix, category, cmd, self.bot, author))
        
            if not cmd_found:
                await channel.send(f"Cette commande n'existe pas. `{prefix}help` pour voir la liste de toute les commandes")

        self.data_file.save(data)

class HelpCommandEmbed(discord.Embed):
    def __init__(self, guild_prefix: str, category: dict, cmd_name: str, bot: discord.Client, author: discord.Member, **kwargs) -> None:
        super().__init__(**kwargs)
        self.color = 0xfcfcfc
        stats_data: dict = stats_file.load()
        cmd_data = category["commands"][cmd_name]
        self.title = f"__Commande {cmd_name}__ __\n\n__"

        self.add_field(name="Commande : ", value=f"{guild_prefix}{cmd_name} {cmd_data['command']}", inline=False)
        self.add_field(name="Description : ", value=cmd_data["description"].format(prefix=guild_prefix), inline=False)
        self.add_field(name="Exemple : ", value=guild_prefix + cmd_name + " " + f"\n  {guild_prefix}{cmd_name} ".join(cmd_data["example"]).format(bot=bot, member=author))
        stats_data.setdefault(cmd_name, 0)
        self.set_footer(text=f"Utilisé en moyenne {round(stats_data[cmd_name]/(datetime.datetime.today().weekday()+1), 1)}/j")

class HelpEmbed(discord.Embed):
    def __init__(self, guild_data, **kwargs) -> None:
        global help_file
        super().__init__(**kwargs)
        self.color = 0xfcfcfc
        guild_prefix = guild_data["prefix"]

        help_data = help_file.load()
        pos = guild_data['react']['help']['pos']
        self.title = f"Page d'aide [{pos+1}/{len(help_data)}]"
        description: str = f"__{help_data[pos]['name']}__ :\n\n"
        for command in help_data[pos]["commands"]:
            description += f"`{command}`\n"

        description += f"\nChaque commandes est à utiliser avec le prefix `{guild_prefix}`\n`{guild_prefix}help <command>` pour plus d'information sur une commande"
        self.description = description
