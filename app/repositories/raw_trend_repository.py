from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.raw_trend_data import RawTrendDataModel
from app.schemas.raw_trend_data import RawTrendDataCreate
from bson import ObjectId
from datetime import datetime, timezone
from typing import Optional, List

class RawTrendRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["raw_trend_data"]

    async def create(self, raw_in: RawTrendDataCreate) -> dict:
        raw_data = raw_in.model_dump()
        new_raw = RawTrendDataModel(**raw_data)
        
        raw_dict = new_raw.model_dump()
        result = await self.collection.insert_one(raw_dict)
        
        raw_dict["_id"] = str(result.inserted_id)
        return raw_dict

    async def create_many(self, items_in: List[RawTrendDataCreate]) -> int:
        """Hỗ trợ lưu hàng loạt dữ liệu khi crawl"""
        if not items_in:
            return 0
        documents = [RawTrendDataModel(**item.model_dump()).model_dump() for item in items_in]
        result = await self.collection.insert_many(documents)
        return len(result.inserted_ids)

    async def get_by_source(self, source: str, limit: int = 100) -> List[dict]:
        """Lấy dữ liệu thô theo nguồn (ví dụ: lấy 100 tin từ TikTok)"""
        results = []
        cursor = self.collection.find({"source_type": source}).limit(limit)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    async def get_by_id(self, raw_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(raw_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(raw_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def assign_trend(self, raw_id: str, trend_id: str) -> bool:
        """Gán trend_id cho dữ liệu thô sau khi AI phân tích xong"""
        if not ObjectId.is_valid(raw_id):
            return False
        result = await self.collection.update_one(
            {"_id": ObjectId(raw_id)},
            {"$set": {"trend_id": trend_id}}
        )
        return result.modified_count > 0

    async def delete_old_data(self, days: int = 30) -> int:
        """Xóa dữ liệu cũ để tránh đầy DB (Cleanup logic)"""
        # Đây là ví dụ, tùy bạn có muốn giữ data làm tập train không
        pass