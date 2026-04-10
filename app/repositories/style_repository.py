from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.style_preset import StylePresetModel
from app.schemas.style_preset import StylePresetCreate, StylePresetUpdate
from bson import ObjectId
from typing import List, Optional

class StyleRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["style_presets"]

    async def create(self, style_in: StylePresetCreate) -> dict:
        style_data = style_in.model_dump()
        new_style = StylePresetModel(**style_data)
        
        style_dict = new_style.model_dump()
        result = await self.collection.insert_one(style_dict)
        
        style_dict["_id"] = str(result.inserted_id)
        return style_dict

    async def get_all(self) -> List[dict]:
        """Lấy danh sách tất cả phong cách để hiển thị lên UI cho user chọn"""
        styles = []
        cursor = self.collection.find().sort("display_name", 1)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            styles.append(doc)
        return styles

    async def get_by_id(self, style_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(style_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(style_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def update(self, style_id: str, style_in: StylePresetUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(style_id):
            return None
        
        update_data = {k: v for k, v in style_in.model_dump(exclude_unset=True).items() if v is not None}
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(style_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def delete(self, style_id: str) -> bool:
        if not ObjectId.is_valid(style_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(style_id)})
        return result.deleted_count > 0