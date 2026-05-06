import logging
import httpx
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.design_repository import DesignRepository
from app.schemas.analysis_request import RequestStatus
from app.schemas.generated_design import GeneratedDesignCreate
from app.core.config import settings

logger = logging.getLogger(__name__)

# URL của Webserver AI tạo ảnh (bạn có thể thay đổi đường dẫn cho phù hợp)
AI_GENERATE_URL = f"{settings.AI_SERVER_URL}/generate-designs"

async def background_generate_images(
    request_id: str, 
    target_style_prompt: str, 
    seed_image_urls: list, 
    num_images: int, 
    db: AsyncIOMotorDatabase
):
    """
    Tiến trình ngầm (Background Task) thực hiện việc tạo ảnh AI:
    1. Chuyển trạng thái sang GENERATING_IMAGES.
    2. Gửi request đến Webserver AI.
    3. Lưu các thiết kế nhận được vào bảng generated_designs.
    4. Cập nhật trạng thái COMPLETED (hoặc FAILED nếu thất bại).
    """
    repo = AnalysisRepository(db)
    design_repo = DesignRepository(db)

    try:
        # Bước 1: Cập nhật trạng thái đang tạo ảnh
        logger.info(f"Starting image generation for request {request_id}")
        await repo.update_status(request_id, RequestStatus.GENERATING_IMAGES.value)

        payload = {
            "request_id": request_id,
            "target_style_prompt": target_style_prompt,
            "seed_image_urls": seed_image_urls,
            "num_images": num_images
        }

        # Bước 2: Gửi request tới AI Server
        async with httpx.AsyncClient() as client:
            response = await client.post(
                AI_GENERATE_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300.0 # Tăng timeout lên 5 phút cho tác vụ tạo ảnh
            )

        if response.status_code in [200, 201]:
            ai_data = response.json()
            logger.info(f"Image generation successful for request {request_id}")
            
            # Giả định AI Server trả về mảng các url ảnh trong trường "designs" hoặc "images"
            generated_designs = ai_data.get("designs", [])
            
            # Lưu kết quả vào DB
            for img_url in generated_designs:
                design_create = GeneratedDesignCreate(
                    request_id=request_id,
                    design_image_url=img_url
                )
                await design_repo.create(design_create)
            
            # Bước 3: Cập nhật trạng thái hoàn thành
            await repo.update_status(request_id, RequestStatus.COMPLETED.value)
            logger.info(f"Request {request_id} status updated to COMPLETED")
        else:
            logger.error(f"AI Server returned error {response.status_code}: {response.text}")
            await repo.update_status(request_id, RequestStatus.FAILED.value)

    except Exception as e:
        logger.error(f"Error during image generation for {request_id}: {str(e)}")
        await repo.update_status(request_id, RequestStatus.FAILED.value)