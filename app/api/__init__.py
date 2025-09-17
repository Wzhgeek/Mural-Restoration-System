# -*- coding: utf-8 -*-
"""
API路由模块
包含所有API端点的路由定义

作者: 王梓涵
邮箱: wangzh011031@163.com
时间: 2025年
"""

from .routes import router
from .work_archive import router as work_archive_router

# 注册工作档案路由
router.include_router(work_archive_router, prefix="/work-archive", tags=["work-archive"])