import uuid
from models.shadow_model import ShadowModel


class AriseSystem:

    @staticmethod
    async def arise(user_id: int, monster: dict):
        shadow_id = str(uuid.uuid4())

        shadow_data = {
            "owner_id": user_id,
            "name": monster["name"],
            "power": monster["xp"] * 2
        }

        await ShadowModel.create_shadow(shadow_id, shadow_data)

        return shadow_id, shadow_data
