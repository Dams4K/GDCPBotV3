from discord.ext import commands
from discord.utils import get
from utils.files import FileJson
from utils.new_discord import new_guild, new_member
from utils.get_member import get_member
from utils.check import can_convert_to_int
from utils.errors import ShopErrors
from time import time
import discord
import asyncio

time_multiplicator = {
    "s": 1,
    "m": 60,
    "h": 60*60,
    "d": 60*60*24
}

class Shops(commands.Cog):
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
        guild_data = data[str(payload.guild_id)]
        if member.bot:
            return

        if message_id == guild_data["react"]["shops"]["id"]:
            await message.remove_reaction(emoji, member)
            pos = guild_data["react"]["shops"]["pos"]
            calc = "+"
            if emoji.name == "⬅️":
                calc = "-"
            elif emoji.name == "🔄":
                calc = "+1-"

            shops_list: list = list(guild_data["shops"].keys())
            shops_list.remove("number")
            shops_list.sort()
            new_pos = eval(f"{pos}{calc}1")
            
            if len(shops_list) > 0:
                if new_pos >= len(shops_list):
                    new_pos = 0
                elif new_pos < 0:
                    new_pos = len(shops_list)-1

                guild_data["react"]["shops"]["pos"] = new_pos
                await message.edit(content="", embed=ShopEmbed(guild_data, shops_list[new_pos]))
            else:
                guild_data["react"]["shops"]["pos"] = 0
                error_embed: discord.Embed = discord.Embed(title="Error", description="Plus aucun shop n'existe...", color=0xff0000)
                await message.edit(content="", embed=error_embed)
        elif message_id == guild_data["react"]["shops_list"]["id"]:
            await message.remove_reaction(emoji, member)
            pos = guild_data["react"]["shops_list"]["pos"]
            max_page = int(len(guild_data["shops"])/10)+1
            calc = "+"
            
            if emoji.name == "⬅️":
                calc = "-"
            elif emoji.name == "🔄":
                calc = "+1-"
            
            new_pos = eval(f"{pos}{calc}1")
            if new_pos < 0:
                new_pos = max_page-1
            elif new_pos > max_page-1:
                new_pos = 0

            guild_data["react"]["shops_list"]["pos"] = new_pos
            await message.edit(content="" ,embed=ShopListEmbed(guild_data, new_pos))

        elif message_id == guild_data["react"]["inv"]["id"]:
            await message.remove_reaction(emoji, member)
            pos = guild_data["react"]["inv"]["pos"]
            max_page = int(len(guild_data["members"][str(member.id)]["inv"])/10)+1
            calc = "+"
            
            if emoji.name == "⬅️":
                calc = "-"
            elif emoji.name == "🔄":
                calc = "+1-"
            
            new_pos = eval(f"{pos}{calc}1")
            if new_pos < 0:
                new_pos = max_page-1
            elif new_pos > max_page-1:
                new_pos = 0

            guild_data["react"]["inv"]["pos"] = new_pos
            await message.edit(content="", embed=InvEmbed(guild_data, member, new_pos))

        self.data_file.save(data)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        author: discord.Member = message.author
        guild: discord.Guild = message.guild
        channel: discord.TextChannel = message.channel

        # On vérifie si le membre n'est pas un bot
        if author.bot: return
        # On charge la DATA
        self.data_file = new_guild(self.data_file, guild)
        self.data_file = new_member(self.data_file, guild, author)
        data = self.data_file.load()

        # On récupère dans des variables la data du membre et de la guild
        guild_data = data[str(guild.id)]
        prefix = guild_data["prefix"]
        author_data = guild_data["members"][str(author.id)]

        message_split = message.content.lower().split()

        if message.content.lower().startswith(prefix + "shop "):
            if can_convert_to_int(message_split[1]) and message_split[1].lower() != "create":
                shop_id: str = message_split[1]
            elif message_split[1].lower() != "create":
                await channel.send(f"`{message_split[1]}` n'est pas un identifiant")
                return
            
            if len(message_split) >= 3 and message_split[2].lower() in ["set", "remove"] or message_split[1].lower() == "create":
                if not author.guild_permissions.administrator:
                    await channel.send("Tu n'as pas la permission d'utiliser cette commande")
                    return

                if message_split[1].lower() == "create":
                    shop_name: str = " ".join(message.content.split()[2:])
                    guild_data["shops"]["number"] += 1
                    new_id: int = guild_data["shops"]["number"]
                    new_shop: Shop = Shop()
                    new_shop.create(shop_name)
                    guild_data["shops"][new_id] = new_shop.__dict__

                    await channel.send(f"Tu as créer le shop {shop_name}, il a l'id `{new_id}`")
                elif message_split[2].lower() == "set":
                    shop: Shop = Shop()

                    if shop_id not in guild_data["shops"]:
                        await channel.send("Ce shop n'existe pas")
                        return
                    shop.load_dict(guild_data["shops"][shop_id])
                    setting_name: str = message_split[3].lower()
                    
                    if len(message_split) >= 5:
                        if setting_name == "price":
                            if can_convert_to_int(message_split[4]):
                                price: int = int(message_split[4])
                                shop.price = price
                                await channel.send(f"Le prix de __{shop.name}__ est maintenant à `{price}` lustres")
                        # Description
                        elif setting_name == "desc":
                            shop.desc = " ".join(message.content.split()[4:])
                            await channel.send(f"La description de __{shop.name}__ est maintenant\n\n{shop.desc}")
                        # Nom
                        elif setting_name == "name":
                            last_name: str = shop.name
                            shop.name = " ".join(message.content.split()[4:])
                            await channel.send(f"Le nom de __{last_name}__ est maintenant `{shop.name}`")
                        # Articles
                        elif setting_name == "article":
                            if len(message_split) >= 6:
                                article_type: str = message_split[4]
                                article_name: str = " ".join(message.content.split()[5:])
                                
                                if article_type == "role":
                                    role: discord.Role = get(guild.roles, name=article_name)
                                    if role == None:
                                        if can_convert_to_int(article_name.replace("<", "").replace(">", "").replace("&", "").replace("@", "")):
                                            role: discord.Role = get(guild.roles, id=int(article_name.replace("<", "").replace(">", "").replace("&", "").replace("@", "")))

                                    if role != None:
                                        shop.object = {"type": article_type, "name": int(role.id)}
                                        await channel.send(f"L'article de __{shop.name}__ est maintenant le role {role.name}")
                                    else:
                                        await channel.send("Ce role n'existe pas")
                                elif article_type == "item":
                                    shop.object = {"type": article_type, "name": article_name}
                                    await channel.send(f"L'article de __{shop.name}__ est maintenant l'item {shop.object['name']}")
                                else:
                                    await channel.send("Ce type d'article n'existe pas")
                            else:
                                await channel.send("Il manque des paramètres")
                        
                        # Cooldown
                        elif setting_name == "cooldown":
                            nbr_time = message_split[4]
                            multiplicator = message.content[len(message.content)-1:]
                            if not can_convert_to_int(nbr_time):
                                if can_convert_to_int(nbr_time[:len(nbr_time)-1]):
                                    nbr_time = nbr_time[:len(nbr_time)-1]
                                else:
                                    await channel.send("Tu n'as pas mis un nombre pour le temps")
                                    return
                            
                            if can_convert_to_int(multiplicator):
                                multiplicator = 1
                            elif multiplicator in time_multiplicator:
                                multiplicator = time_multiplicator[multiplicator]
                            else:
                                await channel.send("Tu n'as pas mis de bon paramètres pour le temps, pour rappel :\ns = seconds\nh = hours\nd = days")
                                return
                            cooldown = f"{nbr_time} * {multiplicator}"
                            shop.cooldown = cooldown
                            await channel.send(f"Le cooldown du shop est maintenant à {message_split[4]}")
                    else:
                        await channel.send("Il manque des paramètres")

                elif message_split[2] == "remove":
                    await channel.send("Veuillez confirmer la suppression de ce shop en ecrivant `confirm`")
                    
                    def check(m):
                        return m.content.lower() == "confirm" and m.author == author and m.channel == message.channel

                    try:
                        await self.bot.wait_for("message", check=check, timeout=30)
                    except asyncio.TimeoutError:
                        await channel.send("Suppression annulé")
                    else:
                        guild_data["shops"].pop(shop_id)
                        await channel.send("Ce shop est maintenant supprimé")

            elif len(message_split) == 2:
                msg: discord.Message = await channel.send(embed=ShopEmbed(guild_data, guild, shop_id))
                await msg.add_reaction("⬅️")
                await msg.add_reaction("➡️")
                await msg.add_reaction("🔄")
                guild_data["react"]["shops"]["id"] = int(msg.id)
                guild_data["react"]["shops"]["pos"] = shop_id

        elif message.content.lower().startswith(prefix + "buy"):
            if len(message_split) > 1:
                if can_convert_to_int(message_split[1]):
                    shop_id: str = message_split[1]
                    if shop_id not in guild_data["shops"]:
                        await channel.send("Ce shop n'existe pas")
                        return

                    shop: Shop = Shop()
                    shop.load_dict(guild_data["shops"][shop_id])
                    if shop.object["type"] == None:
                        await channel.send("Ce shop ne contient aucun article... Ça sert à rien de dépenser de l'argent dans rien, crois moi")
                        return
                    try:
                        await shop.buy(author, guild, shop_id, data)
                        if shop.object["type"] == "item":
                            await channel.send(f"Tu as acheté l'item {shop.object['name']} pour {shop.price} lustres")
                        elif shop.object["type"] == "role":
                            role: discord.Role = get(guild.roles, id=int(shop.object['name']))
                            await channel.send(f"Tu as acheté le role {role.name} pour {shop.price} lustres")
                    except ShopErrors.NotEnoughCoins as err:
                        await channel.send(f"Tu n'as pas assez de lustres, il te manque {err} lustres")
                    except ShopErrors.HasAlreadyTheRole:
                        await channel.send("Tu as déjà ce role")
                    except ShopErrors.ICantGiveYouThisRole:
                        await channel.send("Je ne peux pas te donner ce role")
                    except ShopErrors.CooldownDidntFinished as err:
                        await channel.send(f"Tu dois attendre {err} pour acheter cet article")

                else:
                    await channel.send(f"`{message_split[1]}` n'est pas un identifiant")
                    return

            elif message.content.lower() == prefix + "shops":
                msg: discord.Message = await channel.send(embed=ShopListEmbed(guild_data))
                await msg.add_reaction("⬅️")
                await msg.add_reaction("➡️")
                await msg.add_reaction("🔄")

                guild_data["react"]["shops_list"]["id"] = msg.id
                guild_data["react"]["shops_list"]["pos"] = 0

        elif message.content.lower().startswith(prefix + "inv"):
            member = await get_member(message, prefix + "inv", pop_back=False, error=False)
            if member == None:
                member = author
            else:
                self.data_file = new_member(self.data_file, guild, member)
                data = self.data_file.load()
                guild_data = data[str(guild.id)]
            
            msg: discord.Message = await channel.send(embed=InvEmbed(guild_data, author, 0))
            await msg.add_reaction("⬅️")
            await msg.add_reaction("➡️")
            await msg.add_reaction("🔄")

            guild_data["react"]["inv"]["id"] = msg.id
            guild_data["react"]["inv"]["pos"] = 0

        self.data_file.save(data)

