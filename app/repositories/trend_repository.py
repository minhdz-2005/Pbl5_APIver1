from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.fashion_trend import FashionTrendModel
from app.schemas.fashion_trend import FashionTrendCreate, FashionTrendUpdate
from bson import ObjectId
from typing import Optional, List

class TrendRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["fashion_trends"]

    async def create(self, trend_in: FashionTrendCreate) -> dict:
        trend_data = trend_in.model_dump()
        new_trend = FashionTrendModel(**trend_data)
        
        trend_dict = new_trend.model_dump()
        result = await self.collection.insert_one(trend_dict)
        
        trend_dict["_id"] = str(result.inserted_id)
        return trend_dict

    async def get_by_id(self, trend_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(trend_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(trend_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def get_trends_by_category(self, category_id: str) -> List[dict]:
        """Lấy danh sách xu hướng theo danh mục sản phẩm"""
        trends = []
        cursor = self.collection.find({"category_id": category_id}).sort("popularity_score", -1)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            trends.append(doc)
        return trends

    async def get_top_trends(self, limit: int = 10) -> List[dict]:
        """Lấy các xu hướng hot nhất hiện tại"""
        trends = []
        cursor = self.collection.find().sort("popularity_score", -1).limit(limit)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            trends.append(doc)
        return trends

    async def update(self, trend_id: str, trend_in: FashionTrendUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(trend_id):
            return None
            
        update_data = {k: v for k, v in trend_in.model_dump(exclude_unset=True).items() if v is not None}
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(trend_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def delete(self, trend_id: str) -> bool:
        if not ObjectId.is_valid(trend_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(trend_id)})
        return result.deleted_count > 0