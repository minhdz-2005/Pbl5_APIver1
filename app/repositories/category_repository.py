from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.category import CategoryModel
from app.schemas.category import CategoryCreate, CategoryUpdate
from bson import ObjectId
from typing import Optional, List

class CategoryRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["categories"]

    async def create(self, cat_in: CategoryCreate) -> dict:
        cat_data = cat_in.model_dump()
        
        # Kiểm tra parent_id hợp lệ nếu có
        if cat_data.get("parent_id") and not ObjectId.is_valid(cat_data["parent_id"]):
             cat_data["parent_id"] = None
             
        new_cat = CategoryModel(**cat_data)
        cat_dict = new_cat.model_dump()
        
        result = await self.collection.insert_one(cat_dict)
        cat_dict["_id"] = str(result.inserted_id)
        return cat_dict

    async def get_all_roots(self) -> List[dict]:
        """Lấy tất cả danh mục gốc (không có parent_id)"""
        categories = []
        cursor = self.collection.find({"parent_id": None})
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            categories.append(doc)
        return categories

    async def get_children(self, parent_id: str) -> List[dict]:
        """Lấy các danh mục con của một danh mục cụ thể"""
        categories = []
        cursor = self.collection.find({"parent_id": parent_id})
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            categories.append(doc)
        return categories

    async def get_by_id(self, cat_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(cat_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(cat_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def update(self, cat_id: str, cat_in: CategoryUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(cat_id):
            return None
            
        update_data = {k: v for k, v in cat_in.model_dump(exclude_unset=True).items() if v is not None}
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(cat_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def delete(self, cat_id: str) -> bool:
        """Xóa danh mục (Lưu ý: Bạn có thể cần xử lý xóa các con của nó hoặc set null parent_id của các con)"""
        if not ObjectId.is_valid(cat_id):
            return False
            
        # Optional: Cập nhật các con của nó thành root hoặc xóa luôn tùy logic dự án
        await self.collection.update_many({"parent_id": cat_id}, {"$set": {"parent_id": None}})
        
        result = await self.collection.delete_one({"_id": ObjectId(cat_id)})
        return result.deleted_count > 0