import discord

async def get_member(message: discord.Message, cmd: str, pop_back=True, error=True) -> discord.Member:
    guild: discord.Guild = message.guild
    channel: discord.channel = message.channel
    # On récupère le membre à éditer
    message.content = message.content.lower().replace(cmd.lower() + " ", "")
    member = [i for i in message.content.split()]

    if pop_back:
        member.pop()
    member = " ".join(member)

    # On regarde si il est présent dans la guild
    for guild_member in guild.members:
        if str(guild_member).lower() == member:
            return guild_member
        elif str(guild_member.id) == member:
            return guild_member
        elif member.replace("!", "") == str(guild_member.mention).replace("!", ""):
            return guild_member

    # S'il n'est pas présent, on le dit
    if error:
        await channel.send(member + " ne fais pas parti de ce serveur")