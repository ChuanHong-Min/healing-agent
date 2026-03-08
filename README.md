# 🌟 心灵陪伴 · AI治愈心理智能体

> 专为学生打造的情绪陪伴Agent，支持个性化角色定制、深夜模式、备考包、情绪打卡等功能

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 🎯 在线体验

| 服务 | 地址 |
|------|------|
| 🌐 前端页面 | https://chuanhong-min.github.io/healing-agent/ |
| 🔌 后端API | https://healing-agent-api.onrender.com |

> **首次加载可能需要等待 30-60 秒**（Render 免费版冷启动）

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🤖 AI共情对话 | 基于千问大模型，场景化话术 + 情绪识别 |
| � 6种角色模板 | 暖心挚友、温柔知己、元气搭子、沉稳陪伴者... |
| 🎨 6套视觉主题 | 治愈蓝、元气粉、森林绿、暖阳橙、薰衣草、深夜静 |
| 🌙 深夜模式 | 22:00-06:00 自动切换，更轻柔的陪伴 |
| 📚 备考包 | 高考/考研倒计时、备考专属话术 |
| 💖 情绪打卡 | 每日记录情绪，趋势追踪 |
| 🎤 语音输入/输出 | 支持语音对话（需浏览器授权） |

## 🚀 快速开始（任何人都可以使用）

1. 打开 [在线页面](https://chuanhong-min.github.io/healing-agent/)
2. 按引导完成 3 步个性化设置（角色/风格/主动程度）
3. 注册账号，开始聊天！

## 🛠️ 自行部署指南

### 方式一：Fork 仓库 + Render 一键部署（推荐）

#### Step 1：Fork 仓库
点击页面右上角 **Fork** 按钮

#### Step 2：部署后端到 Render

1. 访问 [render.com](https://render.com) 注册免费账号
2. 点击 **New → Web Service**
3. 连接你 Fork 的 GitHub 仓库
4. 配置如下：
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
5. 添加环境变量：
   - `QWEN_API_KEY` = `你的千问API Key`
   - `QWEN_API_BASE` = `https://apis.iflow.cn/v1`（或其他兼容地址）
6. 点击 **Deploy**，等待部署完成（约2-3分钟）
7. 记录后端URL，格式如：`https://healing-agent-api.onrender.com`

#### Step 3：启用 GitHub Pages（前端）

1. 进入你的 Fork 仓库 → **Settings → Pages**
2. Source 选择：**Deploy from a branch**
3. Branch 选择：`main`，目录选择：`/docs`
4. 保存，等待约1分钟，获得前端URL

#### Step 4：连接前后端

在前端页面底部点击 **⚙️ 配置后端**，填入你的 Render 后端URL即可

### 方式二：本地开发

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/healing-agent.git
cd healing-agent

# 2. 启动后端
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 QWEN_API_KEY
python run.py

# 3. 前端：直接用浏览器打开 docs/index.html
# 或启动简单 HTTP 服务器
cd docs && python -m http.server 8080
```

## 📁 项目结构

```
healing-agent/
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── main.py           # 应用入口 & CORS
│   │   ├── config.py         # 环境变量配置
│   │   ├── models.py         # SQLAlchemy 数据模型
│   │   ├── schemas.py        # Pydantic 接口模型
│   │   ├── database.py       # SQLite 异步连接
│   │   ├── routes/           # API 路由
│   │   │   ├── auth.py       # 注册/登录
│   │   │   ├── chat.py       # 聊天接口
│   │   │   ├── profile.py    # 用户档案
│   │   │   └── mood.py       # 情绪打卡
│   │   └── services/
│   │       └── agent.py      # 🧠 核心：7模块提示词引擎
│   ├── requirements.txt
│   ├── render.yaml           # Render 部署配置
│   └── run.py                # 启动脚本
└── docs/                     # 前端（GitHub Pages）
    └── index.html            # 单页应用 SPA
```

## � 获取 API Key

本项目使用 [千问（Qwen）大模型](https://dashscope.aliyuncs.com/)：

1. 访问 [阿里云百炼](https://bailian.console.aliyun.com/) 注册
2. 在 API-KEY 管理页面创建密钥
3. 将密钥填入 Render 环境变量 `QWEN_API_KEY`

> 也支持任何兼容 OpenAI 格式的 API（如 GPT-4、DeepSeek 等），修改 `QWEN_API_BASE` 和 `QWEN_MODEL` 即可

## 📝 License

MIT License — 欢迎 Star ⭐ 和 PR！