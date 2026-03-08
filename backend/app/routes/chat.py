"""
核心对话API - 无需登录版本，使用 session_id 区分会话
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.agent import get_agent

router = APIRouter(prefix="/chat", tags=["对话"])

# ── 内存中的对话历史（session_id -> list of messages）──
# 每个 session 最多保留 30 条，超出自动裁剪
_session_histories: dict[str, list] = {}
MAX_HISTORY = 30


def is_night_mode() -> bool:
    hour = datetime.now().hour
    return hour >= settings.NIGHT_MODE_START or hour < settings.NIGHT_MODE_END


# ── 请求 / 响应模型 ──
class GuestChatRequest(BaseModel):
    session_id: str                          # 前端生成的 UUID，唯一标识本次会话
    message: str
    profile: Optional[dict] = None           # 用户在引导页选的人设配置
    mode: Optional[str] = "auto"


class GuestChatResponse(BaseModel):
    reply: str
    emotion: str
    mode: str


@router.post("/guest", response_model=GuestChatResponse)
async def guest_chat(request: GuestChatRequest):
    """无需登录的对话接口"""
    session_id = request.session_id.strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id 不能为空")

    # 默认人设（如果前端没传）
    default_profile = {
        "ai_name": "小暖",
        "role_template": "warm_friend",
        "gender_feel": "none",
        "age_feel": "youth",
        "personality_tags": [],
        "user_nickname": "朋友",
        "companion_style": "warm",
        "reply_length": "normal",
        "address_mode": "nickname",
        "custom_address": "",
        "emoji_habit": "sometimes",
        "focus_scenarios": ["emotional"],
        "proactive_level": "moderate",
        "proactive_behaviors": ["check_mood"],
        "sleep_mode": False,
        "preferred_topics": [],
        "forbidden_topics": [],
        "custom_forbidden_words": [],
        "forbidden_phrases": [],
        "emotion_sensitivity": "medium",
        "ai_catchphrase": "",
    }

    profile = {**default_profile, **(request.profile or {})}

    # 自动判断模式
    mode = request.mode or "auto"
    if mode == "auto":
        mode = "night" if is_night_mode() else "normal"

    # 获取该 session 的历史
    history = _session_histories.get(session_id, [])

    # 调用 Agent
    agent = get_agent()
    reply, emotion = await agent.chat(
        user_message=request.message,
        profile=profile,
        history=history,
        mode=mode,
    )

    # 更新历史（只保留最近 MAX_HISTORY 条）
    history.append({"role": "user", "content": request.message})
    history.append({"role": "assistant", "content": reply})
    _session_histories[session_id] = history[-MAX_HISTORY:]

    return GuestChatResponse(reply=reply, emotion=emotion, mode=mode)


@router.delete("/guest/{session_id}")
async def clear_guest_history(session_id: str):
    """清空某个 session 的历史"""
    _session_histories.pop(session_id, None)
    return {"message": "已清空"}