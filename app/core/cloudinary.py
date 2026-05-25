# app/config/cloudinary_config.py
import cloudinary
import cloudinary.uploader
from app.core.config import settings

if settings.CLOUDINARY_URL:
    cloudinary.config(
        cloudinary_url=settings.CLOUDINARY_URL,
        secure=True
    )
else:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )