"""
用户画像/个性化设置API（完整版）
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
    if not exam_date:
        return None
    delta = exam_date - datetime.now()
    return max(0, delta.days)


def profile_to_response(profile: UserProfile) -> ProfileResponse:
    return ProfileResponse(
        ai_name=profile.ai_name or "小暖",
        role_template=profile.role_template or "warm_friend",
        gender_feel=profile.gender_feel or "none",
        age_feel=profile.age_feel or "youth",
        personality_tags=profile.personality_tags or [],
        companion_style=profile.companion_style or "warm",
        reply_length=profile.reply_length or "normal",
        address_mode=profile.address_mode or "nickname",
        custom_address=profile.custom_address,
        emoji_habit=profile.emoji_habit or "sometimes",
        focus_scenarios=profile.focus_scenarios or [],
        proactive_level=profile.proactive_level or "moderate",
        proactive_behaviors=profile.proactive_behaviors or [],
        available_time=profile.available_time or "allday",
        available_start=profile.available_start,
        available_end=profile.available_end,
        preferred_topics=profile.preferred_topics or [],
        forbidden_topics=profile.forbidden_topics or [],
        custom_forbidden_words=profile.custom_forbidden_words or [],
        forbidden_phrases=profile.forbidden_phrases or [],
        avatar_style=profile.avatar_style or "cartoon",
        theme_skin=profile.theme_skin or "healing_blue",
        voice_tone=profile.voice_tone or "neutral",
        voice_mood=profile.voice_mood or "gentle",
        memory_scope=profile.memory_scope or "emotions",
        memory_retention=profile.memory_retention or "7days",
        privacy_shield=profile.privacy_shield if profile.privacy_shield is not None else True,
        cloud_sync=profile.cloud_sync if profile.cloud_sync is not None else True,
        exam_name=profile.exam_name,
        exam_date=profile.exam_date,
        exam_days_left=calculate_days_left(profile.exam_date),
        night_mode_auto=profile.night_mode_auto if profile.night_mode_auto is not None else True,
        emotion_sensitivity=profile.emotion_sensitivity or "medium",
        ai_catchphrase=profile.ai_catchphrase,
        special_dates=profile.special_dates or [],
        sleep_mode=profile.sleep_mode if profile.sleep_mode is not None else False,
    )


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile_to_response(profile)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    updates: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile_to_response(profile)


@router.post("/exam")
async def set_exam(
    exam_name: str,
    exam_date: datetime,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
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
    return {"message": f"已设置备考目标：{exam_name}", "days_left": calculate_days_left(exam_date)}


@router.delete("/exam")
async def clear_exam(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if profile:
        profile.exam_name = None
        profile.exam_date = None
        await db.commit()
    return {"message": "备考信息已清除"}