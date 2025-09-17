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
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """确保存储桶存在"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"创建存储桶: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"创建存储桶失败: {e}")
            raise
    
    def upload_file(self, file_content: bytes, filename: str, content_type: str = None) -> str:
        """
        上传文件到MinIO
        返回文件的访问URL
        """
        try:
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
                self.bucket_name,
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
            
            file_url = f"{protocol}://{settings.MINIO_ENDPOINT}/{self.bucket_name}/{object_name}"
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
    
    def list_objects(self, prefix: str = "", recursive: bool = True) -> list:
        """列出存储桶中的对象"""
        try:
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=recursive
            )
            return list(objects)
        except S3Error as e:
            logger.error(f"列出对象失败: {e}")
            return []
    
    def get_directory_structure(self, bucket_name: str = None) -> dict:
        """获取指定存储桶的目录结构"""
        try:
            target_bucket = bucket_name or self.bucket_name
            if not self.client.bucket_exists(target_bucket):
                logger.warning(f"存储桶 {target_bucket} 不存在")
                return {"folders": [], "files": []}
            
            objects = self.client.list_objects(target_bucket, recursive=True)
            
            # 构建目录结构
            folders = set()
            files = []
            
            for obj in objects:
                object_name = obj.object_name
                
                # 跳过以/结尾的对象（目录标记）
                if object_name.endswith('/'):
                    continue
                
                # 获取文件信息
                file_info = {
                    "name": object_name.split('/')[-1],
                    "path": object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                    "etag": obj.etag,
                    "url": self.get_file_url(object_name)
                }
                files.append(file_info)
                
                # 提取目录路径
                path_parts = object_name.split('/')
                for i in range(1, len(path_parts)):
                    folder_path = '/'.join(path_parts[:i])
                    folders.add(folder_path)
            
            # 将目录转换为列表并排序
            folder_list = sorted(list(folders))
            
            return {
                "folders": folder_list,
                "files": files
            }
            
        except S3Error as e:
            logger.error(f"获取目录结构失败: {e}")
            return {"folders": [], "files": []}
    
    def get_files_in_directory(self, directory_path: str, bucket_name: str = None) -> list:
        """获取指定目录下的文件列表"""
        try:
            target_bucket = bucket_name or self.bucket_name
            if not self.client.bucket_exists(target_bucket):
                return []
            
            # 确保目录路径以/结尾
            if directory_path and not directory_path.endswith('/'):
                directory_path += '/'
            
            objects = self.client.list_objects(
                target_bucket,
                prefix=directory_path,
                recursive=False
            )
            
            files = []
            for obj in objects:
                object_name = obj.object_name
                
                # 跳过目录标记
                if object_name.endswith('/'):
                    continue
                
                # 获取文件扩展名
                file_ext = os.path.splitext(object_name)[1].lower()
                
                # 确定文件类别
                category = "other"
                if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.tif', '.tiff']:
                    category = "image"
                elif file_ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v']:
                    category = "video"
                elif file_ext in ['.pdf', '.doc', '.docx', '.txt', '.md', '.caj']:
                    category = "document"
                elif file_ext in ['.js', '.ts', '.vue', '.html', '.css', '.json', '.yaml', '.yml', '.py']:
                    category = "code"
                
                file_info = {
                    "name": object_name.split('/')[-1],
                    "path": object_name,
                    "ext": file_ext,
                    "size": obj.size,
                    "mtime": obj.last_modified.isoformat() if obj.last_modified else None,
                    "category": category,
                    "url": self.get_file_url(object_name)
                }
                files.append(file_info)
            
            return files
            
        except S3Error as e:
            logger.error(f"获取目录文件失败: {e}")
            return []

# 全局文件服务实例
file_service = FileService()


