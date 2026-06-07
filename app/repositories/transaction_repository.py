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
        # await self.user_collection.update_one(
        #     {"_id": ObjectId(tx_in.user_id)},
        #     {"$inc": {"available_credits": tx_in.amount}}
        # )

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

    async def get_all_transactions(self, limit: int | None = None) -> List[dict]:
        """Lấy tất cả các bản ghi giao dịch. Nếu `limit` không None thì giới hạn số bản ghi trả về."""
        transactions: List[dict] = []
        cursor = self.collection.find().sort("created_at", -1)
        if limit:
            cursor = cursor.limit(limit)

        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            transactions.append(doc)
        return transactions
    async def get_total_credits_sold(self) -> int:
        """Tính tổng credits đã được bán qua các giao dịch TOP_UP."""
        pipeline = [
            {"$match": {"transaction_type": "TOP_UP"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0]["total"] if result else 0

    async def get_by_id(self, tx_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(tx_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(tx_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc