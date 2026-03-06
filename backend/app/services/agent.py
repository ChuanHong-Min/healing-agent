"""
AI治愈心理Agent核心服务
基于ReAct框架：思考 -> 行动 -> 观察 循环
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from openai import AsyncOpenAI

from app.config import settings


def load_prompts() -> dict:
    """加载提示词配置文件"""
    prompts_path = os.path.join(os.path.dirname(__file__), "prompts.json")
    try:
        with open(prompts_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载提示词配置失败: {e}")
        return {}


# 全局提示词配置
PROMPTS = load_prompts()


class HealingAgent:
    """心理治愈Agent"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_API_BASE
        )
        self.model = settings.QWEN_MODEL
        self.prompts = PROMPTS
        
    # ==================== 系统提示词 ====================
    
    def _get_base_system_prompt(self, profile: dict, mode: str = "normal") -> str:
        """获取基础系统提示词"""
        ai_name = profile.get("ai_name", "小暖")
        style = profile.get("companion_style", "warm")
        forbidden = profile.get("forbidden_phrases", [])
        user_nickname = profile.get("user_nickname", "同学")
        
        # 风格定义
        style_desc = {
            "warm": "你是一个温暖体贴的姐姐，说话温柔细腻，善于倾听和安慰，会用温暖的语言让对方感到被理解和关爱。",
            "casual": "你是一个轻松活泼的同龄伙伴，说话幽默风趣，善于用轻松的方式化解压力，会用emoji和网络用语拉近距离。",
            "calm": "你是一个沉稳冷静的学长，说话理性有条理，善于分析问题，会用客观的视角帮助对方看清状况。"
        }
        
        base_prompt = f"""你是{ai_name}，{user_nickname}的心理陪伴伙伴。{style_desc.get(style, style_desc["warm"])}

规则：
- 倾听共情，不评判不说教
- 禁止动作描写如（递纸条）、*拍肩*
- 回复30-60字，简洁温暖
- emoji偶尔用1个或不用，大部分回复不需要emoji
- 禁止说：{json.dumps(forbidden, ensure_ascii=False) if forbidden else '别想太多/这不算什么/加油'}
"""
        return base_prompt
    
    def _get_night_mode_prompt(self) -> str:
        """深夜模式额外提示"""
        return """
## 深夜模式特别提醒
现在是深夜时分，请注意：
- 说话更轻柔，语气更温和
- 回复更简短（30-50字），不要长篇大论
- 侧重倾听，减少追问
- 如果对方想睡了，温柔地道晚安
- 可以适当提醒对方注意休息
"""
    
    def _get_exam_mode_prompt(self, exam_name: str, days_left: int) -> str:
        """备考模式额外提示"""
        return f"""
## 备考模式特别提醒
对方正在备战【{exam_name}】，距离考试还有{days_left}天。
请注意：
- 理解备考压力，不要说"考试不重要"
- 针对"刷题焦虑/模拟考失利/作息紊乱"等场景给予支持
- 适当鼓励，但不要空洞地说"加油"
- 如果对方太焦虑，引导放松，而不是继续聊学习
- 可以分享一些实用的减压小技巧
"""

    # ==================== 核心对话 ====================
    
    async def chat(
        self,
        user_message: str,
        profile: dict,
        history: List[Dict[str, str]] = None,
        mode: str = "normal",
        exam_info: dict = None
    ) -> Tuple[str, str]:
        """
        核心对话方法（稳定版：直接输出文本，简单情绪检测）
        """
        # 1. 构建系统提示词
        system_prompt = self._get_base_system_prompt(profile, mode)
        
        if mode == "night":
            system_prompt += self._get_night_mode_prompt()
        elif mode == "exam" and exam_info:
            system_prompt += self._get_exam_mode_prompt(
                exam_info.get("name", "考试"),
                exam_info.get("days_left", 0)
            )
        
        # 2. 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史对话（最近6轮）
        if history:
            messages.extend(history[-12:])
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 3. 调用模型
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=200,
                top_p=0.9
            )
            reply = response.choices[0].message.content.strip()
            
            # 简单情绪检测（基于关键词，不再额外调用API）
            emotion = self._detect_emotion_simple(user_message)
            
            return reply, emotion
        except Exception as e:
            print(f"对话生成失败: {type(e).__name__}: {e}")
            # 返回一个友好的备用回复
            return "我在听你说，可以再说一遍吗？", "calm"
    
    def _detect_emotion_simple(self, text: str) -> str:
        """简单情绪检测（基于关键词，无需API调用）"""
        text_lower = text.lower()
        
        # 情绪关键词映射
        emotion_keywords = {
            "anxious": ["焦虑", "紧张", "担心", "害怕", "恐惧", "不安", "慌"],
            "sad": ["难过", "伤心", "哭", "失落", "沮丧", "绝望", "心痛"],
            "angry": ["生气", "愤怒", "烦", "讨厌", "恨", "火大", "气死"],
            "tired": ["累", "疲惫", "困", "没劲", "乏", "精疲力竭"],
            "helpless": ["无助", "无奈", "没办法", "不知道怎么办", "绝望"],
            "confused": ["迷茫", "困惑", "不懂", "搞不清", "纠结"],
            "happy": ["开心", "高兴", "快乐", "棒", "好消息", "太好了"]
        }
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return emotion
        
        return "calm"
    
    # ==================== 每日激励 ====================
    
    async def generate_daily_motivation(self, profile: dict, exam_info: dict = None) -> str:
        """生成每日激励语"""
        user_nickname = profile.get("user_nickname", "同学")
        ai_name = profile.get("ai_name", "小暖")
        
        if exam_info:
            prompt = f"""你是{ai_name}，为正在备战{exam_info.get('name', '考试')}的{user_nickname}写一句简短的每日激励。

要求：
- 不超过30字
- 不要说"加油"这种空洞的话
- 要具体、真诚、有力量
- 可以适当用emoji

只返回激励语本身："""
        else:
            prompt = f"""你是{ai_name}，为{user_nickname}写一句温暖的早安问候。

要求：
- 不超过30字
- 温暖、轻松、有力量
- 可以适当用emoji

只返回问候语本身："""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"生成激励语失败: {e}")
            return "今天也要好好的呀 ✨"
    
    # ==================== 情绪报告 ====================
    
    async def generate_mood_summary(
        self,
        mood_logs: List[dict],
        conversations: List[dict],
        profile: dict
    ) -> dict:
        """生成情绪总结报告"""
        user_nickname = profile.get("user_nickname", "同学")
        
        # 统计情绪分布
        emotion_counts = {}
        for log in mood_logs:
            mood = log.get("mood", "calm")
            emotion_counts[mood] = emotion_counts.get(mood, 0) + 1
        
        # 从对话中提取高频场景
        all_content = " ".join([c.get("content", "") for c in conversations if c.get("role") == "user"])
        
        prompt = f"""基于以下信息，为{user_nickname}生成一份简短的情绪总结。

情绪统计：{json.dumps(emotion_counts, ensure_ascii=False)}
近期倾诉内容摘要：{all_content[:500]}

请返回JSON格式：
{{
    "main_emotion": "主要情绪",
    "emotion_trend": "情绪趋势描述（一句话）",
    "main_stressor": "主要压力源（如果有）",
    "positive_point": "一个值得肯定的点",
    "suggestion": "一条温和的建议"
}}

只返回JSON："""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            result = response.choices[0].message.content.strip()
            # 尝试解析JSON
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            return json.loads(result)
        except Exception as e:
            print(f"生成情绪报告失败: {e}")
            return {
                "main_emotion": "平静",
                "emotion_trend": "情绪整体稳定",
                "main_stressor": "无明显压力源",
                "positive_point": "你一直在坚持记录，这很棒",
                "suggestion": "继续保持，有任何想说的随时来找我"
            }


# 单例模式
_agent_instance = None

def get_agent() -> HealingAgent:
    """获取Agent实例"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = HealingAgent()
    return _agent_instance
