from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.project import ProjectModel
from app.schemas.project import ProjectCreate, ProjectUpdate
from bson import ObjectId
from typing import List, Optional
from datetime import datetime, timezone

class ProjectRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["projects"]

    async def create(self, user_id: str, project_in: ProjectCreate) -> dict:
        project_data = project_in.model_dump()
        new_project = ProjectModel(
            user_id=user_id,
            **project_data
        )
        
        project_dict = new_project.model_dump()
        result = await self.collection.insert_one(project_dict)
        
        project_dict["_id"] = str(result.inserted_id)
        return project_dict

    async def get_by_user(self, user_id: str) -> List[dict]:
        """Lấy tất cả các project của một người dùng cụ thể"""
        projects = []
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            projects.append(doc)
        return projects

    async def get_by_id(self, project_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(project_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(project_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def update(self, project_id: str, project_in: ProjectUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(project_id):
            return None
            
        update_data = {k: v for k, v in project_in.model_dump(exclude_unset=True).items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(project_id)

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(project_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def delete(self, project_id: str) -> bool:
        """
        Xóa Project. 
        Lưu ý: Bạn nên có logic xử lý các bản ghi liên quan (như Trend_Requests) 
        khi project bị xóa.
        """
        if not ObjectId.is_valid(project_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(project_id)})
        return result.deleted_count > 0