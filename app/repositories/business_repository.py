from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.business_profile import BusinessProfileModel
from app.schemas.business_profile import BusinessProfileCreate, BusinessProfileUpdate
from typing import List, Optional

class BusinessRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["business_profiles"]

    async def create(self, profile_in: BusinessProfileCreate) -> dict:
        profile_dict = profile_in.model_dump()
        result = await self.collection.insert_one(profile_dict)
        profile_dict["_id"] = str(result.inserted_id)
        return profile_dict

    async def get_all(self) -> List[dict]:
        profiles = []
        async for doc in self.collection.find():
            doc["_id"] = str(doc["_id"])
            profiles.append(doc)
        return profiles

    async def get_by_id(self, profile_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(profile_id): return None
        doc = await self.collection.find_one({"_id": ObjectId(profile_id)})
        if doc: doc["_id"] = str(doc["_id"])
        return doc

    async def update(self, profile_id: str, profile_in: BusinessProfileUpdate, replace: bool = False) -> Optional[dict]:
        if not ObjectId.is_valid(profile_id): return None
        
        update_data = profile_in.model_dump(exclude_unset=not replace)
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(profile_id)},
            {"$set": update_data},
            return_document=True
        )
        if result: result["_id"] = str(result["_id"])
        return result

    async def delete(self, profile_id: str) -> bool:
        if not ObjectId.is_valid(profile_id): return False
        result = await self.collection.delete_one({"_id": ObjectId(profile_id)})
        return result.deleted_count > 0
    
    async def get_interests(self, business_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(business_id): return None
        # Chỉ lấy trường interest_categories để tối ưu
        doc = await self.collection.find_one(
            {"_id": ObjectId(business_id)},
            {"interest_categories": 1}
        )
        if doc:
            return {
                "business_id": str(doc["_id"]),
                "category_ids": doc.get("interest_categories", [])
            }
        return None

    async def update_interests(self, business_id: str, category_ids: List[str]) -> Optional[dict]:
        if not ObjectId.is_valid(business_id): return None
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(business_id)},
            {"$set": {"interest_categories": category_ids}},
            return_document=True
        )
        if result:
            return {
                "business_id": str(result["_id"]),
                "category_ids": result.get("interest_categories", [])
            }
        return None