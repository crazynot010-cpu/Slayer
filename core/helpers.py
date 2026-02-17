from core.config import RANK_LEVELS

def xp_needed(level):
    return 100 + (level - 1) * 50

def get_rank(level):
    current = "E"
    for lvl in sorted(RANK_LEVELS):
        if level >= lvl:
            current = RANK_LEVELS[lvl]
    return current
