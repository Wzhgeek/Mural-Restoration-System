# -*- coding: utf-8 -*-
"""
邮件服务模块

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年
"""
import smtplib
import random
import string
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from sqlalchemy.orm import Session
from ..core.config import settings
from ..models import User
import redis
import json

# Redis连接（用于存储验证码）
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.email_from = settings.EMAIL_FROM
        self.email_from_name = settings.EMAIL_FROM_NAME
    
    def _create_smtp_connection(self):
        """创建SMTP连接"""
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            if self.smtp_use_tls:
                server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            return server
        except Exception as e:
            raise Exception(f"SMTP连接失败: {str(e)}")
    
    def _generate_verification_code(self) -> str:
        """生成验证码"""
        return ''.join(random.choices(string.digits, k=settings.EMAIL_VERIFICATION_CODE_LENGTH))
    
    def _store_verification_code(self, email: str, code: str) -> None:
        """存储验证码到Redis"""
        key = f"email_verification:{email}"
        data = {
            "code": code,
            "created_at": datetime.now().isoformat(),
            "attempts": 0
        }
        # 设置过期时间
        redis_client.setex(key, settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES * 60, json.dumps(data))
    
    def _get_verification_code(self, email: str) -> Optional[dict]:
        """从Redis获取验证码"""
        key = f"email_verification:{email}"
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    
    def _increment_attempts(self, email: str) -> int:
        """增加验证尝试次数"""
        key = f"email_verification:{email}"
        data = self._get_verification_code(email)
        if data:
            data["attempts"] += 1
            redis_client.setex(key, settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES * 60, json.dumps(data))
            return data["attempts"]
        return 0
    
    def _delete_verification_code(self, email: str) -> None:
        """删除验证码"""
        key = f"email_verification:{email}"
        redis_client.delete(key)
    
    def send_verification_email(self, email: str, username: str) -> str:
        """发送邮箱验证邮件"""
        # 生成验证码
        verification_code = self._generate_verification_code()
        
        # 存储验证码
        self._store_verification_code(email, verification_code)
        
        # 创建邮件内容
        subject = f"{self.email_from_name} - 邮箱验证"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>邮箱验证</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .verification-code {{
                    background: #fff;
                    border: 2px dashed #667eea;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                    border-radius: 8px;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 5px;
                }}
                .warning {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>克孜尔石窟壁画智慧修复全生命周期管理系统</h1>
                <p>邮箱验证</p>
            </div>
            <div class="content">
                <h2>亲爱的 {username}，</h2>
                <p>欢迎注册克孜尔石窟壁画智慧修复全生命周期管理系统！</p>
                <p>请使用以下验证码完成邮箱验证：</p>
                
                <div class="verification-code">
                    <div class="code">{verification_code}</div>
                </div>
                
                <div class="warning">
                    <strong>重要提示：</strong>
                    <ul>
                        <li>验证码有效期为 {settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES} 分钟</li>
                        <li>请勿将验证码泄露给他人</li>
                        <li>如非本人操作，请忽略此邮件</li>
                    </ul>
                </div>
                
                <p>如果您有任何问题，请联系系统管理员。</p>
            </div>
            <div class="footer">
                <p>此邮件由系统自动发送，请勿回复</p>
                <p>© 2025 克孜尔石窟壁画智慧修复全生命周期管理系统</p>
            </div>
        </body>
        </html>
        """
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.email_from_name} <{self.email_from}>"
        msg['To'] = email
        
        # 添加HTML内容
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # 发送邮件
        try:
            server = self._create_smtp_connection()
            server.send_message(msg)
            server.quit()
            return verification_code
        except Exception as e:
            # 发送失败时删除验证码
            self._delete_verification_code(email)
            raise Exception(f"邮件发送失败: {str(e)}")
    
    def verify_email_code(self, email: str, code: str) -> bool:
        """验证邮箱验证码"""
        stored_data = self._get_verification_code(email)
        if not stored_data:
            return False
        
        # 检查尝试次数
        if stored_data.get("attempts", 0) >= 5:
            self._delete_verification_code(email)
            return False
        
        # 验证码匹配
        if stored_data["code"] == code:
            self._delete_verification_code(email)
            return True
        else:
            # 增加尝试次数
            self._increment_attempts(email)
            return False
    
    def send_welcome_email(self, email: str, username: str) -> bool:
        """发送欢迎邮件"""
        subject = f"欢迎加入{self.email_from_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>欢迎加入</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .success {{
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    color: #155724;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>克孜尔石窟壁画智慧修复全生命周期管理系统</h1>
                <p>欢迎加入</p>
            </div>
            <div class="content">
                <div class="success">
                    <h2>🎉 邮箱验证成功！</h2>
                </div>
                
                <h2>亲爱的 {username}，</h2>
                <p>恭喜您成功注册并验证了邮箱！您现在可以正常使用克孜尔石窟壁画智慧修复全生命周期管理系统的所有功能。</p>
                
                <h3>系统功能概览：</h3>
                <ul>
                    <li><strong>修复工作流管理：</strong>创建和管理壁画修复工作流程</li>
                    <li><strong>图片标注：</strong>上传和标注壁画图片</li>
                    <li><strong>修复方案提交：</strong>提交详细的修复方案和意见</li>
                    <li><strong>专家评估：</strong>邀请专家对修复方案进行评估</li>
                    <li><strong>历史回溯：</strong>查看和管理修复历史记录</li>
                    <li><strong>知识体系：</strong>管理和分享相关技术文档</li>
                </ul>
                
                <p>如果您在使用过程中遇到任何问题，请联系系统管理员。</p>
            </div>
            <div class="footer">
                <p>此邮件由系统自动发送，请勿回复</p>
                <p>© 2025 克孜尔石窟壁画智慧修复全生命周期管理系统</p>
            </div>
        </body>
        </html>
        """
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.email_from_name} <{self.email_from}>"
        msg['To'] = email
        
        # 添加HTML内容
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # 发送邮件
        try:
            server = self._create_smtp_connection()
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            raise Exception(f"欢迎邮件发送失败: {str(e)}")

# 创建邮件服务实例
email_service = EmailService()