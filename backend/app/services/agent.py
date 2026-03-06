"""
AI治愈心理Agent核心服务
基于ReAct框架：思考 -> 行动 -> 观察 循环
"""
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from openai import AsyncOpenAI

from app.config import settings


class HealingAgent:
    """心理治愈Agent"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_API_BASE
        )
        self.model = settings.QWEN_MODEL
        
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
        
        base_prompt = f"""你叫{ai_name}，是{user_nickname}的专属心理陪伴伙伴。

## 你的性格
{style_desc.get(style, style_desc["warm"])}

## 核心原则
1. **倾听优先**：先理解对方的感受，再给予回应
2. **共情表达**：用"我理解/我感受到/听起来..."等表达共情
3. **具体化回应**：针对对方说的具体事情回应，不说空洞的鸡汤
4. **不评判**：不批评、不说教，只陪伴和支持
5. **适度引导**：在对方需要时，温和地引导思考

## 绝对禁止
{json.dumps(forbidden, ensure_ascii=False) if forbidden else '["别想太多", "这点小事不算什么", "你应该坚强一点", "加油就好了"]'}

## 输出格式要求（非常重要）
- **只输出纯文字对话**，不要任何动作描写
- **禁止**使用括号描述动作，如：（递上纸条）、*轻轻拍肩*、（悄悄地说）
- **禁止**使用小说式的旁白描写
- 直接用文字表达关心，例如"我在听你说"而不是"（认真倾听的样子）"
- 回复控制在50-100字，简洁有力
- 可以适当使用emoji表情，如 😊 🤗 💪

## 对话技巧
- 遵循"倾听→确认→共情→引导"的四步法
- 如果对方情绪很低落，优先倾听，减少追问
- 用温暖的语气，但不要过度夸张

## 重要提醒
- 你不是心理医生，不做诊断
- 如果识别到自杀/自伤倾向，要温和地建议寻求专业帮助
- 记住之前的对话内容，保持连贯性
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

    # ==================== 情绪识别 ====================
    
    async def detect_emotion(self, text: str) -> str:
        """识别用户情绪"""
        prompt = f"""分析以下文字表达的主要情绪，只返回一个情绪标签。

可选标签：anxious(焦虑), sad(低落), angry(愤怒), helpless(无助), happy(开心), calm(平静), confused(困惑), tired(疲惫)

文字：{text}

只返回标签，不要其他内容："""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=20
            )
            emotion = response.choices[0].message.content.strip().lower()
            # 验证是否为有效标签
            valid_emotions = {"anxious", "sad", "angry", "helpless", "happy", "calm", "confused", "tired"}
            return emotion if emotion in valid_emotions else "calm"
        except Exception as e:
            print(f"情绪识别失败: {e}")
            return "calm"
    
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
        核心对话方法
        
        Args:
            user_message: 用户消息
            profile: 用户画像
            history: 历史对话 [{"role": "user/assistant", "content": "..."}]
            mode: 模式 normal/night/exam
            exam_info: 备考信息 {"name": "2026高考", "days_left": 100}
            
        Returns:
            (AI回复, 检测到的情绪)
        """
        # 1. 检测情绪
        emotion = await self.detect_emotion(user_message)
        
        # 2. 构建系统提示词
        system_prompt = self._get_base_system_prompt(profile, mode)
        
        if mode == "night":
            system_prompt += self._get_night_mode_prompt()
        elif mode == "exam" and exam_info:
            system_prompt += self._get_exam_mode_prompt(
                exam_info.get("name", "考试"),
                exam_info.get("days_left", 0)
            )
        
        # 添加情绪感知提示
        emotion_hints = {
            "anxious": "对方现在很焦虑，需要被理解和安抚",
            "sad": "对方现在心情低落，需要温暖的陪伴",
            "angry": "对方现在很生气，先让对方发泄，不要急于讲道理",
            "helpless": "对方感到无助，需要支持和力量",
            "tired": "对方很疲惫，可能需要休息建议",
            "confused": "对方感到困惑，可以帮助理清思路"
        }
        if emotion in emotion_hints:
            system_prompt += f"\n\n## 当前情绪感知\n{emotion_hints[emotion]}"
        
        # 3. 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史对话（最近10轮）
        if history:
            messages.extend(history[-20:])  # 最多保留20条（10轮对话）
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 4. 调用模型
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=500,
                top_p=0.9
            )
            reply = response.choices[0].message.content.strip()
            return reply, emotion
        except Exception as e:
            print(f"对话生成失败: {e}")
            return "抱歉，我刚才走神了...能再说一遍吗？", emotion
    
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
