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
    """用户画像/个性化设置"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # AI伴侣设置
    ai_name = Column(String(20), default="小暖")  # AI昵称
    companion_style = Column(String(20), default="warm")  # warm/casual/calm 温暖/轻松/冷静
    
    # 场景偏好
    focus_scenarios = Column(JSON, default=list)  # ["备考压力", "宿舍矛盾"]
    forbidden_phrases = Column(JSON, default=list)  # ["别想太多", "这不算什么"]
    
    # 备考设置
    exam_name = Column(String(50), nullable=True)  # "2026高考"
    exam_date = Column(DateTime, nullable=True)
    
    # 模式设置
    night_mode_auto = Column(Boolean, default=True)  # 是否自动开启深夜模式
    
    # 关联
    user = relationship("User", back_populates="profile")


class Conversation(Base):
    """对话记录"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    role = Column(String(20))  # user/assistant
    content = Column(Text)
    emotion = Column(String(20), nullable=True)  # 识别到的情绪
    mode = Column(String(20), default="normal")  # normal/night/exam 普通/深夜/备考
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    user = relationship("User", back_populates="conversations")


class MoodLog(Base):
    """情绪打卡记录"""
    __tablename__ = "mood_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    mood = Column(String(20))  # anxious/calm/confident/sad/happy
    mood_score = Column(Integer)  # 1-10
    note = Column(Text, nullable=True)  # 备注
    scene = Column(String(50), nullable=True)  # 场景：exam/daily
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    user = relationship("User", back_populates="mood_logs")
