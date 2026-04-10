from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.credit_transaction import CreditTransactionModel
from app.schemas.credit_transaction import CreditTransactionCreate
from bson import ObjectId
from typing import List, Optional
from datetime import datetime, timezone

class TransactionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["credit_transactions"]
        self.user_collection = db["users"]

    async def create_transaction(self, tx_in: CreditTransactionCreate) -> dict:
        """
        Tạo transaction và cập nhật số dư của User.
        Lưu ý: MongoDB hỗ trợ ACID transaction nhưng yêu cầu chạy Replica Set.
        Ở đây mình sẽ dùng update_one với $inc để đảm bảo tính chính xác.
        """
        tx_data = tx_in.model_dump()
        new_tx = CreditTransactionModel(**tx_data)
        tx_dict = new_tx.model_dump()

        # 1. Lưu bản ghi kiểm toán
        result = await self.collection.insert_one(tx_dict)
        tx_dict["_id"] = str(result.inserted_id)

        # 2. Cập nhật available_credits ở bảng User bằng toán tử $inc
        # amount có thể âm (USAGE) hoặc dương (TOP_UP)
        await self.user_collection.update_one(
            {"_id": ObjectId(tx_in.user_id)},
            {"$inc": {"available_credits": tx_in.amount}}
        )

        return tx_dict

    async def get_history_by_user(self, user_id: str, limit: int = 50) -> List[dict]:
        """Lấy lịch sử giao dịch của một User"""
        transactions = []
        cursor = self.collection.find({"user_id": user_id})\
                                .sort("created_at", -1)\
                                .limit(limit)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            transactions.append(doc)
        return transactions

    async def get_by_id(self, tx_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(tx_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(tx_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc