from fastapi import APIRouter
from app.api.v1.endpoints import users, business_profiles, categories, businesses

api_router = APIRouter()

# Đăng ký các router lẻ vào Big Router
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(business_profiles.router, prefix="/business-profile", tags=["Business Profile"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["Businesses"])