from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.subscription_plan import SubscriptionPlanModel
from app.schemas.subscription_plan import SubscriptionPlanCreate, SubscriptionPlanUpdate
from bson import ObjectId
from typing import List, Optional

class SubscriptionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["subscription_plans"]

    async def create(self, plan_in: SubscriptionPlanCreate) -> dict:
        plan_data = plan_in.model_dump()
        new_plan = SubscriptionPlanModel(**plan_data)
        
        plan_dict = new_plan.model_dump()
        result = await self.collection.insert_one(plan_dict)
        
        plan_dict["_id"] = str(result.inserted_id)
        return plan_dict

    async def get_all(self) -> List[dict]:
        plans = []
        cursor = self.collection.find()
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            plans.append(doc)
        return plans

    async def get_by_name(self, plan_name: str) -> Optional[dict]:
        doc = await self.collection.find_one({"plan_name": plan_name})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def update(self, plan_id: str, plan_in: SubscriptionPlanUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(plan_id):
            return None
            
        update_data = {k: v for k, v in plan_in.model_dump(exclude_unset=True).items() if v is not None}
        
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(plan_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def delete(self, plan_id: str) -> bool:
        if not ObjectId.is_valid(plan_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(plan_id)})
        return result.deleted_count > 0