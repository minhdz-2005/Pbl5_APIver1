from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId

from app.core.database import get_database
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis_request import (
    AnalysisRequestCreate, 
    AnalysisRequestRead, 
    AnalysisRequestUpdate,
    RequestStatus
)

router = APIRouter()

# --- 1. TẠO YÊU CẦU PHÂN TÍCH MỚI ---
@router.post("/", response_model=AnalysisRequestRead, status_code=status.HTTP_201_CREATED)
async def create_analysis_request(
    req_in: AnalysisRequestCreate, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Tạo một yêu cầu phân tích mới. 
    Trạng thái mặc định sẽ là 'PENDING' theo Model định nghĩa.
    """
    # Kiểm tra project_id có hợp lệ không
    if not ObjectId.is_valid(req_in.project_id):
        raise HTTPException(status_code=400, detail="project_id không hợp lệ")

    # Kiểm tra Project có tồn tại không
    project = await db["projects"].find_one({"_id": ObjectId(req_in.project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy Project tương ứng")

    repo = AnalysisRepository(db)
    return await repo.create(req_in)

# --- 2. LẤY DANH SÁCH YÊU CẦU THEO PROJECT ---
@router.get("/project/{project_id}", response_model=List[AnalysisRequestRead])
async def list_analysis_requests_by_project(
    project_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lấy toàn bộ lịch sử các phiên phân tích thuộc về một Project cụ thể.
    """
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="project_id không hợp lệ")
        
    repo = AnalysisRepository(db)
    return await repo.get_by_project(project_id)

