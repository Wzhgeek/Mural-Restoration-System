@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo 克孜尔石窟壁画智慧修复全生命周期管理系统
echo 数据库初始化脚本 (Windows)
echo ============================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查是否在项目根目录
if not exist "main.py" (
    echo ❌ 错误: 请在项目根目录下运行此脚本
    pause
    exit /b 1
)

echo 🔧 开始数据库初始化...
echo.

REM 运行Python初始化脚本
python init_database.py

if errorlevel 1 (
    echo.
    echo ❌ 数据库初始化失败
    echo.
    echo 请检查以下项目:
    echo 1. PostgreSQL服务是否已启动
    echo 2. 数据库连接配置是否正确
    echo 3. 用户权限是否足够
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ✅ 数据库初始化完成
    echo.
    echo 现在可以启动应用程序:
    echo   python main.py
    echo.
)

pause
