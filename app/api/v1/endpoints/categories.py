from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_database
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from typing import List

router = APIRouter()

@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(category_in: CategoryCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    # Có thể thêm logic kiểm tra parent_id có tồn tại thật không ở đây
    return await CategoryRepository(db).create(category_in)

@router.get("/", response_model=List[CategoryRead])
async def list_categories(db: AsyncIOMotorDatabase = Depends(get_database)):
    return await CategoryRepository(db).get_all()

@router.get("/{id}", response_model=CategoryRead)
async def get_category(id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    cat = await CategoryRepository(db).get_by_id(id)
    if not cat: raise HTTPException(404, "Category not found")
    return cat

@router.patch("/{id}", response_model=CategoryRead)
async def update_category(id: str, category_in: CategoryUpdate, db: AsyncIOMotorDatabase = Depends(get_database)):
    cat = await CategoryRepository(db).update(id, category_in)
    if not cat: raise HTTPException(404, "Category not found")
    return cat

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    if not await CategoryRepository(db).delete(id):
        raise HTTPException(404, "Category not found")