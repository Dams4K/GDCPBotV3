from discord.ext import commands
from utils.files import FileJson
from utils.new_discord import new_guild, new_member
import discord, asyncio

updates_file = FileJson("datas/updates.json", None)

class Update(commands.Cog):
    def __init__(self, bot: discord.Client, data_file: FileJson):
        self.bot: discord.Client = bot
        self.data_file: FileJson = data_file

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
        updates_data = updates_file.load()
        guild_data = data[str(payload.guild_id)]

        if message_id == guild_data["react"]["updates"]["id"] and not member.bot:
            await message.remove_reaction(emoji, member)
            pos = guild_data["react"]["updates"]["pos"]
            calc = "+"
            if emoji.name == "⬅️":
                calc = "-"
            elif emoji.name == "🔄":
                calc = "+1-"

            new_pos = eval(f"{pos}{calc}1")
            
            if new_pos < 0: new_pos = len(updates_data)-1
            elif new_pos >= len(updates_data): new_pos = 0

            guild_data["react"]["updates"]["pos"] = new_pos
            await message.edit(content="", embed=UpdateEmbed(new_pos, guild_data["prefix"]))
            self.data_file.save(data)

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
        # On récupère dans des variables la data du membre et de la guild
        guild_data = data[str(guild.id)]
        prefix = guild_data["prefix"]

        if message.content.lower().startswith(prefix + "updates"):
            guild_data["react"]["updates"]["pos"] = len(updates_file.load())-1
            new_message: discord.Message = await channel.send(embed=UpdateEmbed(guild_data["react"]["updates"]["pos"], prefix))
            guild_data["react"]["updates"]["id"] = new_message.id
            await new_message.add_reaction("⬅️")
            await new_message.add_reaction("➡️")
            await new_message.add_reaction("🔄")

        self.data_file.save(data)

class UpdateEmbed(discord.Embed):
    def __init__(self, pos, prefix, **kwargs):
        global updates_file
        super().__init__(**kwargs)
        self.color = 0x0000ff
        update_data = updates_file.load()[pos]
        
        self.title = "Version " + update_data["version"]
        if "description" in update_data.keys():
            self.description = update_data["description"]

        for field in update_data["fields"]:
            self.add_field(name=field["name"], value=field["value"].format(prefix = prefix))