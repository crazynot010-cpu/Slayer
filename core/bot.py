import os
import random
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from motor.motor_asyncio import AsyncIOMotorClient

TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

if not TOKEN:
    raise RuntimeError("TOKEN missing.")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI missing.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class SlayerBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents
        )
        self.mongo = AsyncIOMotorClient(MONGO_URI)
        self.db = self.mongo["solo_leveling"]

    async def setup_hook(self):

        # --- REGISTER SLASH COMMANDS ---
        self.tree.add_command(self.profile)
        self.tree.add_command(self.inventory)
        self.tree.add_command(self.leaderboard)
        self.tree.add_command(self.arise)
        self.tree.add_command(self.setspawnchannel)

        synced = await self.tree.sync()
        print(f"Global synced {len(synced)} commands.")

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        print("Slash Error:", error)

        if interaction.response.is_done():
            await interaction.followup.send(
                "An error occurred.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "An error occurred.",
                ephemeral=True
            )

    async def ensure_user(self, user_id: int):
        user = await self.db.users.find_one({"_id": user_id})
        if not user:
            user = {
                "_id": user_id,
                "level": 1,
                "xp": 0,
                "shadows": []
            }
            await self.db.users.insert_one(user)
        return user

    # ============================
    # PREFIX COMMAND
    # ============================

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

    # ============================
    # SLASH COMMANDS
    # ============================

    @app_commands.command(name="profile", description="View your hunter profile")
    async def profile(self, interaction: discord.Interaction):

        await interaction.response.defer()

        user = await self.ensure_user(interaction.user.id)

        await interaction.followup.send(
            f"**Level:** {user['level']}\n"
            f"**XP:** {user['xp']}\n"
            f"**Shadows:** {len(user['shadows'])}"
        )

    @app_commands.command(name="inventory", description="View your shadows")
    async def inventory(self, interaction: discord.Interaction):

        await interaction.response.defer()

        user = await self.ensure_user(interaction.user.id)

        if not user["shadows"]:
            return await interaction.followup.send("You have no shadows.")

        shadow_list = "\n".join(user["shadows"])
        await interaction.followup.send(f"**Your Shadows:**\n{shadow_list}")

    @app_commands.command(name="leaderboard", description="Top hunters")
    async def leaderboard(self, interaction: discord.Interaction):

        await interaction.response.defer()

        users = self.db.users.find().sort("level", -1).limit(10)

        text = ""
        rank = 1

        async for user in users:
            text += f"{rank}. <@{user['_id']}> - Level {user['level']}\n"
            rank += 1

        if not text:
            text = "No hunters yet."

        await interaction.followup.send(text)

    @app_commands.command(name="arise", description="Arise a random shadow")
    async def arise(self, interaction: discord.Interaction):

        await interaction.response.defer()

        user = await self.ensure_user(interaction.user.id)

        shadows = [
            "Iron",
            "Tank",
            "Beru",
            "Igris",
            "Tusk"
        ]

        shadow = random.choice(shadows)

        await self.db.users.update_one(
            {"_id": interaction.user.id},
            {
                "$push": {"shadows": shadow},
                "$inc": {"xp": 25}
            }
        )

        await interaction.followup.send(
            f"🗡️ You have arisen **{shadow}**!\n+25 XP"
        )

    @app_commands.command(name="setspawnchannel", description="Set spawn channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def setspawnchannel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        await interaction.response.defer(ephemeral=True)

        await self.db.guilds.update_one(
            {"_id": interaction.guild.id},
            {"$set": {"spawn_channel": channel.id}},
            upsert=True
        )

        await interaction.followup.send(
            f"Spawn channel set to {channel.mention}",
            ephemeral=True
        )


bot = SlayerBot()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)


bot.run(TOKEN)
