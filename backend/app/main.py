"""
AI治愈心理智能体 - FastAPI应用入口
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import auth, chat, profile, mood


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    print("✅ 数据库初始化完成")
    yield
    # 关闭时清理资源
    print("👋 应用关闭")


app = FastAPI(
    title="AI治愈心理智能体",
    description="学生情绪陪伴Agent - MVP版本",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(mood.router, prefix="/api")


@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "name": "AI治愈心理智能体",
        "version": "1.0.0",
        "features": [
            "AI共情对话",
            "个性化定制",
            "深夜模式",
            "备考包",
            "情绪打卡",
            "情绪报告"
        ]
    }


@app.get("/api/health")
async def health_check():
    """API健康检查"""
    return {"status": "healthy"}


@app.get("/api/debug")
async def debug_info():
    """调试信息"""
    import sys
    from app.config import settings
    return {
        "python_version": sys.version,
        "qwen_api_configured": bool(settings.QWEN_API_KEY),
        "database_url": settings.DATABASE_URL[:30] + "...",
        "code_version": "2024-03-06-v2"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
