import httpx
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.core.config import settings

# URL endpoint sinh ảnh của AI Server
AI_IMAGE_GEN_URL = f"{settings.AI_SERVER_URL}/generate-images"
# URL của chính server bạn để AI gọi lại khi làm xong ảnh
MY_CALLBACK_URL = f"{settings.BACKEND_URL}/api/v2/analysis_requests/callback/image-result"

logger = logging.getLogger(__name__)

async def request_ai_image_generation(request_id: str, db: AsyncIOMotorDatabase, target_style_prompt: str, base_image_url: str):
    """
    Gửi yêu cầu sinh ảnh tới AI Server dựa trên phong cách đã chọn.
    """
    try:
        # 1. Cập nhật trạng thái sang GENERATING_IMAGES
        await db["analysis_requests"].update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "GENERATING_IMAGES", "updated_at": datetime.utcnow()}}
        )

        # 2. Chuẩn bị Payload
        payload = {
            "request_id": str(request_id),
            "target_style_prompt": target_style_prompt,
            "target_season": "Summer",  # Có thể lấy từ project setting nếu có
            "target_audience": "General",
            "target_weather": "Sunny",
            "base_image_url": base_image_url,
            "num_images": 4,
            "callback_url": MY_CALLBACK_URL,
            "seed": 42, # Bạn có thể random số này
            "canny_low_threshold": 100,
            "canny_high_threshold": 200
        }

        # 3. Gọi AI Server
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(AI_IMAGE_GEN_URL, json=payload)
            response.raise_for_status()
            result = response.json()

        # 4. Lưu job_id vào request để theo dõi sau này nếu cần
        job_id = result.get("job_id")
        await db["analysis_requests"].update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {
                "ai_job_id": job_id,
                "updated_at": datetime.utcnow()
            }}
        )
        
        logger.info(f"Successfully triggered image gen for req {request_id}, Job ID: {job_id}")

    except Exception as e:
        logger.error(f"Error calling AI Image Gen for {request_id}: {str(e)}")
        await db["analysis_requests"].update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "FAILED", "updated_at": datetime.utcnow()}}
        )