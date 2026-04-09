from fastapi import APIRouter
from app.api.v2.endpoints import login, users

api_router = APIRouter()

# Đăng ký các router lẻ vào Big Router
api_router.include_router(login.router, prefix="/auth", tags=["Authentication V2"])
api_router.include_router(users.router, prefix="/users", tags=["Users V2"])