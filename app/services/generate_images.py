import httpx
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.core.config import settings

# --- Cấu hình Endpoint ---
AI_IMAGE_GEN_URL = f"{settings.AI_SERVER_URL}/generate-images"
AI_JOB_DETAIL_URL = f"{settings.AI_SERVER_URL}/generation-jobs"
# URL gọi nội bộ tới route POST của bạn
INTERNAL_DESIGN_POST_URL = f"{settings.BACKEND_URL}/api/v2/generated_designs/"
MY_CALLBACK_URL = f"{settings.BACKEND_URL}/api/v2/analysis_requests/callback/image-result"

logger = logging.getLogger(__name__)

async def sync_ai_design_results(request_id: str, job_id: str, db: AsyncIOMotorDatabase):
    """
    Lấy kết quả chi tiết từ AI Server và lưu vào hệ thống nội bộ.
    Tận dụng Dynamic Schema để lưu toàn bộ metadata.
    """
    try:
        # 1. Gọi AI Server lấy thông tin Job
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{AI_JOB_DETAIL_URL}/{job_id}")
            if response.status_code != 200:
                logger.error(f"Không thể lấy thông tin job {job_id} từ AI Server")
                return
            job_data = response.json()

        # 2. Kiểm tra danh sách ảnh trả về
        designs = job_data.get("generated_designs", [])
        if not designs:
            logger.warning(f"Job {job_id} chưa có thiết kế nào được sinh ra.")
            return

        # 3. Lưu từng thiết kế vào collection nội bộ qua route POST
        # Lưu ý: Cần truyền Token vào Header nếu main.py yêu cầu Auth
        headers = {"Authorization": f"Bearer {settings.INTERNAL_API_TOKEN}"} # Giả định bạn có token nội bộ
        
        async with httpx.AsyncClient() as client:
            for design in designs:
                payload = {
                    "request_id": str(request_id),
                    "design_image_url": design.get("url"),
                    "user_rating": 5,
                    # Tận dụng Dynamic Schema: lưu toàn bộ thông tin gốc từ AI vào đây
                    "ai_metadata": job_data 
                }
                
                res = await client.post(INTERNAL_DESIGN_POST_URL, json=payload, headers=headers)
                if res.status_code != 201:
                    logger.error(f"Lưu design vào DB thất bại: {res.text}")

        # 4. Cập nhật trạng thái cuối cùng cho Analysis Request
        await db["analysis_requests"].update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "COMPLETED", "updated_at": datetime.utcnow()}}
        )
        logger.info(f"Hoàn tất đồng bộ {len(designs)} ảnh cho request {request_id}")

    except Exception as e:
        logger.error(f"Lỗi khi sync kết quả AI: {str(e)}")

async def request_ai_image_generation(request_id: str, db: AsyncIOMotorDatabase, target_style_prompt: str, base_image_url: str):
    """
    Gửi yêu cầu sinh ảnh tới AI Server.
    """
    try:
        # 1. Cập nhật trạng thái
        await db["analysis_requests"].update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "GENERATING_IMAGES", "updated_at": datetime.utcnow()}}
        )

        # 2. Chuẩn bị Payload
        payload = {
            "request_id": str(request_id),
            "target_style_prompt": target_style_prompt,
            "target_season": "Summer",
            "target_audience": "General",
            "target_weather": "Sunny",
            "base_image_url": base_image_url,
            "num_images": 4,
            "callback_url": MY_CALLBACK_URL,
            "seed": 42,
            "canny_low_threshold": 100,
            "canny_high_threshold": 200
        }

        # 3. Gọi AI Server tạo Job
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(AI_IMAGE_GEN_URL, json=payload)
            response.raise_for_status()
            result = response.json()

        # 4. Lưu job_id và kích hoạt đồng bộ
        job_id = result.get("job_id")
        await db["analysis_requests"].update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {
                "ai_job_id": job_id,
                "updated_at": datetime.utcnow()
            }}
        )
        
        logger.info(f"Triggered AI Job: {job_id}. Bắt đầu đồng bộ kết quả...")
        
        # Gọi hàm sync kết quả
        # Lưu ý: Nếu AI Server xử lý lâu, bạn nên gọi hàm này trong route Callback thay vì gọi ở đây
        await sync_ai_design_results(request_id, job_id, db)

    except Exception as e:
        logger.error(f"Error calling AI Image Gen for {request_id}: {str(e)}")
        await db["analysis_requests"].update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "FAILED", "updated_at": datetime.utcnow()}}
        )