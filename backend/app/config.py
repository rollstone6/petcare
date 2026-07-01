"""宠物宝 (PetCare) — 配置"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "宠物宝 PetCare API"
    database_url: str = "sqlite:///./petcare.db"
    debug: bool = False
    api_prefix: str = "/api"
    jwt_secret: str = "change-me-in-production"
    cors_origins: str = "https://petcare.yjyblog.xyz,http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
