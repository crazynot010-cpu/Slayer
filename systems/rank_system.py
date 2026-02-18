import discord 
from utils.constants import RANK_LEVELS


class RankSystem:

    @staticmethod
    async def update_roles(member, level: int):
        guild = member.guild

        eligible_rank = None

        for lvl, role_name in sorted(RANK_LEVELS.items(), reverse=True):
            if level >= lvl:
                eligible_rank = role_name
                break

        if not eligible_rank:
            return

        # Find role in guild
        role = discord.utils.get(guild.roles, name=eligible_rank)
        if not role:
            return  # Role must exist manually in server

        # Remove lower rank roles
        for r in guild.roles:
            if r.name in RANK_LEVELS.values() and r in member.roles:
                await member.remove_roles(r)

        # Add new rank role
        if role not in member.roles:
            await member.add_roles(role)