# --- 3. LẤY CHI TIẾT MỘT YÊU CẦU ---
@router.get("/{req_id}", response_model=AnalysisRequestRead)
async def get_analysis_request(
    req_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lấy thông tin chi tiết và trạng thái hiện tại của một phiên phân tích.
    """
    repo = AnalysisRepository(db)
    req = await repo.get_by_id(req_id)
    
    if not req:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu phân tích")
    return req

# --- 4. CẬP NHẬT TRẠNG THÁI YÊU CẦU ---
@router.patch("/{req_id}/status", response_model=AnalysisRequestRead)
async def update_request_status(
    req_id: str, 
    status_update: RequestStatus, # Truyền trực tiếp enum giá trị mới
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Cập nhật trạng thái của yêu cầu (Ví dụ: PENDING -> CRAWLING -> COMPLETED).
    Hàm này cũng tự động cập nhật trường 'updated_at'.
    """
    repo = AnalysisRepository(db)
    updated_req = await repo.update_status(req_id, status_update)
    
    if not updated_req:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu để cập nhật")
    return updated_req

# --- 5. XÓA YÊU CẦU ---
@router.delete("/{req_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis_request(
    req_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Xóa bỏ một phiên phân tích.
    """
    repo = AnalysisRepository(db)
    success = await repo.delete(req_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Xóa thất bại: Yêu cầu không tồn tại")
    return None

# --- ENDPOINT KHỞI TẠO QUY TRÌNH DISCOVER ---
@router.post("/discover", status_code=status.HTTP_201_CREATED)
async def discover_trends(
    req_in: AnalysisRequestCreate, # Dùng Schema Create bạn đã có
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Khởi tạo một phiên phân tích xu hướng mới (Discover).
    - Tạo bản ghi trong database với trạng thái PENDING.
    - Trả về ID để FE có thể theo dõi (Polling) tiến độ.
    """
    # 1. Kiểm tra ID Project
    if not ObjectId.is_valid(req_in.project_id):
        raise HTTPException(status_code=400, detail="project_id không hợp lệ")
    
    project = await db["projects"].find_one({"_id": ObjectId(req_in.project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Dự án không tồn tại")

    # 2. Tạo bản ghi Request mới bằng Repository
    repo = AnalysisRepository(db)
    new_request = await repo.create(req_in)
    
    # 3. Logic kích hoạt Worker (Ghi chú cho tương lai)
    # Tại đây, sau khi lưu DB, bạn sẽ gửi một tín hiệu (Task) sang 
    # Celery hoặc Redis để con Bot bắt đầu đi cào (Crawl) dữ liệu.
    # Hiện tại chúng ta cứ trả về theo yêu cầu của FE:
    
    return {
        "request_id": new_request["id"], # Hoặc new_request["_id"] tùy repo trả về
        "status": new_request["status"],
        "message": "Đã ghi nhận. AI đang chuẩn bị cào dữ liệu."
    }

# --- ENDPOINT THEO DÕI TRẠNG THÁI (POLLING) ---
@router.get("/{request_id}/status", response_model=dict)
async def get_request_status(
    request_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Endpoint tối giản dành cho FE để cập nhật thanh tiến trình (Progress Bar).
    Chỉ trả về ID và Status để giảm băng thông.
    """
    if not ObjectId.is_valid(request_id):
        raise HTTPException(status_code=400, detail="ID yêu cầu không hợp lệ")

    # Chỉ truy vấn lấy trường status để tối ưu tốc độ
    request_doc = await db["analysis_requests"].find_one(
        {"_id": ObjectId(request_id)},
        {"status": 1} # Projection: Chỉ lấy field status
    )

    if not request_doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu")

    return {
        "request_id": str(request_doc["_id"]),
        "status": request_doc.get("status")
    }

@router.get("/{request_id}/trends", response_model=List[dict])
async def get_request_trend_insights(
    request_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lấy danh sách các ảnh xu hướng (Trend Insights) đã tìm thấy 
    cho một yêu cầu phân tích cụ thể.
    """
    if not ObjectId.is_valid(request_id):
        raise HTTPException(status_code=400, detail="ID yêu cầu không hợp lệ")

    # Kiểm tra xem request này có tồn tại không
    request_exists = await db["analysis_requests"].find_one({"_id": ObjectId(request_id)})
    if not request_exists:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu phân tích")

    # Truy vấn bảng trend_insights để lấy các ảnh xu hướng
    trends = []
    cursor = db["trend_insights"].find({"request_id": request_id})
    
    async for doc in cursor:
        trends.append({
            "id": str(doc["_id"]),
            "image_url": doc.get("source_image_url"),
            "positive_rate": doc.get("positive_rate", 0)
        })

    # Nếu chưa có trend nào (có thể AI vẫn đang xử lý), trả về danh sách rỗng
    return trends

from app.repositories.transaction_repository import TransactionRepository
from app.schemas.credit_transaction import CreditTransactionCreate, TransactionType

@router.post("/{request_id}/generate", status_code=status.HTTP_200_OK)
async def trigger_generation(
    request_id: str,
    data_in: dict, # Nhận selected_trend_ids và target_style_id
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Kích hoạt quy trình tạo ảnh AI:
    1. Kiểm tra số dư credit của User sở hữu project.
    2. Trừ 10 credits.
    3. Cập nhật style và các ảnh trend đã chọn vào Request.
    4. Chuyển trạng thái sang GENERATING_IMAGES.
    """
    if not ObjectId.is_valid(request_id):
        raise HTTPException(status_code=400, detail="ID yêu cầu không hợp lệ")

    # 1. Lấy thông tin Request và Project để biết User là ai
    analysis_req = await db["analysis_requests"].find_one({"_id": ObjectId(request_id)})
    if not analysis_req:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu phân tích")
    
    project = await db["projects"].find_one({"_id": ObjectId(analysis_req["project_id"])})
    user_id = project["user_id"]

    # 2. Kiểm tra số dư của User
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if user.get("available_credits", 0) < 10:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, 
            detail="Bạn không đủ credit để tạo ảnh (Cần 10 credits)"
        )

    # 3. Thực hiện trừ Credit (Sử dụng TransactionRepository)
    tx_repo = TransactionRepository(db)
    tx_create = CreditTransactionCreate(
        user_id=user_id,
        transaction_type=TransactionType.USAGE,
        amount=-10,
        related_request_id=request_id
    )
    await tx_repo.create_transaction(tx_create)

    # 4. Cập nhật Request với Style và Trend đã chọn
    await db["analysis_requests"].update_one(
        {"_id": ObjectId(request_id)},
        {
            "$set": {
                "target_style_id": str(data_in.get("target_style_id")),
                "selected_trend_image_ids": [str(i) for i in data_in.get("selected_trend_ids", [])],
                "status": "GENERATING_IMAGES",
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    # 5. [Ghi chú] Tại đây bạn sẽ gọi sang AI Service để bắt đầu vẽ ảnh
    # ... logic call AI ...

    return {
        "status": "GENERATING_IMAGES",
        "credits_deducted": 10,
        "remaining_credits": user.get("available_credits", 0) - 10
    }

@router.get("/{request_id}/results", response_model=dict)
async def get_analysis_results(
    request_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lấy kết quả cuối cùng của phiên phân tích bao gồm:
    - trend_summary: Dữ liệu thống kê để vẽ biểu đồ.
    - generated_designs: Danh sách các mẫu thiết kế do AI tạo ra.
    """
    if not ObjectId.is_valid(request_id):
        raise HTTPException(status_code=400, detail="ID yêu cầu không hợp lệ")

    # 1. Kiểm tra Request có tồn tại không
    analysis_req = await db["analysis_requests"].find_one({"_id": ObjectId(request_id)})
    if not analysis_req:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu phân tích")

    # 2. Lấy dữ liệu trend_summary (Dựa trên Trend_Insight)
    # Ở đây mình giả sử bạn muốn thống kê tỷ lệ tích cực trung bình hoặc danh sách sản phẩm hot
    trend_insights_cursor = db["trend_insights"].find({"request_id": request_id})
    insights = []
    avg_positive = 0
    total_reviews = 0
    
    async for insight in trend_insights_cursor:
        insights.append({
            "product_name": insight.get("product_name"),
            "positive_rate": insight.get("positive_rate"),
            "total_reviews": insight.get("total_reviews")
        })
        avg_positive += insight.get("positive_rate", 0)
        total_reviews += insight.get("total_reviews", 0)

    # Tính toán sơ bộ cho trend_summary (FE dùng vẽ chart)
    trend_summary = {
        "total_analyzed": len(insights),
        "average_positive_rate": round(avg_positive / len(insights), 2) if insights else 0,
        "total_market_reviews": total_reviews,
        "details": insights
    }

    # 3. Lấy danh sách ảnh AI đã tạo từ bảng generated_designs
    designs = []
    designs_cursor = db["generated_designs"].find({"request_id": request_id})
    async for design in designs_cursor:
        designs.append({
            "id": str(design["_id"]),
            "image_url": design.get("design_image_url"),
            "user_rating": design.get("user_rating")
        })

    # 4. Trả về kết quả tổng hợp
    return {
        "trend_summary": trend_summary,
        "generated_designs": designs
    }