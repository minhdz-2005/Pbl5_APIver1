from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_database
from app.repositories.business_repository import BusinessRepository
from app.schemas.business_profile import BusinessProfileCreate, BusinessProfileRead, BusinessProfileUpdate, BusinessInterestsUpdate, BusinessInterestsRead
from typing import List

router = APIRouter()

@router.post("/", response_model=BusinessProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(profile_in: BusinessProfileCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    return await BusinessRepository(db).create(profile_in)

@router.get("/", response_model=List[BusinessProfileRead])
async def list_profiles(db: AsyncIOMotorDatabase = Depends(get_database)):
    return await BusinessRepository(db).get_all()

@router.get("/{id}", response_model=BusinessProfileRead)
async def get_profile(id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    profile = await BusinessRepository(db).get_by_id(id)
    if not profile: raise HTTPException(404, "Profile not found")
    return profile

@router.put("/{id}", response_model=BusinessProfileRead)
async def replace_profile(id: str, profile_in: BusinessProfileUpdate, db: AsyncIOMotorDatabase = Depends(get_database)):
    # PUT thường dùng để thay thế toàn bộ dữ liệu
    profile = await BusinessRepository(db).update(id, profile_in, replace=True)
    if not profile: raise HTTPException(404, "Profile not found")
    return profile

@router.patch("/{id}", response_model=BusinessProfileRead)
async def update_profile(id: str, profile_in: BusinessProfileUpdate, db: AsyncIOMotorDatabase = Depends(get_database)):
    profile = await BusinessRepository(db).update(id, profile_in, replace=False)
    if not profile: raise HTTPException(404, "Profile not found")
    return profile

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    if not await BusinessRepository(db).delete(id):
        raise HTTPException(404, "Profile not found")