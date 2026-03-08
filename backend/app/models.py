"""
数据库模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    nickname = Column(String(50), default="同学")  # 用户昵称
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    conversations = relationship("Conversation", back_populates="user")
    mood_logs = relationship("MoodLog", back_populates="user")


class UserProfile(Base):
    """用户画像/个性化设置（完整版）"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # ── 模块1：核心身份人设 ──
    ai_name = Column(String(20), default="小暖")          # AI昵称
    role_template = Column(String(30), default="warm_friend")  # 角色模板
    gender_feel = Column(String(10), default="none")      # 性别感: male/female/none
    age_feel = Column(String(10), default="youth")         # 年龄感: teen/youth/mature/none
    personality_tags = Column(JSON, default=list)          # 性格标签(最多3个)
    
    # ── 模块2：交互风格 ──
    companion_style = Column(String(20), default="warm")   # 语气: warm/energetic/calm/humor/minimal
    reply_length = Column(String(10), default="normal")    # 回复长度: short/normal/detailed
    address_mode = Column(String(20), default="nickname")  # 称呼方式
    custom_address = Column(String(20), nullable=True)     # 自定义称呼
    emoji_habit = Column(String(10), default="sometimes")  # 表情习惯: always/sometimes/never
    
    # ── 模块3：陪伴场景 ──
    focus_scenarios = Column(JSON, default=list)           # 选中的陪伴场景列表
    
    # ── 模块4：主动交互边界 ──
    proactive_level = Column(String(10), default="moderate")  # very/moderate/passive
    proactive_behaviors = Column(JSON, default=list)          # 主动行为列表
    available_time = Column(String(10), default="allday")     # allday/daytime/nighttime/custom
    available_start = Column(String(5), nullable=True)        # 自定义起始时间 "08:00"
    available_end = Column(String(5), nullable=True)          # 自定义结束时间 "22:00"
    
    # ── 模块5：话题与内容边界 ──
    preferred_topics = Column(JSON, default=list)             # 偏好话题
    forbidden_topics = Column(JSON, default=list)             # 禁止话题勾选项
    custom_forbidden_words = Column(JSON, default=list)       # 自定义屏蔽词
    forbidden_phrases = Column(JSON, default=list)            # 禁止说的话
    
    # ── 模块6：形象/语音设定 ──
    avatar_style = Column(String(20), default="cartoon")      # 二次元/卡通/简约/写实
    theme_skin = Column(String(20), default="healing_blue")   # 皮肤主题
    voice_tone = Column(String(20), default="neutral")        # 音色
    voice_mood = Column(String(10), default="gentle")         # 语调: gentle/stable/energetic
    
    # ── 模块7：记忆与隐私 ──
    memory_scope = Column(String(20), default="emotions")     # habits/emotions/none
    memory_retention = Column(String(20), default="7days")    # 24h/7days/local/manual
    privacy_shield = Column(Boolean, default=True)            # 自动屏蔽隐私信息
    cloud_sync = Column(Boolean, default=True)                # 云端同步开关
    
    # ── 备考设置（保留） ──
    exam_name = Column(String(50), nullable=True)
    exam_date = Column(DateTime, nullable=True)
    
    # ── 模式设置 ──
    night_mode_auto = Column(Boolean, default=True)
    
    # ── 特色小设定 ──
    emotion_sensitivity = Column(String(10), default="medium")    # high/medium/low
    ai_catchphrase = Column(String(50), nullable=True)            # AI口头禅
    special_dates = Column(JSON, default=list)                    # 纪念日列表 [{name, date}]
    sleep_mode = Column(Boolean, default=False)                   # 助眠模式
    
    # 关联
    user = relationship("User", back_populates="profile")


class Conversation(Base):
    """对话记录"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    role = Column(String(20))  # user/assistant
    content = Column(Text)
    emotion = Column(String(20), nullable=True)
    mode = Column(String(20), default="normal")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")


class MoodLog(Base):
    """情绪打卡记录"""
    __tablename__ = "mood_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    mood = Column(String(20))
    mood_score = Column(Integer)
    note = Column(Text, nullable=True)
    scene = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="mood_logs")