class Shop:
    def __init__(self) -> None:
        self.name: str = ""
        self.desc = ""
        self.price: int = 0
        self.object: dict = {"name": None, "type": None}
        self.cooldown: str = "0"

    def create(self, name: str) -> None:
        self.name: str = name

    async def buy(self, member: discord.Member, guild: discord.Guild, shop_id: str, data) -> str:
        guild_data: dict = data[str(guild.id)]
        member_data: dict = guild_data["members"][str(member.id)]
        member_coins = member_data["coins"]
        
        if shop_id in member_data["shops"]:
            last_purchase = member_data["shops"][shop_id]
        else:
            last_purchase = "0"
            member_data["shops"][shop_id] = last_purchase

        if member_coins < self.price:
            raise ShopErrors.NotEnoughCoins(self.price, member_coins)
        elif eval(f"{last_purchase} + {self.cooldown}") > int(time()):
            raise ShopErrors.CooldownDidntFinished(eval(f"({last_purchase} + {self.cooldown}) - {time()}"))
        else:
            if self.object["type"] == "role":
                role: discord.Role = get(guild.roles, id=int(self.object["name"]))
                if role == None:
                    raise ShopErrors.RoleDoesntExist()
                elif role in member.roles:
                    raise ShopErrors.HasAlreadyTheRole()
                else:
                    try:
                        await member.add_roles(role, reason=f"Buy this role for {self.price} lustres")
                    except discord.Forbidden:
                        raise ShopErrors.ICantGiveYouThisRole()
            elif self.object["type"] == "item":
                if self.object["name"] in member_data["inv"]:
                    member_data["inv"][self.object["name"]] += 1
                else:
                    member_data["inv"][self.object["name"]] = 1
                member_data["inv"]
            member_data["coins"] -= self.price
            member_data["shops"][shop_id] = str(int(time()))

    def load_dict(self, data: dict) -> None:
        self.__dict__ = data

