from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import UserModel
from app.schemas.user import UserCreate, UserUpdate
from passlib.context import CryptContext
from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional, List

# Thiết lập mã hóa mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    async def check_email_exists(self, email: str) -> bool:
        user = await self.collection.find_one({"email": email})
        return user is not None

    async def check_username_exists(self, username: str) -> bool:
        user = await self.collection.find_one({"username": username})
        return user is not None

    async def create(self, user_in: UserCreate) -> dict:
        user_data = user_in.model_dump()
        password = str(user_data.pop("password"))
        
        # Khởi tạo model với các giá trị mặc định theo yêu cầu mới
        new_user = UserModel(
            **user_data,
            password_hash=self.hash_password(password),
            available_credits=10, # Mặc định tặng 10 credits
            created_at=datetime.now(timezone.utc)
        )
        
        user_dict = new_user.model_dump()
        result = await self.collection.insert_one(user_dict)
        
        user_dict["_id"] = str(result.inserted_id)
        return user_dict

    async def get_by_id(self, user_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(user_id):
            return None
        
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user

    async def get_by_email(self, email: str) -> Optional[dict]:
        user = await self.collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user

    async def get_all(self) -> List[dict]:
        users = []
        async for user in self.collection.find():
            user["_id"] = str(user["_id"])
            users.append(user)
        return users

    async def update(self, user_id: str, user_in: UserUpdate) -> Optional[dict]:
        if not ObjectId.is_valid(user_id):
            return None

        # Loại bỏ các giá trị None để tránh ghi đè dữ liệu cũ bằng null
        update_data = {k: v for k, v in user_in.model_dump(exclude_unset=True).items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(user_id)

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True 
        )
        
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def delete(self, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0