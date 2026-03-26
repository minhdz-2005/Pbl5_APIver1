from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.schemas.category import CategoryCreate, CategoryUpdate
from typing import List, Optional

class CategoryRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["categories"]

    async def create(self, category_in: CategoryCreate) -> dict:
        category_dict = category_in.model_dump()
        result = await self.collection.insert_one(category_dict)
        category_dict["_id"] = str(result.inserted_id)
        return category_dict

    async def get_all(self) -> List[dict]:
        categories = []
        async for doc in self.collection.find():
            doc["_id"] = str(doc["_id"])
            categories.append(doc)
        return categories

    async def get_by_id(self, category_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(category_id): return None
        doc = await self.collection.find_one({"_id": ObjectId(category_id)})
        if doc: doc["_id"] = str(doc["_id"])
        return doc

    async def update(self, category_id: str, category_in: CategoryUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(category_id): return None
        update_data = {k: v for k, v in category_in.model_dump().items() if v is not None}
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(category_id)},
            {"$set": update_data},
            return_document=True
        )
        if result: result["_id"] = str(result["_id"])
        return result

    async def delete(self, category_id: str) -> bool:
        if not ObjectId.is_valid(category_id): return False
        result = await self.collection.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0