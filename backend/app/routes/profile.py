"""
用户画像/个性化设置API
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, UserProfile
from app.schemas import ProfileUpdate, ProfileResponse
from app.routes.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["个性化设置"])


def calculate_days_left(exam_date: datetime) -> int:
    """计算距离考试的天数"""
    if not exam_date:
        return None
    delta = exam_date - datetime.now()
    return max(0, delta.days)


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户画像"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    
    return ProfileResponse(
        ai_name=profile.ai_name,
        companion_style=profile.companion_style,
        focus_scenarios=profile.focus_scenarios or [],
        forbidden_phrases=profile.forbidden_phrases or [],
        exam_name=profile.exam_name,
        exam_date=profile.exam_date,
        exam_days_left=calculate_days_left(profile.exam_date),
        night_mode_auto=profile.night_mode_auto
    )


@router.put("", response_model=ProfileResponse)
async def update_profile(
    updates: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户画像"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # 更新字段
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return ProfileResponse(
        ai_name=profile.ai_name,
        companion_style=profile.companion_style,
        focus_scenarios=profile.focus_scenarios or [],
        forbidden_phrases=profile.forbidden_phrases or [],
        exam_name=profile.exam_name,
        exam_date=profile.exam_date,
        exam_days_left=calculate_days_left(profile.exam_date),
        night_mode_auto=profile.night_mode_auto
    )


@router.post("/exam")
async def set_exam(
    exam_name: str,
    exam_date: datetime,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """设置备考信息"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    profile.exam_name = exam_name
    profile.exam_date = exam_date
    await db.commit()
    
    return {
        "message": f"已设置备考目标：{exam_name}",
        "days_left": calculate_days_left(exam_date)
    }


@router.delete("/exam")
async def clear_exam(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """清除备考信息"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if profile:
        profile.exam_name = None
        profile.exam_date = None
        await db.commit()
    
    return {"message": "备考信息已清除"}
