class RankSystem:

    RANKS = {
        1: "E",
        5: "D",
        10: "C",
        20: "B",
        35: "A",
        50: "S"
    }

    @staticmethod
    def get_rank(level: int) -> str:
        current_rank = "E"

        for lvl, rank in sorted(RankSystem.RANKS.items()):
            if level >= lvl:
                current_rank = rank

        return current_rank
