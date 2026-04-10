from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.analysis_request import AnalysisRequestModel
from app.schemas.analysis_request import AnalysisRequestCreate, AnalysisRequestUpdate
from bson import ObjectId
from typing import List, Optional
from datetime import datetime, timezone

class AnalysisRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["analysis_requests"]

    async def create(self, req_in: AnalysisRequestCreate) -> dict:
        req_data = req_in.model_dump()
        new_req = AnalysisRequestModel(**req_data)
        
        req_dict = new_req.model_dump()
        result = await self.collection.insert_one(req_dict)
        
        req_dict["_id"] = str(result.inserted_id)
        return req_dict

    async def get_by_project(self, project_id: str) -> List[dict]:
        """Lấy danh sách các phiên phân tích trong một Project"""
        requests = []
        cursor = self.collection.find({"project_id": project_id}).sort("created_at", -1)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            requests.append(doc)
        return requests

    async def get_by_id(self, req_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(req_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(req_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def update_status(self, req_id: str, status: str) -> Optional[dict]:
        """Cập nhật trạng thái và thời gian updated_at"""
        if not ObjectId.is_valid(req_id):
            return None

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(req_id)},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.now(timezone.utc)
                }
            },
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def delete(self, req_id: str) -> bool:
        if not ObjectId.is_valid(req_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(req_id)})
        return result.deleted_count > 0