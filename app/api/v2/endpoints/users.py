from fastapi import APIRouter, Depends, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from app.core.security import get_current_user # Hàm lấy user từ token
from app.core.database import get_database
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    repo = UserRepository(db)
    
    # 1. Logic kiểm tra trùng lặp
    if await repo.check_email_exists(user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được đăng ký trên hệ thống"
        )
    
    if await repo.check_username_exists(user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên người dùng đã tồn tại"
        )
    
    # 2. Tạo User (Repo v2 nên gán mặc định available_credits = 0 hoặc theo gói)
    new_user = await repo.create(user_in)
    
    # [Tư duy SDET]: Ở đây có thể thêm logic tạo Business_Profile mặc định 
    # để đảm bảo tính toàn vẹn dữ liệu cho v2
    return new_user

@router.get("/", response_model=List[UserRead])
async def list_users(db: AsyncIOMotorDatabase = Depends(get_database)):
    repo = UserRepository(db)
    return await repo.get_all()

@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy người dùng"
        )
    return user

@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str, 
    user_in: UserUpdate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Cập nhật thông tin User bao gồm cả số dư credits
    """
    repo = UserRepository(db)
    
    # Trước khi update, có thể kiểm tra xem ID có hợp lệ không
    updated_user = await repo.update(user_id, user_in)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Cập nhật thất bại: User không tồn tại"
        )
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    repo = UserRepository(db)
    
    # [Tư duy SDET]: Khi xóa User, cần cân nhắc xóa luôn Business_Profile (Cascade Delete)
    # Bạn có thể thực hiện việc này trong Repository để sạch code ở Controller
    success = await repo.delete(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy User để xóa"
        )
    return None

@router.get("/me")
async def get_my_info(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user) # Xác thực token tại đây
):
    """
    Lấy thông tin chi tiết của người dùng hiện tại (v2)
    """
    try:
        user_id = str(current_user["_id"])
        
        # 1. Lấy thêm thông tin Business Profile để có company_name
        business_profile = await db["business_profiles"].find_one({"user_id": user_id})
        
        # 2. Lấy lại token từ Header (để trả về theo yêu cầu của bạn)
        auth_header = request.headers.get("Authorization")
        token = auth_header.split(" ")[1] if auth_header else None

        # 3. Format Response đúng yêu cầu
        return {
            "token": token,
            "user": {
                "id": user_id,
                "email": current_user["email"],
                "company_name": business_profile.get("company_name") if business_profile else None,
                "available_credits": current_user.get("available_credits", 0),
                "role": current_user.get("role", "user")
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy thông tin người dùng: {str(e)}"
        )