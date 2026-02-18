class RankSystem:

    RANK_ORDER = ["E", "D", "C", "B", "A", "S", "SS", "SSS"]

    @staticmethod
    def is_valid_rank(rank: str):
        return rank.upper() in RankSystem.RANK_ORDER

    @staticmethod
    def rank_index(rank: str):
        return RankSystem.RANK_ORDER.index(rank.upper())
