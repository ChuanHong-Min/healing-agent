"""
全局配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # 项目路径
    BASE_DIR = Path(__file__).parent.parent
    
    # 千问API
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    QWEN_API_BASE: str = os.getenv("QWEN_API_BASE", "https://apis.iflow.cn/v1")
    QWEN_MODEL: str = "qwen3-max"  # 可选: qwen3-max, qwen3-coder-plus, deepseek-v3
    
    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./healing_agent.db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # Redis（可选）
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # 深夜模式时间范围
    NIGHT_MODE_START: int = 22  # 22:00
    NIGHT_MODE_END: int = 6     # 06:00

settings = Settings()
