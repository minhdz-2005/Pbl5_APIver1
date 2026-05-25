import asyncio
import logging
import cloudinary          # 1. IMPORT SDK GỐC ĐỂ DÙNG CHẠY HÀM UPLOAD
import cloudinary.uploader
from typing import Dict, Any

import httpx

# 2. IMPORT file core này để ÉP Python chạy đoạn code cấu hình tự động của bạn
from app.core import cloudinary as cloudinary_initializer 
from app.core.config import settings

logger = logging.getLogger(__name__)


async def upload_image_to_cloudinary(
    folder_name: str,
    image_url: str,
    generated_design_id: str
) -> Dict[str, Any]:
    """
    Upload an image to Cloudinary from a URL.
    
    Args:
        image_url (str): The URL of the image to upload
        generated_design_id (str): The ID of the generated design
    
    Returns:
        Dict containing:
            - design_id (str): The generated design ID
            - cloudinary_url (str): The URL of the uploaded image on Cloudinary
            - public_id (str): The public ID of the resource on Cloudinary
    
    Raises:
        Exception: If upload fails
    """
    try:
        # Ensure Cloudinary is configured at call time (idempotent)
        try:
            if settings.CLOUDINARY_URL:
                # cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL, secure=True)
                cloudinary.config(url=settings.CLOUDINARY_URL, secure=True)
                
                # Để đề phòng SDK kén cấu hình URL, ta chủ động ép thêm 3 key lẻ từ settings luôn cho chắc chắn 100%
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                    api_key=settings.CLOUDINARY_API_KEY,
                    api_secret=settings.CLOUDINARY_API_SECRET,
                    secure=True
                )
                logger.warning(settings.CLOUDINARY_URL)
            else:
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                    api_key=settings.CLOUDINARY_API_KEY,
                    api_secret=settings.CLOUDINARY_API_SECRET,
                    secure=True,
                )
                logger.warning(settings.CLOUDINARY_CLOUD_NAME)
                logger.warning(settings.CLOUDINARY_API_KEY)
                logger.warning(settings.CLOUDINARY_API_SECRET)
        except Exception:
            logger.debug("Could not (re)configure Cloudinary from settings before upload")

        # 1. Chủ động tải ảnh từ AI Server về Backend của bạn bằng httpx
        async with httpx.AsyncClient() as client:
            # Thêm header để ngrok KHÔNG hiện trang cảnh báo nữa mà trả về file ảnh luôn
            headers = {"ngrok-skip-browser-warning": "6969"}
            response = await client.get(image_url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Không thể tải ảnh từ AI Server, Status code: {response.status_code}")
            
            # Lấy dữ liệu dạng bytes của bức ảnh
            image_bytes = response.content

        # Run the blocking upload call in a thread to avoid blocking the event loop
        upload_result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            image_bytes,
            folder=f"pbl5/{folder_name}/{generated_design_id}",
            resource_type="auto",
            quality="auto",
            fetch_format="auto"
        )

        logger.debug("Cloudinary upload result: %s", upload_result)

        return {
            "design_id": generated_design_id,
            "cloudinary_url": upload_result.get("secure_url") or upload_result.get("url"),
            "public_id": upload_result.get("public_id"),
            "raw": upload_result
        }

    except Exception as e:
        logger.exception("Failed to upload image to Cloudinary: %s", e)
        # Return structured error info to caller instead of raising to keep caller robust
        return {
            "design_id": generated_design_id,
            "cloudinary_url": None,
            "public_id": None,
            "error": str(e)
        }
