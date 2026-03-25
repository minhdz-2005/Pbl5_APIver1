from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import UserModel
from app.schemas.user import UserCreate
from passlib.context import CryptContext
from datetime import datetime
from bson import ObjectId
from app.schemas.user import UserUpdate
from typing import Optional

# Thiết lập công cụ mã hóa mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    async def create(self, user_in: UserCreate) -> dict:
        # 1. Chuyển đổi Schema sang dict và mã hóa mật khẩu
        user_data = user_in.model_dump()
        password = str(user_data.pop("password")) # Đảm bảo là string
        
        user_dict = UserModel(
            **user_data,
            password_hash=self.hash_password(password),
            created_at=datetime.utcnow()
        ).model_dump()

        # 2. Lưu vào MongoDB
        result = await self.collection.insert_one(user_dict)
        
        # 3. Trả về document đã tạo (kèm ID)
        user_dict["_id"] = str(result.inserted_id)
        return user_dict

    async def get_all(self):
        users = []
        cursor = self.collection.find()
        async for document in cursor:
            document["_id"] = str(document["_id"])
            users.append(document)
        return users
    
    async def get_by_id(self, user_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(user_id):
            return None
        
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user

    async def update(self, user_id: str, user_in: UserUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(user_id):
            return None

        # Chỉ lấy các field có giá trị (không None) để cập nhật
        update_data = {k: v for k, v in user_in.model_dump().items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(user_id)

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True # Trả về document sau khi đã update
        )
        
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def delete(self, user_id: str) -> bool:
        """
        Xóa một user theo ID. 
        Trả về True nếu xóa thành công, False nếu không tìm thấy ID.
        """
        if not ObjectId.is_valid(user_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        
        # result.deleted_count sẽ bằng 1 nếu tìm thấy và xóa thành công
        return result.deleted_count > 0