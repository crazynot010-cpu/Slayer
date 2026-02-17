RANKS = {
    "E": 1,
    "D": 5,
    "C": 10,
    "B": 20,
    "A": 35,
    "S": 50
}

RANK_COLORS = {
    "E": 0x95A5A6,
    "D": 0x2ECC71,
    "C": 0x3498DB,
    "B": 0x9B59B6,
    "A": 0xE67E22,
    "S": 0xE74C3C
}

def get_rank_from_level(level: int):
    current_rank = "E"
    for rank, lvl in RANKS.items():
        if level >= lvl:
            current_rank = rank
    return current_rank
