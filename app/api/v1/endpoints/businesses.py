from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_database
from app.repositories.business_repository import BusinessRepository
from app.schemas.business_profile import BusinessInterestsUpdate, BusinessInterestsRead
from typing import List

router = APIRouter()

@router.get("/{id}/interests", response_model=BusinessInterestsRead)
async def get_business_interests(id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    repo = BusinessRepository(db)
    interests = await repo.get_interests(id)
    if not interests:
        raise HTTPException(status_code=404, detail="Business not found")
    return interests

@router.put("/{id}/interests", response_model=BusinessInterestsRead)
async def update_business_interests(
    id: str, 
    interests_in: BusinessInterestsUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    repo = BusinessRepository(db)
    updated = await repo.update_interests(id, interests_in.category_ids)
    if not updated:
        raise HTTPException(status_code=404, detail="Business not found")
    return updated