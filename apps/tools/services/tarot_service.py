"""
塔罗牌服务类
处理塔罗牌相关的业务逻辑
"""

import random
import logging
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.db import models
import requests

from ..models.tarot_models import TarotCard, TarotSpread, TarotReading, TarotEnergyCalendar

logger = logging.getLogger(__name__)


class TarotService:
    """塔罗牌服务类"""
    
    def __init__(self):
        self.all_cards = None
        self.spreads = None
    
    def get_all_cards(self):
        """获取所有塔罗牌"""
        if self.all_cards is None:
            self.all_cards = list(TarotCard.objects.all())
        return self.all_cards
    
    def get_spreads(self):
        """获取所有牌阵"""
        if self.spreads is None:
            self.spreads = list(TarotSpread.objects.filter(is_active=True))
        return self.spreads
    
    def draw_cards(self, spread, count=None):
        """抽取塔罗牌"""
        all_cards = self.get_all_cards()
        if not all_cards:
            raise ValueError("没有可用的塔罗牌")
        
        # 确定抽取数量
        if count is None:
            count = spread.card_count
        
        # 随机抽取牌
        selected_cards = random.sample(all_cards, min(count, len(all_cards)))
        drawn_cards = []
        
        for i, card in enumerate(selected_cards):
            is_reversed = random.choice([True, False])
            position = spread.positions[i] if i < len(spread.positions) else f'位置{i+1}'
            
            drawn_cards.append({
                'card': {
                    'id': card.id,
                    'name': card.name,
                    'name_en': card.name_en,
                    'card_type': card.card_type,
                    'suit': card.suit,
                    'number': card.number,
                    'image_url': card.image_url
                },
                'position': position,
                'is_reversed': is_reversed,
                'meaning': card.reversed_meaning if is_reversed else card.upright_meaning,
                'keywords': card.keywords
            })
        
        return drawn_cards
    
    def create_reading(self, user, spread, reading_type, question, mood_before=None):
        """创建占卜记录"""
        try:
            # 抽取牌
            drawn_cards = self.draw_cards(spread)
            
            # 生成AI解读
            ai_interpretation = self.generate_ai_interpretation(spread, drawn_cards, question, reading_type)
            
            # 保存占卜记录
            reading = TarotReading.objects.create(
                user=user,
                spread=spread,
                reading_type=reading_type,
                question=question,
                drawn_cards=drawn_cards,
                card_positions=spread.positions,
                ai_interpretation=ai_interpretation,
                mood_before=mood_before
            )
            
            return reading
            
        except Exception as e:
            logger.error(f"创建占卜记录失败: {str(e)}")
            raise
    
    def generate_ai_interpretation(self, spread, drawn_cards, question, reading_type):
        """生成AI解读"""
        try:
            # 构建提示词
            prompt = self._build_interpretation_prompt(spread, drawn_cards, question, reading_type)
            
            # 调用AI API
            interpretation = self._call_ai_api(prompt)
            
            if interpretation:
                return interpretation
            
            # 如果AI API不可用，返回默认解读
            return self._generate_default_interpretation(spread, drawn_cards, question, reading_type)
            
        except Exception as e:
            logger.error(f"生成AI解读失败: {str(e)}")
            return self._generate_default_interpretation(spread, drawn_cards, question, reading_type)
    
    def _build_interpretation_prompt(self, spread, drawn_cards, question, reading_type):
        """构建解读提示词"""
        prompt = f"""
作为一位经验丰富的塔罗牌解读师，请为以下占卜提供专业的解读：

占卜类型：{reading_type}
问题：{question}
牌阵：{spread.name}（{spread.card_count}张牌）

抽到的牌：
"""
        
        for card_data in drawn_cards:
            card = card_data['card']
            position = card_data['position']
            is_reversed = card_data['is_reversed']
            meaning = card_data['meaning']
            
            prompt += f"- {position}：{card['name']}（{'逆位' if is_reversed else '正位'}）\n"
            prompt += f"  含义：{meaning}\n"
        
        prompt += """
请提供：
1. 整体解读：结合所有牌面，给出对问题的整体分析
2. 各位置解读：详细解释每张牌在对应位置的含义
3. 建议指导：基于解读结果，给出具体的建议和指导
4. 注意事项：提醒需要注意的方面

请用温暖、专业且易懂的语言进行解读。
"""
        
        return prompt
    
    def _call_ai_api(self, prompt):
        """调用AI API"""
        try:
            # 获取API密钥
            api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
            if not api_key:
                return None
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'deepseek-chat',
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            
            return None
            
        except Exception as e:
            logger.error(f"调用AI API失败: {str(e)}")
            return None
    
    def _generate_default_interpretation(self, spread, drawn_cards, question, reading_type):
        """生成默认解读"""
        interpretation = f"基于{spread.name}的占卜结果，为您解读如下：\n\n"
        
        # 整体解读
        interpretation += "【整体解读】\n"
        interpretation += f"您的问题是关于{reading_type}的，通过{spread.name}的指引，我们可以看到一些重要的信息。\n\n"
        
        # 各位置解读
        interpretation += "【各位置解读】\n"
        for card_data in drawn_cards:
            card = card_data['card']
            position = card_data['position']
            is_reversed = card_data['is_reversed']
            meaning = card_data['meaning']
            
            interpretation += f"{position}：{card['name']}（{'逆位' if is_reversed else '正位'}）\n"
            interpretation += f"{meaning}\n\n"
        
        # 建议指导
        interpretation += "【建议指导】\n"
        interpretation += "请保持开放的心态，相信自己的直觉。塔罗牌是指导而非决定，最终的选择权在您手中。\n\n"
        
        # 注意事项
        interpretation += "【注意事项】\n"
        interpretation += "塔罗牌解读仅供参考，请理性对待。重要的决定需要结合实际情况综合考虑。"
        
        return interpretation
    
    def get_daily_energy(self, date=None):
        """获取每日能量"""
        if date is None:
            date = datetime.now().date()
        
        # 检查缓存
        cache_key = f'tarot_daily_energy_{date}'
        daily_energy = cache.get(cache_key)
        
        if daily_energy:
            return daily_energy
        
        # 获取今日能量日历
        try:
            energy_calendar = TarotEnergyCalendar.objects.get(date=date)
            daily_energy = {
                'date': date.isoformat(),
                'energy_type': energy_calendar.get_energy_type_display(),
                'energy_level': energy_calendar.energy_level,
                'description': energy_calendar.description,
                'recommended_cards': energy_calendar.recommended_cards,
                'special_reading': energy_calendar.special_reading
            }
        except TarotEnergyCalendar.DoesNotExist:
            # 生成默认每日能量
            all_cards = self.get_all_cards()
            daily_card = random.choice(all_cards) if all_cards else None
            
            daily_energy = {
                'date': date.isoformat(),
                'energy_type': '日常能量',
                'energy_level': random.randint(6, 10),
                'description': f'今天是充满活力的一天，适合尝试新事物，保持开放的心态。',
                'recommended_cards': [daily_card.name] if daily_card else [],
                'special_reading': '今天是一个适合突破自我的日子，勇敢地面对挑战吧！',
                'lucky_color': random.choice(['红色', '蓝色', '绿色', '黄色', '紫色']),
                'lucky_number': random.randint(1, 99)
            }
        
        # 缓存24小时
        cache.set(cache_key, daily_energy, 86400)
        
        return daily_energy
    
    def get_user_readings(self, user, limit=20):
        """获取用户占卜历史"""
        return TarotReading.objects.filter(user=user).order_by('-created_at')[:limit]
    
    def get_reading_detail(self, reading_id, user):
        """获取占卜详情"""
        try:
            return TarotReading.objects.get(id=reading_id, user=user)
        except TarotReading.DoesNotExist:
            return None
    
    def submit_feedback(self, reading_id, user, feedback, rating, mood_after):
        """提交反馈"""
        try:
            reading = TarotReading.objects.get(id=reading_id, user=user)
            reading.user_feedback = feedback
            reading.accuracy_rating = rating
            reading.mood_after = mood_after
            reading.save()
            return True
        except TarotReading.DoesNotExist:
            return False
    
    def get_reading_statistics(self, user):
        """获取占卜统计"""
        readings = TarotReading.objects.filter(user=user)
        
        stats = {
            'total_readings': readings.count(),
            'reading_types': {},
            'average_rating': 0,
            'favorite_spreads': {},
            'mood_changes': {}
        }
        
        if readings.exists():
            # 统计占卜类型
            for reading in readings:
                reading_type = reading.get_reading_type_display()
                stats['reading_types'][reading_type] = stats['reading_types'].get(reading_type, 0) + 1
            
            # 统计平均评分
            rated_readings = readings.exclude(accuracy_rating__isnull=True)
            if rated_readings.exists():
                stats['average_rating'] = rated_readings.aggregate(
                    avg_rating=models.Avg('accuracy_rating')
                )['avg_rating']
            
            # 统计常用牌阵
            for reading in readings:
                spread_name = reading.spread.name
                stats['favorite_spreads'][spread_name] = stats['favorite_spreads'].get(spread_name, 0) + 1
            
            # 统计心情变化
            for reading in readings:
                if reading.mood_before and reading.mood_after:
                    mood_pair = f"{reading.mood_before} → {reading.mood_after}"
                    stats['mood_changes'][mood_pair] = stats['mood_changes'].get(mood_pair, 0) + 1
        
        return stats
    
    def get_card_meaning(self, card_id):
        """获取牌面含义"""
        try:
            card = TarotCard.objects.get(id=card_id)
            return {
                'name': card.name,
                'name_en': card.name_en,
                'upright_meaning': card.upright_meaning,
                'reversed_meaning': card.reversed_meaning,
                'keywords': card.keywords,
                'description': card.description
            }
        except TarotCard.DoesNotExist:
            return None
    
    def search_cards(self, keyword):
        """搜索塔罗牌"""
        return TarotCard.objects.filter(
            models.Q(name__icontains=keyword) |
            models.Q(name_en__icontains=keyword) |
            models.Q(keywords__contains=[keyword])
        )
    
    def get_spread_detail(self, spread_id):
        """获取牌阵详情"""
        try:
            return TarotSpread.objects.get(id=spread_id)
        except TarotSpread.DoesNotExist:
            return None 