from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import List

class TrendRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["trend_results"]

    async def get_by_request_id(self, request_id: str) -> List[dict]:
        cursor = self.collection.find({"analysis_request_id": ObjectId(request_id)})
        return await cursor.to_list(length=100)

    async def get_one(self, trend_id: str) -> dict:
        return await self.collection.find_one({"_id": ObjectId(trend_id)})

    async def delete(self, trend_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(trend_id)})
        return result.deleted_count > 0

    async def update(self, trend_id: str, data: dict) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(trend_id)},
            {"$set": {**data, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0