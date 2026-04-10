from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.generated_design import GeneratedDesignModel
from app.schemas.generated_design import GeneratedDesignCreate, GeneratedDesignUpdate
from bson import ObjectId
from typing import List, Optional

class DesignRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["generated_designs"]

    async def create(self, design_in: GeneratedDesignCreate) -> dict:
        design_data = design_in.model_dump()
        new_design = GeneratedDesignModel(**design_data)
        
        design_dict = new_design.model_dump()
        result = await self.collection.insert_one(design_dict)
        
        design_dict["_id"] = str(result.inserted_id)
        return design_dict

    async def get_by_request(self, request_id: str) -> List[dict]:
        """Lấy tất cả các mẫu thiết kế được tạo ra trong một phiên phân tích"""
        designs = []
        cursor = self.collection.find({"request_id": request_id})
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            designs.append(doc)
        return designs

    async def update_rating(self, design_id: str, rating: int) -> Optional[dict]:
        """Cập nhật đánh giá của người dùng cho mẫu thiết kế"""
        if not ObjectId.is_valid(design_id):
            return None

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(design_id)},
            {"$set": {"user_rating": rating}},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def get_by_id(self, design_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(design_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(design_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc