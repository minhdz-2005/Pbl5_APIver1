from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # API Metadata
    PROJECT_NAME: str = "pbl5 fastapi app"
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # MongoDB Configuration
    # Pydantic sẽ ưu tiên lấy từ file .env nếu trùng tên biến
    MONGO_DETAILS: str = Field(..., alias="DATABASE_URL")
    DATABASE_NAME: str = "pbl5"

    # Pydantic Settings Config
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )

# Khởi tạo object settings để dùng chung cho toàn bộ app
settings = Settings()