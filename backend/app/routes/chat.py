"""
核心对话API
"""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import User, UserProfile, Conversation
from app.schemas import ChatRequest, ChatResponse, ConversationItem
from app.routes.auth import get_current_user
from app.services.agent import get_agent

router = APIRouter(prefix="/chat", tags=["对话"])


def is_night_mode() -> bool:
    """判断当前是否为深夜时段"""
    hour = datetime.now().hour
    return hour >= settings.NIGHT_MODE_START or hour < settings.NIGHT_MODE_END


def calculate_days_left(exam_date: datetime) -> int:
    """计算距离考试的天数"""
    if not exam_date:
        return 0
    delta = exam_date - datetime.now()
    return max(0, delta.days)


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """核心对话接口"""
    # 1. 获取用户画像
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    
    # 2. 确定对话模式
    mode = request.mode
    if mode == "auto":
        if profile.exam_date and calculate_days_left(profile.exam_date) > 0:
            mode = "exam"
        elif is_night_mode() and profile.night_mode_auto:
            mode = "night"
        else:
            mode = "normal"
    
    # 3. 获取历史对话
    history_result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.created_at))
        .limit(20)
    )
    history_records = history_result.scalars().all()
    history = [{"role": r.role, "content": r.content} for r in reversed(history_records)]
    
    # 4. 构建profile字典
    profile_dict = {
        "ai_name": profile.ai_name,
        "companion_style": profile.companion_style,
        "forbidden_phrases": profile.forbidden_phrases or [],
        "user_nickname": current_user.nickname,
        "focus_scenarios": profile.focus_scenarios or []
    }
    
    # 5. 构建exam_info
    exam_info = None
    if mode == "exam" and profile.exam_date:
        exam_info = {
            "name": profile.exam_name or "考试",
            "days_left": calculate_days_left(profile.exam_date)
        }
    
    # 6. 调用Agent
    agent = get_agent()
    reply, emotion = await agent.chat(
        user_message=request.message,
        profile=profile_dict,
        history=history,
        mode=mode,
        exam_info=exam_info
    )
    
    # 7. 保存对话记录
    # 保存用户消息
    user_msg = Conversation(
        user_id=current_user.id,
        role="user",
        content=request.message,
        emotion=emotion,
        mode=mode
    )
    db.add(user_msg)
    
    # 保存AI回复
    ai_msg = Conversation(
        user_id=current_user.id,
        role="assistant",
        content=reply,
        mode=mode
    )
    db.add(ai_msg)
    await db.commit()
    
    return ChatResponse(
        reply=reply,
        emotion=emotion,
        mode=mode,
        ai_name=profile.ai_name
    )


@router.get("/history", response_model=List[ConversationItem])
async def get_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话历史"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.created_at))
        .limit(limit)
    )
    records = result.scalars().all()
    return list(reversed(records))


@router.delete("/history")
async def clear_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """清空对话历史"""
    from sqlalchemy import delete
    await db.execute(
        delete(Conversation).where(Conversation.user_id == current_user.id)
    )
    await db.commit()
    return {"message": "对话历史已清空"}
