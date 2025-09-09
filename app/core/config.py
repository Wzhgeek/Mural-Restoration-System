# -*- coding: utf-8 -*-
"""
克孜尔石窟壁画智慧修复全生命周期管理系统
系统配置文件

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年
"""
import os
from typing import List
from pydantic import Field, validator
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
    
    # 前端配置
    VUE_WEB: bool = Field(default=False, description="是否使用Vue3前端，False使用static目录，True使用Vue3前端")
    
    # 文件上传配置
    MAX_FILE_SIZE: int = Field(default=100 * 1024 * 1024, description="最大文件大小，单位字节")
    ALLOWED_IMAGE_TYPES: List[str] = Field(default=["image/jpeg", "image/png", "image/bmp", "image/tiff"], description="允许的图片类型")
    ALLOWED_FILE_TYPES: List[str] = Field(default=["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"], description="允许的文件类型")
    
    @validator('ALLOWED_IMAGE_TYPES', pre=True)
    def parse_image_types(cls, v):
        """解析图片类型字符串为列表"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        elif isinstance(v, list):
            return v
        return v
    
    @validator('ALLOWED_FILE_TYPES', pre=True)
    def parse_file_types(cls, v):
        """解析文件类型字符串为列表"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        elif isinstance(v, list):
            return v
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

settings = Settings()

# 数据库连接URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
