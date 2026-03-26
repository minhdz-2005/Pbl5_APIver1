import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.v1.router import api_router


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
app.include_router(api_router, prefix=settings.API_V1_STR)

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