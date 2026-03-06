"""
情绪打卡与报告API
"""
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, UserProfile, MoodLog, Conversation
from app.schemas import MoodLogCreate, MoodLogResponse, MoodReport, DailyMotivation
from app.routes.auth import get_current_user
from app.services.agent import get_agent

router = APIRouter(prefix="/mood", tags=["情绪打卡"])


@router.post("/log", response_model=MoodLogResponse)
async def create_mood_log(
    log_data: MoodLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """情绪打卡"""
    mood_log = MoodLog(
        user_id=current_user.id,
        mood=log_data.mood,
        mood_score=log_data.mood_score,
        note=log_data.note,
        scene=log_data.scene
    )
    db.add(mood_log)
    await db.commit()
    await db.refresh(mood_log)
    
    return mood_log


@router.get("/logs", response_model=List[MoodLogResponse])
async def get_mood_logs(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取情绪打卡记录"""
    since = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(MoodLog)
        .where(MoodLog.user_id == current_user.id, MoodLog.created_at >= since)
        .order_by(desc(MoodLog.created_at))
    )
    return result.scalars().all()


@router.get("/report", response_model=MoodReport)
async def get_mood_report(
    period: str = Query("weekly", pattern="^(weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取情绪报告"""
    days = 7 if period == "weekly" else 30
    since = datetime.utcnow() - timedelta(days=days)
    
    # 获取情绪打卡记录
    mood_result = await db.execute(
        select(MoodLog)
        .where(MoodLog.user_id == current_user.id, MoodLog.created_at >= since)
        .order_by(desc(MoodLog.created_at))
    )
    mood_logs = mood_result.scalars().all()
    
    # 获取对话记录
    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id, Conversation.created_at >= since)
        .order_by(desc(Conversation.created_at))
        .limit(100)
    )
    conversations = conv_result.scalars().all()
    
    # 统计情绪分布
    emotion_distribution = {}
    total_score = 0
    for log in mood_logs:
        emotion_distribution[log.mood] = emotion_distribution.get(log.mood, 0) + 1
        total_score += log.mood_score
    
    avg_score = total_score / len(mood_logs) if mood_logs else 5.0
    
    # 获取用户画像
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    
    profile_dict = {
        "user_nickname": current_user.nickname,
        "ai_name": profile.ai_name if profile else "小暖"
    }
    
    # 生成AI总结
    agent = get_agent()
    summary = await agent.generate_mood_summary(
        mood_logs=[{"mood": l.mood, "score": l.mood_score} for l in mood_logs],
        conversations=[{"role": c.role, "content": c.content} for c in conversations],
        profile=profile_dict
    )
    
    return MoodReport(
        period=period,
        emotion_distribution=emotion_distribution,
        average_score=round(avg_score, 1),
        summary=summary,
        mood_logs=[MoodLogResponse.model_validate(log) for log in mood_logs]
    )


@router.get("/motivation", response_model=DailyMotivation)
async def get_daily_motivation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取每日激励"""
    # 获取用户画像
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    
    profile_dict = {
        "user_nickname": current_user.nickname,
        "ai_name": profile.ai_name if profile else "小暖"
    }
    
    exam_info = None
    exam_countdown = None
    exam_name = None
    
    if profile and profile.exam_date:
        delta = profile.exam_date - datetime.now()
        days_left = max(0, delta.days)
        if days_left > 0:
            exam_info = {"name": profile.exam_name, "days_left": days_left}
            exam_countdown = days_left
            exam_name = profile.exam_name
    
    agent = get_agent()
    message = await agent.generate_daily_motivation(profile_dict, exam_info)
    
    return DailyMotivation(
        message=message,
        exam_countdown=exam_countdown,
        exam_name=exam_name
    )


@router.get("/trend")
async def get_mood_trend(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取情绪趋势数据（用于绘制图表）"""
    since = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(MoodLog)
        .where(MoodLog.user_id == current_user.id, MoodLog.created_at >= since)
        .order_by(MoodLog.created_at)
    )
    logs = result.scalars().all()
    
    # 按日期聚合
    daily_data = {}
    for log in logs:
        date_str = log.created_at.strftime("%Y-%m-%d")
        if date_str not in daily_data:
            daily_data[date_str] = {"scores": [], "moods": []}
        daily_data[date_str]["scores"].append(log.mood_score)
        daily_data[date_str]["moods"].append(log.mood)
    
    trend = []
    for date_str, data in sorted(daily_data.items()):
        avg_score = sum(data["scores"]) / len(data["scores"])
        # 找出当天最频繁的情绪
        mood_counts = {}
        for mood in data["moods"]:
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        main_mood = max(mood_counts, key=mood_counts.get) if mood_counts else "calm"
        
        trend.append({
            "date": date_str,
            "average_score": round(avg_score, 1),
            "main_mood": main_mood,
            "log_count": len(data["scores"])
        })
    
    return {"trend": trend}
