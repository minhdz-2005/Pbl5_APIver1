from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.business_product import BusinessProductModel
from app.schemas.business_product import BusinessProductCreate, BusinessProductUpdate
from bson import ObjectId
from typing import Optional, List
from datetime import datetime, timezone

class ProductRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["business_products"]

    async def create(self, product_in: BusinessProductCreate) -> dict:
        product_data = product_in.model_dump()
        new_product = BusinessProductModel(**product_data)
        
        product_dict = new_product.model_dump()
        result = await self.collection.insert_one(product_dict)
        
        product_dict["_id"] = str(result.inserted_id)
        return product_dict

    async def get_by_business(self, business_id: str) -> List[dict]:
        """Lấy toàn bộ sản phẩm của một doanh nghiệp"""
        products = []
        cursor = self.collection.find({"business_id": business_id})
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            products.append(doc)
        return products

    async def get_by_id(self, product_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(product_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(product_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def update(self, product_id: str, product_in: BusinessProductUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(product_id):
            return None
            
        update_data = {k: v for k, v in product_in.model_dump(exclude_unset=True).items() if v is not None}
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(product_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def delete(self, product_id: str) -> bool:
        if not ObjectId.is_valid(product_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count > 0