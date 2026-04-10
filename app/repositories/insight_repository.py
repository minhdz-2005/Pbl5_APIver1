from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.trend_insight import TrendInsightModel
from app.schemas.trend_insight import TrendInsightCreate
from bson import ObjectId
from typing import List, Optional

class InsightRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["trend_insights"]

    async def create(self, insight_in: TrendInsightCreate) -> dict:
        insight_data = insight_in.model_dump()
        new_insight = TrendInsightModel(**insight_data)
        
        insight_dict = new_insight.model_dump()
        result = await self.collection.insert_one(insight_dict)
        
        insight_dict["_id"] = str(result.inserted_id)
        return insight_dict

    async def create_many(self, insights_in: List[TrendInsightCreate]) -> int:
        """Lưu hàng loạt kết quả insight sau khi AI phân tích xong một request"""
        if not insights_in:
            return 0
        documents = [TrendInsightModel(**i.model_dump()).model_dump() for i in insights_in]
        result = await self.collection.insert_many(documents)
        return len(result.inserted_ids)

    async def get_by_request(self, request_id: str) -> List[dict]:
        """Lấy tất cả các kết quả insight của một phiên phân tích"""
        insights = []
        cursor = self.collection.find({"request_id": request_id})
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            insights.append(doc)
        return insights

    async def get_by_id(self, insight_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(insight_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(insight_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def delete_by_request(self, request_id: str) -> bool:
        """Xóa các insight liên quan khi request bị xóa"""
        result = await self.collection.delete_many({"request_id": request_id})
        return result.deleted_count > 0