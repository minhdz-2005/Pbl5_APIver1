from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId

from app.core.database import get_database
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter()

# --- 1. TẠO PROJECT MỚI ---
@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    user_id: str, # Tạm thời truyền user_id trực tiếp để test thay vì lấy từ token
    project_in: ProjectCreate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Tạo một project mới cho người dùng.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")
        
    repo = ProjectRepository(db)
    # ProjectRepository.create yêu cầu user_id và dữ liệu project
    new_project = await repo.create(user_id=user_id, project_in=project_in)
    return new_project

# --- 2. LẤY DANH SÁCH PROJECT CỦA MỘT USER ---
@router.get("/user/{user_id}", response_model=List[ProjectRead])
async def list_user_projects(
    user_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lấy toàn bộ danh sách project của một người dùng.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")
        
    repo = ProjectRepository(db)
    # Trả về danh sách project sắp xếp theo thời gian mới nhất
    return await repo.get_by_user(user_id)

# --- 3. LẤY CHI TIẾT MỘT PROJECT ---
@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lấy thông tin chi tiết của một project cụ thể.
    """
    repo = ProjectRepository(db)
    project = await repo.get_by_id(project_id) #
    
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy project")
    return project

# --- 4. CẬP NHẬT PROJECT ---
@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str, 
    project_in: ProjectUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Cập nhật tên hoặc mô tả của project.
    """
    repo = ProjectRepository(db)
    # Loại bỏ các giá trị None trước khi update
    updated_project = await repo.update(project_id, project_in)
    
    if not updated_project:
        raise HTTPException(status_code=404, detail="Cập nhật thất bại: Project không tồn tại")
    return updated_project

# --- 5. XÓA PROJECT ---
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Xóa bỏ một project.
    """
    repo = ProjectRepository(db)
    success = await repo.delete(project_id) #
    
    if not success:
        raise HTTPException(status_code=404, detail="Xóa thất bại: Project không tồn tại")
    return None

@router.get("/{project_id}/requests", response_model=dict)
async def get_project_requests_summary(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Endpoint tổng hợp: Lấy thông tin Project kèm danh sách chi tiết các Request bên trong.
    """
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="ID dự án không hợp lệ")

    # 1. Lấy thông tin Project
    project = await db["projects"].find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án")

    # 2. Lấy danh sách Requests thuộc project này
    requests_cursor = db["analysis_requests"].find({"project_id": project_id}).sort("created_at", -1)
    
    detailed_requests = []
    async for req in requests_cursor:
        req_id_str = str(req["_id"])
        
        # Lấy tên Style từ bảng style_presets
        style_name = "N/A"
        if req.get("target_style_id"):
            style = await db["style_presets"].find_one({"_id": ObjectId(req["target_style_id"])})
            if style:
                style_name = style.get("display_name")

        # Lấy ảnh thumbnail từ bảng generated_designs (lấy ảnh đầu tiên tìm thấy)
        thumb_url = None
        design = await db["generated_designs"].find_one({"request_id": req_id_str})
        if design:
            thumb_url = design.get("design_image_url")

        detailed_requests.append({
            "request_id": req_id_str,
            "category_name": req.get("category_name"),
            "style_name": style_name,
            "status": req.get("status"),
            "created_at": req.get("created_at"),
            "result_thumbnail_url": thumb_url
        })

    # 3. Trả về cấu trúc đúng như FE yêu cầu
    return {
        "project_id": str(project["_id"]),
        "project_name": project.get("project_name"),
        "total_requests": len(detailed_requests),
        "requests": detailed_requests
    }