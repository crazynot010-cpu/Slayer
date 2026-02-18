import time


class CooldownSystem:

    def __init__(self):
        self.cooldowns = {}

    def is_on_cooldown(self, user_id: int, seconds: int):
        now = time.time()

        if user_id not in self.cooldowns:
            self.cooldowns[user_id] = now
            return False

        last_used = self.cooldowns[user_id]

        if now - last_used < seconds:
            return True

        self.cooldowns[user_id] = now
        return False


cooldown_system = CooldownSystem()
