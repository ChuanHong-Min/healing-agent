"""
AI治愈心理智能体 - FastAPI应用入口（无需登录版）
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ AI治愈心理智能体启动（无需登录版）")
    yield
    print("👋 应用关闭")


app = FastAPI(
    title="AI治愈心理智能体",
    description="学生情绪陪伴Agent - 无需登录，即开即用",
    version="2.0.0",
    lifespan=lifespan
)

# CORS - 允许任何来源（GitHub Pages 需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 只注册聊天路由
app.include_router(chat.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "status": "ok",
        "name": "AI治愈心理智能体",
        "version": "2.0.0",
        "mode": "guest-only",
        "chat_endpoint": "/api/chat/guest"
    }


@app.get("/api/health")
async def health_check():
    from app.config import settings
    return {
        "status": "healthy",
        "api_key_set": bool(settings.QWEN_API_KEY),
        "model": settings.QWEN_MODEL
    }


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