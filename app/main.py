import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.v1.endpoints import users, business_profiles, businesses, categories  # Import router 


# 1. Định nghĩa Lifespan handler (Quản lý startup/shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [Startup]: Kết nối DB khi app khởi động
    try:
        await connect_to_mongo()
        print("MDB: Connected successfully via Lifespan")
    except Exception as e:
        print(f"MDB: connection error: {e}")
    
    yield  # App đang chạy...
    
    # [Shutdown]: Đóng kết nối khi app tắt
    await close_mongo_connection()
    print("MDB: Connection closed via Lifespan")

# 2. Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# 3. Đăng ký các Router (Endpoints)
# Prefix này sẽ gộp với prefix trong router của users (nếu có)
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(business_profiles.router, prefix=f"{settings.API_V1_STR}/business-profile", tags=["Business Profile"])
app.include_router(businesses.router, prefix=f"{settings.API_V1_STR}/businesses", tags=["Businesses"])
app.include_router(categories.router, prefix=f"{settings.API_V1_STR}/categories", tags=["Categories"])

# 4. Route kiểm tra nhanh tại trang chủ
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "status": "running",
        "docs": "/docs"
    }

# 5. Để chạy trực tiếp bằng lệnh: python app/main.py
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)