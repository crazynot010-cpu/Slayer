import random
from models.npc_model import NPC_TEMPLATES
from systems.player_system import PlayerSystem
from database import players_collection

class CombatSystem:

    CRIT_MULTIPLIER = 1.5

    @staticmethod
    def calculate_damage(attacker_attack, defender_defense, crit_chance):
        base_damage = attacker_attack - (defender_defense * 0.5)

        if base_damage < 1:
            base_damage = 1

        is_crit = random.random() < crit_chance

        if is_crit:
            base_damage *= CombatSystem.CRIT_MULTIPLIER

        return int(base_damage), is_crit

    @staticmethod
    async def start_combat(user_id: int, npc_key: str):
        player = await PlayerSystem.get_player(user_id)

        if npc_key not in NPC_TEMPLATES:
            return {"error": "NPC not found"}

        npc_template = NPC_TEMPLATES[npc_key]

        npc = npc_template.copy()
        npc["current_hp"] = npc["hp"]

        player_current_hp = player["hp"]

        combat_log = []

        # PLAYER TURN
        player_damage, player_crit = CombatSystem.calculate_damage(
            player["attack"],
            npc["defense"],
            0.1  # Player base crit chance
        )

        npc["current_hp"] -= player_damage

        combat_log.append({
            "attacker": "player",
            "damage": player_damage,
            "crit": player_crit
        })

        if npc["current_hp"] <= 0:
            await CombatSystem.handle_victory(user_id, npc)
            return {
                "result": "win",
                "log": combat_log,
                "npc": npc
            }

        # NPC TURN
        npc_damage, npc_crit = CombatSystem.calculate_damage(
            npc["attack"],
            player["defense"],
            npc["crit_chance"]
        )

        player_current_hp -= npc_damage

        combat_log.append({
            "attacker": "npc",
            "damage": npc_damage,
            "crit": npc_crit
        })

        if player_current_hp <= 0:
            await CombatSystem.handle_defeat(user_id)
            return {
                "result": "lose",
                "log": combat_log,
                "npc": npc
            }

        # Update player HP in database
        await players_collection.update_one(
            {"_id": user_id},
            {"$set": {"hp": player_current_hp}}
        )

        return {
            "result": "ongoing",
            "log": combat_log,
            "player_hp": player_current_hp,
            "npc_hp": npc["current_hp"],
            "npc": npc
        }

    @staticmethod
    async def handle_victory(user_id: int, npc: dict):
        await players_collection.update_one(
            {"_id": user_id},
            {
                "$inc": {
                    "xp": npc["xp_reward"],
                    "money": npc["money_reward"]
                }
            }
        )

    @staticmethod
    async def handle_defeat(user_id: int):
        await players_collection.update_one(
            {"_id": user_id},
            {"$set": {"hp": 1}}
            )
