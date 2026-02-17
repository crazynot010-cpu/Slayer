import discord
from database.mongo import guilds

async def update_rank_role(member, rank):
    guild_data = await guilds.find_one({"guild_id": member.guild.id})
    if not guild_data:
        guild_data = {"guild_id": member.guild.id, "rank_roles": {}}
        await guilds.insert_one(guild_data)

    role_id = guild_data["rank_roles"].get(rank)
    role = member.guild.get_role(role_id) if role_id else None

    if not role:
        role = await member.guild.create_role(name=f"{rank} Rank")
        guild_data["rank_roles"][rank] = role.id
        await guilds.update_one(
            {"guild_id": member.guild.id},
            {"$set": {"rank_roles": guild_data["rank_roles"]}}
        )

    for r in guild_data["rank_roles"].values():
        old = member.guild.get_role(r)
        if old and old in member.roles:
            await member.remove_roles(old)

    await member.add_roles(role)
