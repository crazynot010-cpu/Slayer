import discord
from utils.constants import DEFAULT_COLOR


def base_embed(title: str = None, description: str = None, color: int = DEFAULT_COLOR):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed


def success_embed(message: str):
    from utils.constants import SUCCESS_COLOR
    return base_embed("Success", message, SUCCESS_COLOR)


def error_embed(message: str):
    from utils.constants import ERROR_COLOR
    return base_embed("Error", message, ERROR_COLOR)


def warning_embed(message: str):
    from utils.constants import WARNING_COLOR
    return base_embed("Warning", message, WARNING_COLOR)
