from core.bot import SoloLevelingBot
from settings import TOKEN

bot = SoloLevelingBot()

if __name__ == "__main__":
    bot.run(TOKEN)
