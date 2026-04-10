from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.business_profile import BusinessProfileModel
from app.schemas.business_profile import BusinessProfileCreate, BusinessProfileUpdate
from bson import ObjectId
from datetime import datetime, timezone
from typing import Optional, List

class BusinessRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["business_profiles"]

    async def create(self, profile_in: BusinessProfileCreate) -> dict:
        profile_data = profile_in.model_dump()
        
        # Tạo model để lấy các giá trị mặc định
        new_profile = BusinessProfileModel(
            **profile_data,
            updated_at=datetime.now(timezone.utc)
        )
        
        profile_dict = new_profile.model_dump()
        result = await self.collection.insert_one(profile_dict)
        
        profile_dict["_id"] = str(result.inserted_id)
        return profile_dict

    async def get_by_user_id(self, user_id: str) -> Optional[dict]:
        # Tìm profile dựa trên user_id của bảng users
        profile = await self.collection.find_one({"user_id": user_id})
        if profile:
            profile["_id"] = str(profile["_id"])
        return profile

    async def get_by_id(self, profile_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(profile_id):
            return None
        
        profile = await self.collection.find_one({"_id": ObjectId(profile_id)})
        if profile:
            profile["_id"] = str(profile["_id"])
        return profile

    async def update_by_user_id(self, user_id: str, profile_in: BusinessProfileUpdate) -> Optional[dict]:
        update_data = {k: v for k, v in profile_in.model_dump(exclude_unset=True).items() if v is not None}
        
        if not update_data:
            return await self.get_by_user_id(user_id)
            
        update_data["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.find_one_and_update(
            {"user_id": user_id},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def delete_by_user_id(self, user_id: str) -> bool:
        result = await self.collection.delete_one({"user_id": user_id})
        return result.deleted_count > 0