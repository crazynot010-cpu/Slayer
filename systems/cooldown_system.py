import time


class CooldownSystem:

    _cooldowns = {}

    @staticmethod
    def check(user_id: int, key: str, seconds: int):
        now = time.time()
        user_data = CooldownSystem._cooldowns.get(user_id, {})

        last_used = user_data.get(key)

        if last_used and now - last_used < seconds:
            remaining = seconds - (now - last_used)
            return False, round(remaining, 1)

        user_data[key] = now
        CooldownSystem._cooldowns[user_id] = user_data
        return True, 0
