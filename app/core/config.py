"""
克孜尔石窟壁画智慧修复全生命周期管理系统
系统配置文件
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "克孜尔石窟壁画智慧修复全生命周期管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务端口配置
    APP_PORT: int = 8080
    ADMIN_PORT: int = 8081
    
    # 数据库配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "repair_system"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres123"
    
    # MinIO配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "repair-file"
    MINIO_SECURE: bool = False
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # JWT配置
    SECRET_KEY: str = "kizil-cave-repair-system-secret-key-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/bmp", "image/tiff"]
    ALLOWED_FILE_TYPES: list = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
    
    class Config:
        env_file = ".env"

settings = Settings()

# 数据库连接URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
