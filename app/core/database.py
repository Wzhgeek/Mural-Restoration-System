"""
数据库连接和初始化
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models import Base, Role, User, SystemConfig
from .config import DATABASE_URL
from passlib.context import CryptContext

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

def init_data():
    """初始化基础数据"""
    db = SessionLocal()
    try:
        # 创建角色
        roles_data = [
            {"role_key": "admin", "role_name": "管理员"},
            {"role_key": "restorer", "role_name": "修复专家"},
            {"role_key": "evaluator", "role_name": "评估专家"}
        ]
        
        for role_data in roles_data:
            existing_role = db.query(Role).filter(Role.role_key == role_data["role_key"]).first()
            if not existing_role:
                role = Role(**role_data)
                db.add(role)
        
        db.commit()
        
        # 创建默认管理员用户
        admin_role = db.query(Role).filter(Role.role_key == "admin").first()
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin and admin_role:
            admin_user = User(
                username="admin",
                password_hash=pwd_context.hash("admin123"),
                full_name="系统管理员",
                role_id=admin_role.role_id,
                email="admin@repair.com"
            )
            db.add(admin_user)
        
        # 创建测试用户
        restorer_role = db.query(Role).filter(Role.role_key == "restorer").first()
        evaluator_role = db.query(Role).filter(Role.role_key == "evaluator").first()
        
        test_users = [
            {
                "username": "restorer1",
                "password": "123456",
                "full_name": "修复专家张三",
                "role_id": restorer_role.role_id if restorer_role else None,
                "email": "restorer1@repair.com"
            },
            {
                "username": "evaluator1", 
                "password": "123456",
                "full_name": "评估专家李四",
                "role_id": evaluator_role.role_id if evaluator_role else None,
                "email": "evaluator1@repair.com"
            }
        ]
        
        for user_data in test_users:
            if user_data["role_id"]:
                existing_user = db.query(User).filter(User.username == user_data["username"]).first()
                if not existing_user:
                    user = User(
                        username=user_data["username"],
                        password_hash=pwd_context.hash(user_data["password"]),
                        full_name=user_data["full_name"],
                        role_id=user_data["role_id"],
                        email=user_data["email"]
                    )
                    db.add(user)
        
        # 创建系统配置
        configs = [
            {
                "config_key": "privacy_agreement",
                "config_value": """保密协议

尊敬的用户：

感谢您使用克孜尔石窟壁画智慧修复全生命周期管理系统。为了保护珍贵的文物信息和相关技术资料，请您仔细阅读并同意以下保密条款：

1. 保密义务
   您承诺对在使用本系统过程中接触到的所有壁画图像、修复技术、工艺流程等信息严格保密。

2. 信息安全
   未经授权，不得复制、传播、泄露任何系统中的文物信息。

3. 使用限制
   仅可将获得的信息用于指定的修复工作，不得用于其他商业或个人目的。

4. 责任承担
   如违反保密义务造成损失，将承担相应的法律责任。

请仔细阅读上述条款，点击"同意"按钮表示您已完全理解并同意遵守本保密协议。""",
                "description": "用户保密协议内容"
            }
        ]
        
        for config_data in configs:
            existing_config = db.query(SystemConfig).filter(
                SystemConfig.config_key == config_data["config_key"]
            ).first()
            if not existing_config:
                config = SystemConfig(**config_data)
                db.add(config)
        
        db.commit()
        print("基础数据初始化完成")
        
    except Exception as e:
        db.rollback()
        print(f"数据初始化失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # 创建表和初始化数据
    create_tables()
    init_data()


