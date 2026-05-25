# test_env.py
import os
from dotenv import load_dotenv
from app.core.config import settings

print("--- KIỂM TRA BẰNG OS ĐỌC THUẦN ---")
load_dotenv()
print("OS Cloud Name:", os.getenv("CLOUDINARY_CLOUD_NAME"))
print("OS API Key:", os.getenv("CLOUDINARY_API_KEY"))

print("\n--- KIỂM TRA BẰNG PYDANTIC SETTINGS ---")
print("Pydantic Cloud Name:", settings.CLOUDINARY_CLOUD_NAME)
print("Pydantic API Key:", settings.CLOUDINARY_API_KEY)
print("Pydantic URL:", settings.CLOUDINARY_URL)