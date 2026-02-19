import discord

def success_embed(title, description):
    embed = discord.Embed(
        title=title,
        description=description,
        color=0x2ecc71
    )
    return embed

def error_embed(title, description):
    embed = discord.Embed(
        title=title,
        description=description,
        color=0xe74c3c
    )
    return embed
