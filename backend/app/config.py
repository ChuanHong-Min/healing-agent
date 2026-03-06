"""
全局配置
"""
import os
from pathlib import Path

# 尝试加载 .env 文件（本地开发用，生产环境使用环境变量）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # 生产环境可能没有 python-dotenv


class Settings:
    # 项目路径
    BASE_DIR = Path(__file__).parent.parent
    
    # 千问API
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    QWEN_API_BASE: str = os.getenv("QWEN_API_BASE", "https://apis.iflow.cn/v1")
    QWEN_MODEL: str = os.getenv("QWEN_MODEL", "qwen3-max")
    
    # 数据库 - Render 使用临时文件系统，需要用 /tmp 目录
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:////tmp/healing_agent.db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "healing_agent_secret_2024_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # Redis（可选）
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    
    # 深夜模式时间范围
    NIGHT_MODE_START: int = 22  # 22:00
    NIGHT_MODE_END: int = 6     # 06:00


settings = Settings()
