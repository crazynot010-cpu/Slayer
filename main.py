import asyncio
from settings import TOKEN
from core.bot import SlayerBot


async def main():
    bot = SlayerBot()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
