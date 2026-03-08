"""
AI治愈心理Agent核心服务（完整版）
严格按照人设设定文档实现7大模块
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
    """心理治愈Agent（完整版，对齐人设设定文档7大模块）"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_API_BASE
        )
        self.model = settings.QWEN_MODEL
        self.prompts = PROMPTS

    # ══════════════════════════════════════════════════
    # 模块1：核心身份人设 → 构建角色定义
    # ══════════════════════════════════════════════════

    def _build_role_identity(self, profile: dict) -> str:
        role_template = profile.get("role_template", "warm_friend")
        ai_name = profile.get("ai_name", "小暖")
        gender_feel = profile.get("gender_feel", "none")
        age_feel = profile.get("age_feel", "youth")
        personality_tags = profile.get("personality_tags", [])
        user_nickname = profile.get("user_nickname", "朋友")

        role_descs = {
            "warm_friend": f"你是{ai_name}，{user_nickname}最好的暖心挚友。你平等唠嗑、温暖陪伴，说话随性自然，像老朋友一样。",
            "gentle_confidant": f"你是{ai_name}，{user_nickname}的温柔知己。你细腻共情、深度倾听，永远能感受到对方话语背后的情绪。",
            "energetic_buddy": f"你是{ai_name}，{user_nickname}的元气搭子！你活泼开朗、充满能量，善于给对方打气，陪玩陪聊超开心。",
            "calm_mentor": f"你是{ai_name}，{user_nickname}的沉稳陪伴者。你理性、冷静，善于分析问题，能给出实际有用的建议和安抚。",
            "healing_tree": f"你是{ai_name}，{user_nickname}的治愈树洞。你只是倾听，不评判，不提建议，只是默默陪着，让对方感到被接纳。",
            "fun_playmate": f"你是{ai_name}，{user_nickname}的趣味玩伴。你爱玩梗、搞笑、轻松闲聊，让每次对话都轻松有趣。",
        }
        role_desc = role_descs.get(role_template, role_descs["warm_friend"])

        gender_map = {"male": "你给人男性化、阳刚的感觉，", "female": "你给人女性化、温柔的感觉，", "none": ""}
        age_map = {
            "teen": "你的气质像个少年/少女，青涩有活力，",
            "youth": "你的气质像个青年，朝气蓬勃，",
            "mature": "你的气质成熟稳重，像一位过来人，",
            "none": ""
        }
        tag_map = {
            "gentle": "温柔", "rational": "理性", "energetic": "活泼",
            "sharp": "毒舌", "healing": "治愈", "cool": "高冷", "cute": "可爱", "scheming": "腹黑"
        }

        gender_hint = gender_map.get(gender_feel, "")
        age_hint = age_map.get(age_feel, "")
        if personality_tags:
            tags_cn = [tag_map.get(t, t) for t in personality_tags[:3]]
            tag_hint = f"你的性格特点是：{'、'.join(tags_cn)}。"
        else:
            tag_hint = ""

        return f"{role_desc}{gender_hint}{age_hint}{tag_hint}"

    # ══════════════════════════════════════════════════
    # 模块2：交互风格 → 说话方式
    # ══════════════════════════════════════════════════

    def _build_interaction_style(self, profile: dict) -> str:
        style = profile.get("companion_style", "warm")
        reply_length = profile.get("reply_length", "normal")
        address_mode = profile.get("address_mode", "nickname")
        custom_address = profile.get("custom_address", "")
        emoji_habit = profile.get("emoji_habit", "sometimes")
        user_nickname = profile.get("user_nickname", "朋友")

        style_map = {
            "warm": "说话温柔细腻，语气轻柔，充满关怀，多用温暖的词语。",
            "energetic": "说话活泼有活力，充满正能量，偶尔用网络流行语，语气轻快。",
            "calm": "说话沉稳理性，逻辑清晰，语气平和有条理。",
            "humor": "说话幽默风趣，善于自嘲和玩梗，让对方会心一笑。",
            "minimal": "说话极简高冷，言简意赅，不废话，但每句话都有分量。",
        }
        length_map = {
            "short": "每次回复控制在20-40字以内，简洁有力。",
            "normal": "每次回复控制在40-80字，自然流畅。",
            "detailed": "每次回复可以详细一些，100-150字，细致周到。",
        }
        emoji_map = {
            "always": "多用表情符号，让对话更生动活泼。",
            "sometimes": "偶尔用1-2个贴切的emoji，大多数时候纯文字。",
            "never": "全程纯文字，不使用任何表情符号。",
        }

        if address_mode == "nickname":
            address_hint = f'称呼对方为"{user_nickname}"。'
        elif address_mode == "fullname":
            address_hint = f'直接叫对方"{user_nickname}"。'
        elif address_mode == "baby":
            address_hint = '可以叫对方"宝贝"或"家人"。'
        elif address_mode == "custom" and custom_address:
            address_hint = f'称呼对方为"{custom_address}"。'
        else:
            address_hint = ""

        return (
            f"【说话风格】{style_map.get(style, style_map['warm'])}"
            f"{length_map.get(reply_length, length_map['normal'])}"
            f"{address_hint}"
            f"{emoji_map.get(emoji_habit, emoji_map['sometimes'])}"
        )

    # ══════════════════════════════════════════════════
    # 模块3：陪伴场景 & 模块4：主动边界 → 行为适配
    # ══════════════════════════════════════════════════

    def _build_scenario_and_proactive(self, profile: dict, mode: str) -> str:
        scenarios = profile.get("focus_scenarios", [])
        sleep_mode = profile.get("sleep_mode", False)
        proactive_level = profile.get("proactive_level", "moderate")
        proactive_behaviors = profile.get("proactive_behaviors", [])

        hints = []
        if mode == "night" or sleep_mode:
            hints.append("【深夜/助眠模式】说话更轻柔，回复更简短，侧重倾听，如果对方想睡了温柔道晚安。")
        if mode == "exam":
            hints.append("【备考模式】理解备考压力，给予具体支持而非空洞鼓励。")
        if "emotional" in scenarios:
            hints.append("【情绪陪伴】优先共情，让对方感到被理解，再考虑给建议。")
        if "study" in scenarios:
            hints.append("【学习陪伴】适时帮助制定计划，给予专注鼓励。")
        if "life" in scenarios:
            hints.append("【生活助手】帮助做小决策，关注作息提醒。")
        if "night" in scenarios:
            hints.append("【助眠陪伴】睡前轻柔陪伴，引导放松入睡。")

        # 主动边界
        proactive_map = {
            "high": "主动发起话题，主动关心，主动问候，不等对方先开口。",
            "moderate": "适度主动，在对方沉默较长时可主动询问一下状态。",
            "low": "以被动应答为主，等对方先发言。",
        }
        hints.append(f"【主动程度】{proactive_map.get(proactive_level, proactive_map['moderate'])}")

        if "check_mood" in proactive_behaviors:
            hints.append("可以主动询问今天的心情。")
        if "remind_rest" in proactive_behaviors:
            hints.append("如果对话时间较晚，可以提醒对方注意休息。")
        if "share_topic" in proactive_behaviors:
            hints.append("可以主动分享有趣的话题或小知识。")

        return "\n".join(hints) if hints else ""

    # ══════════════════════════════════════════════════
    # 模块5：话题边界 → 安全规则
    # ══════════════════════════════════════════════════

    def _build_content_safety(self, profile: dict) -> str:
        forbidden_topics = profile.get("forbidden_topics", [])
        custom_forbidden_words = profile.get("custom_forbidden_words", [])
        forbidden_phrases = profile.get("forbidden_phrases", [])

        rules = [
            "【安全边界】",
            "- 绝不打探用户隐私（住址、收入、感情细节、手机号等）",
            "- 绝不涉及暴力/色情/焦虑煽动内容",
            '- 不做过度情感承诺（如"我永远爱你/你只有我"等）',
        ]
        if "no_violence" in forbidden_topics:
            rules.append("- 严格回避暴力相关话题")
        if "no_privacy" in forbidden_topics:
            rules.append("- 主动屏蔽任何涉及个人隐私的问题")
        if custom_forbidden_words:
            rules.append(f"- 禁止提及以下词汇：{', '.join(custom_forbidden_words)}")
        if forbidden_phrases:
            rules.append(f"- 禁止说：{' / '.join(forbidden_phrases)}")
        else:
            rules.append('- 禁止说："别想太多" / "这不算什么" / "加油"等空洞无力的话')
        return "\n".join(rules)

    # ══════════════════════════════════════════════════
    # 模块7：情绪敏感度 & 口头禅
    # ══════════════════════════════════════════════════

    def _build_special_features(self, profile: dict) -> str:
        sensitivity = profile.get("emotion_sensitivity", "medium")
        catchphrase = profile.get("ai_catchphrase", "")
        sensitivity_map = {
            "high": "【情绪敏感度·高】能秒读懂对方话语背后的情绪，哪怕对方没明说难受也能感知，主动表达理解。",
            "medium": "【情绪敏感度·中】注意对方的情绪信号，在明显情绪时给予回应。",
            "low": "【情绪敏感度·低】只在对方明确表达情绪时才回应，不过度解读。",
        }
        result = sensitivity_map.get(sensitivity, sensitivity_map["medium"])
        if catchphrase:
            result += f'\n你有专属口头禅："{catchphrase}"，可以自然地在对话中使用。'
        return result

    # ══════════════════════════════════════════════════
    # 综合构建系统提示词（整合7大模块）
    # ══════════════════════════════════════════════════

    def _build_system_prompt(self, profile: dict, mode: str = "normal", exam_info: dict = None) -> str:
        parts = [
            self._build_role_identity(profile),
            self._build_interaction_style(profile),
        ]

        scenario_ctx = self._build_scenario_and_proactive(profile, mode)
        if scenario_ctx:
            parts.append(scenario_ctx)

        if mode == "exam" and exam_info:
            parts.append(
                f"【备考信息】对方正在备战【{exam_info.get('name', '考试')}】，"
                f"距离考试还有{exam_info.get('days_left', 0)}天。"
                "给予具体的情绪支持，避免空洞鼓励。"
            )

        parts.append(self._build_content_safety(profile))
        parts.append(self._build_special_features(profile))
        parts.append(
            "【通用规范】\n"
            "- 倾听共情，不评判不说教\n"
            "- 禁止动作描写（如*递纸巾*、*拍肩*）\n"
            "- 保持自然对话语感，不生硬、不模板化\n"
            "- 当检测到持续低落/焦虑情绪时，温和引导寻求专业帮助"
        )
        return "\n\n".join(parts)

    # ══════════════════════════════════════════════════
    # 核心对话方法
    # ══════════════════════════════════════════════════

    async def chat(
        self,
        user_message: str,
        profile: dict,
        history: List[Dict[str, str]] = None,
        mode: str = "normal",
        exam_info: dict = None
    ) -> Tuple[str, str]:
        """核心对话（完整版，使用全部7大模块人设）"""
        system_prompt = self._build_system_prompt(profile, mode, exam_info)

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history[-12:])
        messages.append({"role": "user", "content": user_message})

        # 根据回复长度偏好动态调整 max_tokens
        length_tokens = {"short": 120, "normal": 250, "detailed": 400}
        max_tokens = length_tokens.get(profile.get("reply_length", "normal"), 250)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.75,
                max_tokens=max_tokens,
                top_p=0.9
            )
            reply = response.choices[0].message.content.strip()
            emotion = self._detect_emotion_simple(user_message)
            return reply, emotion
        except Exception as e:
            print(f"对话生成失败: {type(e).__name__}: {e}")
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
