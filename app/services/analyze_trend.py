import logging
import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis_request import RequestStatus
from app.core.config import settings

# Cấu hình log để tiện theo dõi tiến trình chạy ngầm
logger = logging.getLogger(__name__)

async def background_analyze_trend(request_id: str, db: AsyncIOMotorDatabase):
    """
    Hàm chạy ngầm xử lý quy trình phân tích AI:
    1. Chuyển trạng thái sang ANALYZING_AI.
    2. Thu thập dữ liệu liên quan từ DB (Trend Insights / Products) để chuẩn bị payload.
    3. Gửi request POST tới AI Webserver.
    4. Cập nhật kết quả: Thành công -> COMPLETED, Thất bại -> FAILED.
    """
    repo = AnalysisRepository(db)
    
    try:
        # Bước 1: Cập nhật trạng thái thành ANALYZING_AI
        logger.info(f"Starting AI Analysis for request: {request_id}. Setting status to ANALYZING_AI.")
        await repo.update_status(request_id, RequestStatus.ANALYZING_AI.value)
        
        # Lấy thông tin chi tiết của Request hiện tại
        analysis_req = await repo.get_by_id(request_id)
        if not analysis_req:
            logger.error(f"Request {request_id} not found in database.")
            return

        # --- BƯỚC CHUẨN BỊ PAYLOAD ---
        # Ở đây mình giả định bạn lấy dữ liệu sản phẩm thô đã cào được từ bảng `trend_insights`
        # Nếu ở bước trước (CRAWLING) bạn lưu sản phẩm vào đâu thì truy vấn ở bảng đó.
        # Mẫu payload sản phẩm mà AI Server cần có thể là:
        products_payload = [
            {
                "product_id": "2227605234",
                "title": "Vest nam, Áo vets nam chất liệu KAKI thô dày dặn, ít nhăn, ít nhàu. Kiếu dáng tay lỡ trẻ trung năng động. sang trọng. Vừa đi chơi, vừa đi làm. T18",
                "image_url": "https://img.lazcdn.com/g/ff/kf/S9a0617ab39034ee48328bc9fcb3b2514y.jpg_720x720q80.jpg_.webp",
                "positive_rate": 0.77,
                "total_reviews": 39
            },
            {
                "product_id": "2322178340",
                "title": "Secondhand Blazer (Vest) - [Free Shipping] - Vintage, Classic, Unisex - (Inbox Shop for Size Advice)",
                "image_url": "https://img.lazcdn.com/g/p/06c3c790ae2ca006fee307dcbccdcdc1.png_720x720q80.png_.webp",
                "positive_rate": 0.82,
                "total_reviews": 22
            }
        ]
        # cursor = db["trend_insights"].find({"request_id": request_id})
        # async for doc in cursor:
        #     products_payload.append({
        #         "product_name": doc.get("product_name", "Unknown Product"),
        #         "image_url": doc.get("source_image_url", ""),
        #         # Nếu cấu trúc dữ liệu của bạn có mảng reviews thì map vào, không thì để mảng rỗng
        #         "reviews": doc.get("reviews", ["Sản phẩm mặc định, đánh giá tốt"]) 
        #     })

        # Xây dựng cấu trúc Request Body đúng như AI Webserver yêu cầu
        payload = {
            "request_id": request_id,
            "category_keyword": analysis_req.get("category_name"),
            "products": products_payload,
            "limit": 5
        }

        # Bước 2: Gửi request tới AI Webserver với timeout hợp lý (vì xử lý AI thường lâu)
        logger.info(f"Sending payload to AI server for request {request_id}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.AI_SERVER_URL, 
                json=payload, 
                headers={"Content-Type": "application/json"},
                timeout=120.0 # Timeout 2 phút đợi AI xử lý
            )
            
        # Kiểm tra phản hồi từ AI Server
        if response.status_code in [200, 201]:
            ai_data = response.json()
            logger.info(f"AI Server responded successfully for request {request_id}.")
            
            # [TÙY CHỌN TÍCH HỢP SAU]
            # Nếu AI Server trả về danh sách ảnh đã gen luôn ở đây, bạn có thể lưu chúng vào bảng `generated_designs`
            # ví dụ: ai_designs = ai_data.get("generated_designs", [])
            # loop và chèn vào db["generated_designs"]...

            # Đổi trạng thái thành COMPLETED
            await repo.update_status(request_id, RequestStatus.COMPLETED.value)
            logger.info(f"Request {request_id} processed successfully. Status updated to COMPLETED.")
        else:
            logger.error(f"AI Server error ({response.status_code}) for request {request_id}: {response.text}")
            await repo.update_status(request_id, RequestStatus.FAILED.value)

    except httpx.RequestError as exc:
        logger.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
        await repo.update_status(request_id, RequestStatus.FAILED.value)
    except Exception as e:
        logger.error(f"Unexpected error in background analysis for request {request_id}: {str(e)}")
        await repo.update_status(request_id, RequestStatus.FAILED.value)