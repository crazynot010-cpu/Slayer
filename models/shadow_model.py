from database import shadows_collection


class ShadowModel:

    @staticmethod
    async def create_shadow(shadow_id: str, data: dict):
        shadow = {
            "_id": shadow_id,
            **data
        }
        await shadows_collection.insert_one(shadow)

    @staticmethod
    async def get_shadow(shadow_id: str):
        return await shadows_collection.find_one({"_id": shadow_id})

    @staticmethod
    async def delete_shadow(shadow_id: str):
        await shadows_collection.delete_one({"_id": shadow_id})
