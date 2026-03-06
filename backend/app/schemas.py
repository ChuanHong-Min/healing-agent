"""
Pydantic schemas - API请求/响应模型
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ==================== 用户相关 ====================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    nickname: Optional[str] = "同学"


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    id: int
    username: str
    nickname: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 用户画像 ====================

class ProfileUpdate(BaseModel):
    ai_name: Optional[str] = Field(None, max_length=20)
    companion_style: Optional[str] = Field(None, pattern="^(warm|casual|calm)$")
    focus_scenarios: Optional[List[str]] = None
    forbidden_phrases: Optional[List[str]] = None
    exam_name: Optional[str] = None
    exam_date: Optional[datetime] = None
    night_mode_auto: Optional[bool] = None


class ProfileResponse(BaseModel):
    ai_name: str
    companion_style: str
    focus_scenarios: List[str]
    forbidden_phrases: List[str]
    exam_name: Optional[str]
    exam_date: Optional[datetime]
    exam_days_left: Optional[int]
    night_mode_auto: bool

    class Config:
        from_attributes = True


# ==================== 对话相关 ====================

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    mode: Optional[str] = Field("auto", pattern="^(auto|normal|night|exam)$")


class ChatResponse(BaseModel):
    reply: str
    emotion: str
    mode: str
    ai_name: str


class ConversationItem(BaseModel):
    role: str
    content: str
    emotion: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 情绪打卡 ====================

class MoodLogCreate(BaseModel):
    mood: str = Field(..., pattern="^(anxious|calm|confident|sad|happy|tired|angry)$")
    mood_score: int = Field(..., ge=1, le=10)
    note: Optional[str] = None
    scene: Optional[str] = "daily"


class MoodLogResponse(BaseModel):
    id: int
    mood: str
    mood_score: int
    note: Optional[str]
    scene: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 情绪报告 ====================

class MoodSummary(BaseModel):
    main_emotion: str
    emotion_trend: str
    main_stressor: Optional[str]
    positive_point: str
    suggestion: str


class MoodReport(BaseModel):
    period: str  # "weekly" / "monthly"
    emotion_distribution: dict  # {"anxious": 5, "calm": 10, ...}
    average_score: float
    summary: MoodSummary
    mood_logs: List[MoodLogResponse]


# ==================== 每日激励 ====================

class DailyMotivation(BaseModel):
    message: str
    exam_countdown: Optional[int]
    exam_name: Optional[str]
