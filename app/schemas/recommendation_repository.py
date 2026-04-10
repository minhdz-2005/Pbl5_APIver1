from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.recommendation import RecommendationModel
from app.schemas.recommendation import RecommendationCreate
from bson import ObjectId
from typing import List, Optional

class RecommendationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["recommendations"]

    async def create(self, rec_in: RecommendationCreate) -> dict:
        rec_data = rec_in.model_dump()
        new_rec = RecommendationModel(**rec_data)
        
        rec_dict = new_rec.model_dump()
        result = await self.collection.insert_one(rec_dict)
        
        rec_dict["_id"] = str(result.inserted_id)
        return rec_dict

    async def get_by_business(self, business_id: str, limit: int = 20) -> List[dict]:
        """Lấy các gợi ý mới nhất dành cho một doanh nghiệp cụ thể"""
        recommendations = []
        cursor = self.collection.find({"business_id": business_id})\
                                 .sort("created_at", -1)\
                                 .limit(limit)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            recommendations.append(doc)
        return recommendations

    async def get_by_id(self, rec_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(rec_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(rec_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def delete_old_recommendations(self, business_id: str):
        """Xóa các gợi ý cũ khi có đợt phân tích mới (Tránh gây nhiễu)"""
        await self.collection.delete_many({"business_id": business_id})