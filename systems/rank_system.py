import discord
from utils.constants import RANK_LEVELS


class RankSystem:

    @staticmethod
    async def update_roles(member, level: int):

        eligible_rank = None

        for lvl, role_name in sorted(RANK_LEVELS.items(), reverse=True):
            if level >= lvl:
                eligible_rank = role_name
                break

        if not eligible_rank:
            return

        role = discord.utils.get(member.guild.roles, name=eligible_rank)
        if not role:
            return

        for r in member.roles:
            if r.name in RANK_LEVELS.values():
                await member.remove_roles(r)

        if role not in member.roles:
            await member.add_roles(role)
