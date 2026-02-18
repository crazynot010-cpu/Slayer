import random
import asyncio
import discord

from models.guild_model import GuildModel

active_spawns = {}


async def handle_message_spawn(bot, message: discord.Message):

    guild_data = await GuildModel.get_guild(message.guild.id)

    # If no spawn channel set, don't spawn
    if not guild_data["spawn_channel_id"]:
        return

    # Increment message counter
    new_count = guild_data["message_count"] + 1

    # If no threshold yet, set random 12–30
    if not guild_data.get("spawn_threshold"):
        threshold = random.randint(12, 30)
    else:
        threshold = guild_data["spawn_threshold"]

    # Save updated count
    await GuildModel.update_guild(
        message.guild.id,
        {"message_count": new_count}
    )

    if new_count < threshold:
        return

    # RESET counter + set new threshold
    new_threshold = random.randint(12, 30)

    await GuildModel.update_guild(
        message.guild.id,
        {
            "message_count": 0,
            "spawn_threshold": new_threshold
        }
    )

    await spawn_shadow(bot, message.guild)


async def spawn_shadow(bot, guild: discord.Guild):

    guild_data = await GuildModel.get_guild(guild.id)

    channel = guild.get_channel(guild_data["spawn_channel_id"])
    if not channel:
        return

    shadow_name = random.choice(["Goblin", "Orc", "Shadow Knight"])
    shadow_rank = random.choice(["E", "D", "C"])
    xp_reward = random.randint(50, 120)

    embed = discord.Embed(
        title="⚔️ A Shadow Has Appeared!",
        description=f"**{shadow_name}** (Rank {shadow_rank})\n\nType `/arise` to claim!",
        color=0x2f3136
    )

    msg = await channel.send(
        content=f"<@&{guild_data['ping_role_id']}>" if guild_data["ping_role_id"] else None,
        embed=embed
    )

    active_spawns[guild.id] = {
        "name": shadow_name,
        "rank": shadow_rank,
        "xp": xp_reward,
        "message_id": msg.id
    }

    # Expire after 2 minutes
    await asyncio.sleep(120)

    if guild.id in active_spawns:
        del active_spawns[guild.id]

        expire_embed = discord.Embed(
            title="❌ Shadow Escaped!",
            description="You were too slow...",
            color=0xff0000
        )

        await channel.send(embed=expire_embed)
