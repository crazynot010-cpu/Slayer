def format_number(number: int) -> str:
    return f"{number:,}"


def progress_bar(current: int, maximum: int, length: int = 20) -> str:
    ratio = current / maximum if maximum > 0 else 0
    filled = int(ratio * length)
    empty = length - filled

    return "█" * filled + "░" * empty


def rank_emoji(rank: str) -> str:
    emojis = {
        "E": "🟤",
        "D": "🟢",
        "C": "🔵",
        "B": "🟣",
        "A": "🔴",
        "S": "🟡"
    }
    return emojis.get(rank, "⚪")
