#!/usr/bin/env python3
"""
启动脚本 - 用于 Render 部署
"""
import os
import sys

# 确保可以找到 app 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting server on port {port}...")
    print(f"📦 QWEN_API_KEY configured: {'Yes' if os.getenv('QWEN_API_KEY') else 'No'}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
