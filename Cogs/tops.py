import asyncio

import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle, message
from discord_components.client import DiscordComponents
from discord_components.interaction import Interaction, InteractionType
from utils.files import FileJson
from utils.level_calc import level_to_xp, xp_to_level
from utils.new_discord import new_guild, new_member

order = [
    "level",
    "lustres"
]

top_emoji = [
    "<:First:798229195549179915>",
    "<:Second:798266104761024582>",
    "<:Third:798229194743611434>"
]

class Tops(commands.Cog):
    def __init__(self, bot: discord.Client, data_file: FileJson):
        self.bot: discord.Client = bot
        self.data_file: FileJson = data_file
        DiscordComponents(bot)


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

        if message.content.lower() == prefix + "tops":
            embed_msg: discord.Message = await channel.send(
                embed=TopsEmbed(0, author, guild, guild_data),
                components=[
                    [
                        Button(label="←", style=ButtonStyle.green),
                        Button(label="→", style=ButtonStyle.green),
                        Button(label="🔄", style=ButtonStyle.blue)
                    ]
                ]
            )
            guild_data["react"]["tops"]["id"] = embed_msg.id
            guild_data["react"]["tops"]["pos"] = 0

        self.data_file.save(data)

    @commands.Cog.listener()
    async def on_button_click(self, res: Interaction):
        """
        Possible interaction types:
        - Pong
        - ChannelMessageWithSource
        - DeferredChannelMessageWithSource
        - DeferredUpdateMessage
        - UpdateMessage
        """
        self.data_file = new_guild(self.data_file, res.guild)
        self.data_file = new_member(self.data_file, res.guild, res.author)
        data = self.data_file.load()

        guild_data = data[str(res.guild.id)]
        button_label: str = res.component.label

        if res.message.id == guild_data["react"]["tops"]["id"]:
            pos = guild_data["react"]["tops"]["pos"]
            calc = "+"
            if button_label == "←":
                calc = "-"
            elif button_label in ["refresh", "🔄"]:
                calc = "+1-"
            new_pos = eval(f"{pos}{calc}1")
            
            if new_pos >= 0:
                if new_pos >= len(order):
                    new_pos = 0
            else:
                new_pos = len(order)-1
                
            guild_data["react"]["tops"]["pos"] = new_pos
            
            await res.respond(
                type=InteractionType.UpdateMessage, embed=TopsEmbed(pos=new_pos, author=res.author, guild=res.guild, guild_data=guild_data, 
                components=[
                    [
                        Button(label="←", style=ButtonStyle.green),
                        Button(label="→", style=ButtonStyle.green),
                        Button(label=f"Page {new_pos+1}/2", style=ButtonStyle.blue, disabled=True)
                    ]
                ])
            )

        self.data_file.save(data)




class TopsEmbed(discord.Embed):
    def __init__(self, pos: int, author: discord.Member, guild: discord.Guild, guild_data: dict, **kwargs) -> None:
        super().__init__(**kwargs)

        self.color = 0xff8000
        self.title = order[pos][0].upper() + order[pos][1:] + " top"

        top_members: dict = {}
        author_id: str = str(author.id)

        if pos == 0:
            top_xp: list = []
            xp_list: list = []
            guild_level_calc = guild_data["level"]["calc"]

            for member in guild_data["members"]:
                if guild.get_member(int(member)) == None:
                    continue

                member_xp = level_to_xp(guild_level_calc, guild_data["members"][member]["level"]) + guild_data["members"][member]["xp"]
    
                if len(top_xp) < 10:
                    top_xp.append(member_xp)
                    top_members[member] = member_xp
                else:
                    if top_xp[-1] < member_xp:
                        top_members.pop(list(top_members.keys())[list(top_members.values()).index(top_xp[-1])])
                        top_xp.pop(-1)

                        top_xp.append(member_xp)
                        top_members[member] = member_xp
                xp_list.append(member_xp)
                top_xp.sort()
                top_xp.reverse()
            xp_list.sort()
            xp_list.reverse()

            desc: str = ""
            author_rank: int = 0

            for xp_index in range(len(top_xp)):
                rank: int = xp_index+1
                xp: int = top_xp[xp_index]
                member_id: str = list(top_members.keys())[list(top_members.values()).index(xp)]
                top_members.pop(member_id)
                member = guild.get_member(int(member_id))

                if member_id == author_id: author_rank = rank
                if member == None: member = "Deleted User"
                
                if rank < 4:
                    rank = top_emoji[rank-1]
                else:
                    rank = f"[{rank}]"
                
                desc += f"{rank} {member} - **{guild_data['members'][member_id]['level']}**\n"

            author_xp: int = level_to_xp(guild_level_calc, guild_data["members"][author_id]["level"]) + guild_data["members"][author_id]["xp"]

            if author_rank == 0: author_rank = xp_list.index(author_xp)+1

            if author_rank < 4:
                author_rank = top_emoji[author_rank-1]
            else:
                author_rank = f"[{author_rank}]"

            desc += f"\n\n**Toi : ** {author_rank} {author} - **{guild_data['members'][str(author_id)]['level']}**"

            self.description = desc

        elif pos == 1:
            top_coins: list = []
            coins_list: list = []

            for member in guild_data["members"]:
                if guild.get_member(int(member)) == None:
                    continue
                member_coins = guild_data["members"][member]["coins"]
                if len(top_coins) < 10:
                    top_coins.append(member_coins)
                    top_members[member] = member_coins
                else:
                    if top_coins[-1] < member_coins:
                        top_members.pop(list(top_members.keys())[list(top_members.values()).index(top_coins[-1])])
                        top_coins.pop(-1)

                        top_coins.append(member_coins)
                        top_members[member] = member_coins
                coins_list.append(member_coins)
                top_coins.sort()
                top_coins.reverse()
            coins_list.sort()
            coins_list.reverse()

            desc: str = ""
            author_rank: int = 0

            for coins_index in range(len(top_coins)):
                rank: int = coins_index+1
                coins: int = top_coins[coins_index]
                member_id: int = int(list(top_members.keys())[list(top_members.values()).index(coins)])
                top_members.pop(str(member_id))
                member = guild.get_member(member_id)

                if str(member_id) == author_id: author_rank = rank
                if member == None: member = "Deleted User"

                if rank < 4:
                    rank = top_emoji[rank-1]
                else:
                    rank = f"[{rank}]"
                desc += f"{rank} {member} - **{coins}**\n"

            author_coins: int = guild_data['members'][author_id]['coins']
            if author_rank == 0: author_rank = coins_list.index(author_coins)+1

            if author_rank < 4:
                author_rank = top_emoji[author_rank-1]
            else:
                author_rank = f"[{author_rank}]"

            desc += f"\n\n**Toi : ** {author_rank} {author} - **{author_coins}**"

            self.description = desc
