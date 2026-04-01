import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_to_mongo():
    """Khởi tạo kết nối khi App bắt đầu"""
    db.client = AsyncIOMotorClient(
        settings.MONGO_DETAILS,
        tls=True,
        tlsCAFile=certifi.where()
    )
    # Kiểm tra kết nối
    await db.client.admin.command('ping')
    
    # Tạo unique indexes cho users collection
    await setup_indexes()

async def setup_indexes():
    """Tạo các indexes cho database"""
    database = db.client[settings.DATABASE_NAME]
    users_collection = database["users"]
    
    # Tạo unique index cho email (case-insensitive)
    await users_collection.create_index(
        "email",
        unique=True,
        collation={"locale": "en", "strength": 2}  # Case-insensitive
    )
    
    # Tạo unique index cho username (case-insensitive)
    await users_collection.create_index(
        "username",
        unique=True,
        collation={"locale": "en", "strength": 2}  # Case-insensitive
    )

async def close_mongo_connection():
    """Đóng kết nối khi App tắt"""
    if db.client:
        db.client.close()

def get_database():
    """
    Dependency dùng để inject vào các Router sau này.
    Nó sẽ trả về database instance cụ thể (ví dụ: 'my_app_db')
    """
    return db.client[settings.DATABASE_NAME]