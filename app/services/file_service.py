# -*- coding: utf-8 -*-
"""
文件存储服务 - MinIO

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年
"""
from minio import Minio
from minio.error import S3Error
from ..core.config import settings
import os
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET
        self.knowledge_bucket_name = "knowledge-files"  # 知识体系文件存储桶
        self._ensure_buckets_exist()
    
    def _ensure_buckets_exist(self):
        """确保所有存储桶存在"""
        try:
            # 确保主存储桶存在
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"创建存储桶: {self.bucket_name}")
            
            # 确保知识体系文件存储桶存在
            if not self.client.bucket_exists(self.knowledge_bucket_name):
                self.client.make_bucket(self.knowledge_bucket_name)
                logger.info(f"创建知识体系文件存储桶: {self.knowledge_bucket_name}")
        except S3Error as e:
            logger.error(f"创建存储桶失败: {e}")
            raise
    
    def upload_file(self, file_content: bytes, filename: str, content_type: str = None, bucket_name: str = None) -> str:
        """
        上传文件到MinIO
        返回文件的访问URL
        """
        try:
            # 使用指定的存储桶或默认存储桶
            target_bucket = bucket_name or self.bucket_name
            
            # 生成唯一文件名
            file_ext = os.path.splitext(filename)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{uuid.uuid4()}_{timestamp}{file_ext}"
            
            # 按日期组织目录结构
            date_path = datetime.now().strftime("%Y/%m/%d")
            object_name = f"{date_path}/{unique_filename}"
            
            # 上传文件
            from io import BytesIO
            self.client.put_object(
                target_bucket,
                object_name,
                BytesIO(file_content),
                length=len(file_content),
                content_type=content_type
            )
            
            # 生成访问URL
            if settings.MINIO_SECURE:
                protocol = "https"
            else:
                protocol = "http"
            
            file_url = f"{protocol}://{settings.MINIO_ENDPOINT}/{target_bucket}/{object_name}"
            return file_url
            
        except S3Error as e:
            logger.error(f"文件上传失败: {e}")
            raise Exception(f"文件上传失败: {str(e)}")
    
    async def upload_file_async(self, file, bucket_name: str = None) -> str:
        """
        异步上传文件到MinIO
        返回文件的访问URL
        """
        try:
            # 使用指定的存储桶或默认存储桶
            target_bucket = bucket_name or self.bucket_name
            
            # 读取文件内容
            file_content = await file.read()
            
            # 生成唯一文件名
            file_ext = os.path.splitext(file.filename)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{uuid.uuid4()}_{timestamp}{file_ext}"
            
            # 按日期组织目录结构
            date_path = datetime.now().strftime("%Y/%m/%d")
            object_name = f"{date_path}/{unique_filename}"
            
            # 上传文件
            from io import BytesIO
            self.client.put_object(
                target_bucket,
                object_name,
                BytesIO(file_content),
                length=len(file_content),
                content_type=file.content_type
            )
            
            # 生成访问URL
            if settings.MINIO_SECURE:
                protocol = "https"
            else:
                protocol = "http"
            
            file_url = f"{protocol}://{settings.MINIO_ENDPOINT}/{target_bucket}/{object_name}"
            return file_url
            
        except S3Error as e:
            logger.error(f"文件上传失败: {e}")
            raise Exception(f"文件上传失败: {str(e)}")
    
    def delete_file(self, file_url: str) -> bool:
        """删除文件"""
        try:
            # 从URL中提取object_name
            object_name = file_url.split(f"/{self.bucket_name}/")[1]
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except Exception as e:
            logger.error(f"文件删除失败: {e}")
            return False
    
    def get_file_url(self, object_name: str) -> str:
        """获取文件访问URL"""
        if settings.MINIO_SECURE:
            protocol = "https"
        else:
            protocol = "http"
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{self.bucket_name}/{object_name}"

# 全局文件服务实例
file_service = FileService()


