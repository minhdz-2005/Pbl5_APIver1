# app/core/cloudinary.py
import logging
import cloudinary
import cloudinary.uploader
from app.core.config import settings

logger = logging.getLogger(__name__)


def _mask(s: str | None) -> str | None:
    if not s:
        return None
    if len(s) <= 8:
        return s[:2] + "..."
    return s[:4] + "..." + s[-4:]


try:
    if settings.CLOUDINARY_URL:
        cloudinary.config(
            cloudinary_url=settings.CLOUDINARY_URL,
            secure=True
        )
        logger.info("Configured Cloudinary from CLOUDINARY_URL")
    else:
        if not (settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET):
            logger.warning("Cloudinary settings missing: cloud_name=%s, api_key=%s, api_secret=%s",
                           _mask(getattr(settings, 'CLOUDINARY_CLOUD_NAME', None)),
                           _mask(getattr(settings, 'CLOUDINARY_API_KEY', None)),
                           _mask(getattr(settings, 'CLOUDINARY_API_SECRET', None)))
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
        logger.info("Configured Cloudinary from individual settings (cloud_name=%s, api_key=%s)",
                    _mask(settings.CLOUDINARY_CLOUD_NAME), _mask(settings.CLOUDINARY_API_KEY))
except Exception as e:
    logger.exception("Failed to configure Cloudinary: %s", e)