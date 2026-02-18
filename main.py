import asyncio
from core.bot import SoloBot
from settings import TOKEN


async def main():
    bot = SoloBot()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