class ShopEmbed(discord.Embed):
    def __init__(self, guild_data, guild, shop_id: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.color = 0xffff00

        if shop_id not in guild_data["shops"]:
            self.title = "ERROR"
            self.colour = 0xff0000
            self.description = "Ce shop n'existe pas" 
        else:
            shop = Shop()
            shop.load_dict(guild_data["shops"][shop_id])
            self.title = shop.name
            self.description = shop.desc
            if shop.object['type'] == "role":
                role: discord.Role = get(guild.roles, id=int(shop.object['name']))
                self.add_field(name=f"{shop.object['type']} : {role.name}", value=f"Prix : {shop.price} lustres")
            else:
                self.add_field(name=f"{shop.object['type']} : {shop.object['name']}", value=f"Prix : {shop.price} lustres")

class ShopListEmbed(discord.Embed):
    def __init__(self, guild_data: dict, page: int = 0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.color = 0xffff00

        max_page = int(len(guild_data["shops"])/10)+1
        self.title = f"__List des shops__ [{page+1}/{max_page}]"

        shops_keys: list = list(guild_data["shops"].keys())
        shops_keys.remove("number")
        shops_keys: list = [int(e) for e in shops_keys]
        shops_keys.sort()

        self.description = "Pas de shops existant"
        if len(shops_keys) >= 1:
            self.description = ""

        for shop_id in shops_keys[page*10:page*10+10]:
            self.description += f"**{guild_data['shops'][str(shop_id)]['name']}** | id : {shop_id} | prix : {guild_data['shops'][str(shop_id)]['price']}\n"

class InvEmbed(discord.Embed):
    def __init__(self, guild_data: dict, member: discord.Member, page: int = 0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.color = 0x00ff00

        
        member_inv_keys: list = list(guild_data["members"][str(member.id)]["inv"].keys())
        member_inv_keys.sort()

        desc = "Tu n'as pas d'item"
        if len(member_inv_keys) >= 1:
            desc = ""

        max_page = int(len(guild_data['members'][str(member.id)]['inv'])/10)+1
        self.title = f"__List de tes items__ [{page+1}/{max_page}]"

        for item_name in member_inv_keys[page*10:page*10+10]:
            desc += f"**{item_name}** : {guild_data['members'][str(member.id)]['inv'][item_name]}\n"

        self.description = desc