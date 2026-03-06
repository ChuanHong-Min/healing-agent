# AI治愈心理智能体

🌟 学生情绪陪伴Agent - 在线体验版

## ✨ 功能特性

- 🤖 **AI共情对话** - 基于大模型，场景化话术+情绪识别
- 🎨 **个性化定制** - AI昵称、陪伴风格、禁忌词设置
- 🌙 **深夜模式** - 22:00-06:00自动切换，更轻柔的陪伴
- 📚 **备考包** - 倒计时、备考专属话术、每日激励
- 💖 **情绪打卡** - 每日记录情绪，生成趋势图
- 📊 **情绪报告** - 周/月度情绪分析报告

## 🚀 在线体验

访问地址：[https://你的用户名.github.io/healing-agent](https://你的用户名.github.io/healing-agent)

## 🛠️ 本地开发

### 后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API Key
python -m uvicorn app.main:app --reload
```

### 前端

直接打开 `frontend/index.html` 或使用 Live Server

## 📁 项目结构

```
healing-agent/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── main.py         # FastAPI入口
│   │   ├── config.py       # 配置
│   │   ├── models.py       # 数据模型
│   │   ├── schemas.py      # API模型
│   │   ├── database.py     # 数据库
│   │   ├── routes/         # API路由
│   │   └── services/       # 业务逻辑
│   ├── requirements.txt
│   └── render.yaml         # Render部署配置
├── frontend/               # 前端代码(GitHub Pages)
│   └── index.html
└── README.md
```

## 🔧 部署指南

### 1. 部署后端到 Render

1. Fork 本仓库
2. 在 [Render](https://render.com) 创建账号
3. 新建 Web Service，选择本仓库
4. 设置环境变量 `QWEN_API_KEY`
5. 部署完成后获取后端URL

### 2. 部署前端到 GitHub Pages

1. 修改 `frontend/index.html` 中的 `API_BASE` 为后端URL
2. 在仓库 Settings → Pages 启用 GitHub Pages
3. 选择 main 分支的 /frontend 目录

## 📝 License

MIT License
