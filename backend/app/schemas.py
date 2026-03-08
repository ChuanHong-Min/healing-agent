"""
Pydantic schemas - API请求/响应模型（完整版）
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ==================== 用户相关 ====================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    nickname: Optional[str] = "同学"
    companion_style: Optional[str] = "warm"


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


# ==================== 用户画像（完整版）====================

class ProfileUpdate(BaseModel):
    # 模块1：核心身份人设
    ai_name: Optional[str] = Field(None, max_length=20)
    role_template: Optional[str] = None
    gender_feel: Optional[str] = None       # male/female/none
    age_feel: Optional[str] = None          # teen/youth/mature/none
    personality_tags: Optional[List[str]] = None  # 最多3个

    # 模块2：交互风格
    companion_style: Optional[str] = None  # warm/energetic/calm/humor/minimal
    reply_length: Optional[str] = None     # short/normal/detailed
    address_mode: Optional[str] = None     # nickname/fullname/baby/custom
    custom_address: Optional[str] = None
    emoji_habit: Optional[str] = None      # always/sometimes/never

    # 模块3：陪伴场景
    focus_scenarios: Optional[List[str]] = None

    # 模块4：主动交互边界
    proactive_level: Optional[str] = None       # very/moderate/passive
    proactive_behaviors: Optional[List[str]] = None
    available_time: Optional[str] = None        # allday/daytime/nighttime/custom
    available_start: Optional[str] = None
    available_end: Optional[str] = None

    # 模块5：话题与内容边界
    preferred_topics: Optional[List[str]] = None
    forbidden_topics: Optional[List[str]] = None
    custom_forbidden_words: Optional[List[str]] = None
    forbidden_phrases: Optional[List[str]] = None

    # 模块6：形象/语音设定
    avatar_style: Optional[str] = None
    theme_skin: Optional[str] = None
    voice_tone: Optional[str] = None
    voice_mood: Optional[str] = None

    # 模块7：记忆与隐私
    memory_scope: Optional[str] = None
    memory_retention: Optional[str] = None
    privacy_shield: Optional[bool] = None
    cloud_sync: Optional[bool] = None

    # 备考设置
    exam_name: Optional[str] = None
    exam_date: Optional[datetime] = None
    night_mode_auto: Optional[bool] = None

    # 特色小设定
    emotion_sensitivity: Optional[str] = None
    ai_catchphrase: Optional[str] = None
    special_dates: Optional[List[Dict[str, Any]]] = None
    sleep_mode: Optional[bool] = None


class ProfileResponse(BaseModel):
    # 模块1
    ai_name: str
    role_template: str
    gender_feel: str
    age_feel: str
    personality_tags: List[str]

    # 模块2
    companion_style: str
    reply_length: str
    address_mode: str
    custom_address: Optional[str]
    emoji_habit: str

    # 模块3
    focus_scenarios: List[str]

    # 模块4
    proactive_level: str
    proactive_behaviors: List[str]
    available_time: str
    available_start: Optional[str]
    available_end: Optional[str]

    # 模块5
    preferred_topics: List[str]
    forbidden_topics: List[str]
    custom_forbidden_words: List[str]
    forbidden_phrases: List[str]

    # 模块6
    avatar_style: str
    theme_skin: str
    voice_tone: str
    voice_mood: str

    # 模块7
    memory_scope: str
    memory_retention: str
    privacy_shield: bool
    cloud_sync: bool

    # 备考
    exam_name: Optional[str]
    exam_date: Optional[datetime]
    exam_days_left: Optional[int]
    night_mode_auto: bool

    # 特色
    emotion_sensitivity: str
    ai_catchphrase: Optional[str]
    special_dates: List[Dict[str, Any]]
    sleep_mode: bool

    class Config:
        from_attributes = True


# ==================== 对话相关 ====================

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    mode: Optional[str] = Field("auto", pattern="^(auto|normal|night|exam|sleep)$")


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
    mood: str = Field(..., pattern="^(anxious|calm|confident|sad|happy|tired|angry|love)$")
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
    period: str
    emotion_distribution: dict
    average_score: float
    summary: MoodSummary
    mood_logs: List[MoodLogResponse]


# ==================== 每日激励 ====================

class DailyMotivation(BaseModel):
    message: str
    exam_countdown: Optional[int]
    exam_name: Optional[str]