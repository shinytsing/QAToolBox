import random
import json
from datetime import datetime, date
from django.db import transaction
from django.utils import timezone
from ..models import (
    TarotCard, TarotSpread, TarotReading, TarotDiary, 
    TarotEnergyCalendar, TarotCommunity, TarotCommunityComment
)


class TarotService:
    """塔罗牌服务类"""
    
    def __init__(self):
        self.major_arcana = [
            "愚者", "魔术师", "女祭司", "女皇", "皇帝", "教皇", "恋人", "战车",
            "力量", "隐者", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔",
            "高塔", "星星", "月亮", "太阳", "审判", "世界"
        ]
        
        self.minor_arcana = {
            "wands": ["权杖王牌", "权杖二", "权杖三", "权杖四", "权杖五", "权杖六", "权杖七", "权杖八", "权杖九", "权杖十", "权杖侍从", "权杖骑士", "权杖皇后", "权杖国王"],
            "cups": ["圣杯王牌", "圣杯二", "圣杯三", "圣杯四", "圣杯五", "圣杯六", "圣杯七", "圣杯八", "圣杯九", "圣杯十", "圣杯侍从", "圣杯骑士", "圣杯皇后", "圣杯国王"],
            "swords": ["宝剑王牌", "宝剑二", "宝剑三", "宝剑四", "宝剑五", "宝剑六", "宝剑七", "宝剑八", "宝剑九", "宝剑十", "宝剑侍从", "宝剑骑士", "宝剑皇后", "宝剑国王"],
            "pentacles": ["钱币王牌", "钱币二", "钱币三", "钱币四", "钱币五", "钱币六", "钱币七", "钱币八", "钱币九", "钱币十", "钱币侍从", "钱币骑士", "钱币皇后", "钱币国王"]
        }
    
    def initialize_tarot_deck(self):
        """初始化塔罗牌数据库"""
        with transaction.atomic():
            # 创建大阿卡纳
            for i, name in enumerate(self.major_arcana):
                TarotCard.objects.get_or_create(
                    name=name,
                    defaults={
                        'name_en': f"Major Arcana {i}",
                        'card_type': 'major',
                        'suit': 'major',
                        'number': i,
                        'upright_meaning': f"{name}的正位含义",
                        'reversed_meaning': f"{name}的逆位含义",
                        'keywords': [name, "神秘", "命运"],
                        'description': f"{name}的详细描述",
                        'symbolism': f"{name}的象征意义",
                        'advice': f"关于{name}的建议"
                    }
                )
            
            # 创建小阿卡纳
            for suit, cards in self.minor_arcana.items():
                for i, name in enumerate(cards):
                    TarotCard.objects.get_or_create(
                        name=name,
                        defaults={
                            'name_en': f"{suit.title()} {i+1}",
                            'card_type': 'minor',
                            'suit': suit,
                            'number': i + 1,
                            'upright_meaning': f"{name}的正位含义",
                            'reversed_meaning': f"{name}的逆位含义",
                            'keywords': [name, suit, "小阿卡纳"],
                            'description': f"{name}的详细描述",
                            'symbolism': f"{name}的象征意义",
                            'advice': f"关于{name}的建议"
                        }
                    )
    
    def create_default_spreads(self):
        """创建默认牌阵"""
        default_spreads = [
            {
                'name': '三张牌阵',
                'spread_type': 'classic',
                'description': '经典的三张牌阵，代表过去、现在、未来',
                'card_count': 3,
                'positions': [
                    {'position': 1, 'name': '过去', 'description': '代表过去的影响'},
                    {'position': 2, 'name': '现在', 'description': '代表当前的状况'},
                    {'position': 3, 'name': '未来', 'description': '代表未来的发展'}
                ]
            },
            {
                'name': '凯尔特十字',
                'spread_type': 'classic',
                'description': '经典的凯尔特十字牌阵，提供全面的解读',
                'card_count': 10,
                'positions': [
                    {'position': 1, 'name': '中心', 'description': '当前状况'},
                    {'position': 2, 'name': '挑战', 'description': '面临的挑战'},
                    {'position': 3, 'name': '基础', 'description': '问题的基础'},
                    {'position': 4, 'name': '过去', 'description': '过去的影响'},
                    {'position': 5, 'name': '可能', 'description': '可能的结果'},
                    {'position': 6, 'name': '未来', 'description': '未来的发展'},
                    {'position': 7, 'name': '自我', 'description': '自我认知'},
                    {'position': 8, 'name': '环境', 'description': '外部环境'},
                    {'position': 9, 'name': '希望', 'description': '希望和恐惧'},
                    {'position': 10, 'name': '结果', 'description': '最终结果'}
                ]
            },
            {
                'name': '爱情牌阵',
                'spread_type': 'situation',
                'description': '专门用于爱情问题的牌阵',
                'card_count': 5,
                'positions': [
                    {'position': 1, 'name': '你的感受', 'description': '你对这段关系的感受'},
                    {'position': 2, 'name': '对方感受', 'description': '对方对这段关系的感受'},
                    {'position': 3, 'name': '关系现状', 'description': '当前关系的状况'},
                    {'position': 4, 'name': '挑战', 'description': '关系中的挑战'},
                    {'position': 5, 'name': '建议', 'description': '如何改善关系'}
                ]
            },
            {
                'name': '事业牌阵',
                'spread_type': 'situation',
                'description': '专门用于事业发展的牌阵',
                'card_count': 6,
                'positions': [
                    {'position': 1, 'name': '当前工作', 'description': '当前工作状况'},
                    {'position': 2, 'name': '技能优势', 'description': '你的技能和优势'},
                    {'position': 3, 'name': '发展机会', 'description': '职业发展机会'},
                    {'position': 4, 'name': '挑战障碍', 'description': '面临的挑战和障碍'},
                    {'position': 5, 'name': '建议行动', 'description': '建议采取的行动'},
                    {'position': 6, 'name': '未来前景', 'description': '职业发展前景'}
                ]
            }
        ]
        
        with transaction.atomic():
            for spread_data in default_spreads:
                TarotSpread.objects.get_or_create(
                    name=spread_data['name'],
                    defaults=spread_data
                )
    
    def draw_cards(self, spread_id, card_count=None):
        """抽牌"""
        try:
            spread = TarotSpread.objects.get(id=spread_id)
            if card_count is None:
                card_count = spread.card_count
            
            # 获取所有可用的牌
            all_cards = list(TarotCard.objects.all())
            
            # 随机抽牌
            drawn_cards = random.sample(all_cards, min(card_count, len(all_cards)))
            
            # 为每张牌随机决定正逆位
            card_results = []
            for i, card in enumerate(drawn_cards):
                is_reversed = random.choice([True, False])
                card_results.append({
                    'card': {
                        'id': card.id,
                        'name': card.name,
                        'name_en': card.name_en,
                        'suit': card.suit,
                        'card_type': card.card_type,
                        'number': card.number,
                        'image_url': card.image_url
                    },
                    'position': i + 1,
                    'is_reversed': is_reversed,
                    'meaning': card.reversed_meaning if is_reversed else card.upright_meaning,
                    'keywords': card.keywords
                })
            
            return card_results
        except TarotSpread.DoesNotExist:
            return None
    
    def create_reading(self, user, spread_id, reading_type, question, mood_before=None):
        """创建占卜记录"""
        try:
            spread = TarotSpread.objects.get(id=spread_id)
            drawn_cards = self.draw_cards(spread_id)
            
            if not drawn_cards:
                return None
            
            reading = TarotReading.objects.create(
                user=user,
                spread=spread,
                reading_type=reading_type,
                question=question,
                drawn_cards=drawn_cards,
                card_positions=spread.positions,
                mood_before=mood_before
            )
            
            return reading
        except TarotSpread.DoesNotExist:
            return None
    
    def generate_ai_interpretation(self, reading):
        """生成AI解读"""
        # 这里可以集成AI服务，目前返回基础解读
        interpretation = f"基于您的问题：{reading.question}\n\n"
        interpretation += f"使用{reading.spread.name}为您进行占卜，以下是详细解读：\n\n"
        
        for card_data in reading.drawn_cards:
            card = card_data['card']
            position = card_data['position']
            is_reversed = card_data['is_reversed']
            
            # 找到对应的位置描述
            position_desc = ""
            for pos in reading.card_positions:
                if pos['position'] == position:
                    position_desc = pos['description']
                    break
            
            interpretation += f"第{position}张牌：{card['name']}"
            if is_reversed:
                interpretation += "（逆位）"
            interpretation += f"\n位置含义：{position_desc}\n"
            interpretation += f"牌义：{card_data['meaning']}\n\n"
        
        interpretation += "总体建议：请根据牌面含义，结合您的具体情况来理解这次占卜的结果。"
        
        return interpretation
    
    def save_reading_with_interpretation(self, reading):
        """保存占卜记录并生成解读"""
        interpretation = self.generate_ai_interpretation(reading)
        reading.ai_interpretation = interpretation
        reading.save()
        return reading
    
    def get_user_readings(self, user, limit=10):
        """获取用户的占卜记录"""
        return TarotReading.objects.filter(user=user).order_by('-created_at')[:limit]
    
    def get_daily_energy(self, target_date=None):
        """获取每日能量"""
        if target_date is None:
            target_date = date.today()
        
        try:
            energy = TarotEnergyCalendar.objects.get(date=target_date, energy_type='daily')
            return energy
        except TarotEnergyCalendar.DoesNotExist:
            # 如果没有预设的能量，生成一个
            energy_level = random.randint(1, 10)
            energy_desc = f"{target_date}的能量等级为{energy_level}，适合进行{self._get_energy_description(energy_level)}的占卜。"
            
            energy = TarotEnergyCalendar.objects.create(
                date=target_date,
                energy_type='daily',
                energy_level=energy_level,
                description=energy_desc
            )
            return energy
    
    def _get_energy_description(self, level):
        """根据能量等级获取描述"""
        if level <= 3:
            return "内省和反思"
        elif level <= 6:
            return "平衡和稳定"
        else:
            return "积极和行动"
    
    def create_tarot_diary(self, user, reading_id, title, content, tags=None, is_public=False):
        """创建塔罗日记"""
        try:
            reading = TarotReading.objects.get(id=reading_id, user=user)
            diary = TarotDiary.objects.create(
                user=user,
                reading=reading,
                title=title,
                content=content,
                tags=tags or [],
                is_public=is_public
            )
            return diary
        except TarotReading.DoesNotExist:
            return None
    
    def get_community_posts(self, post_type=None, limit=20):
        """获取社区帖子"""
        queryset = TarotCommunity.objects.filter(is_featured=True)
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        return queryset.order_by('-created_at')[:limit]
    
    def create_community_post(self, user, post_type, title, content, tags=None, is_anonymous=False):
        """创建社区帖子"""
        post = TarotCommunity.objects.create(
            user=user,
            post_type=post_type,
            title=title,
            content=content,
            tags=tags or [],
            is_anonymous=is_anonymous
        )
        return post
    
    def add_community_comment(self, user, post_id, content, parent_comment_id=None):
        """添加社区评论"""
        try:
            post = TarotCommunity.objects.get(id=post_id)
            parent_comment = None
            if parent_comment_id:
                parent_comment = TarotCommunityComment.objects.get(id=parent_comment_id)
            
            comment = TarotCommunityComment.objects.create(
                post=post,
                user=user,
                content=content,
                parent_comment=parent_comment
            )
            
            # 更新帖子评论数
            post.comments_count = post.comments.count()
            post.save()
            
            return comment
        except (TarotCommunity.DoesNotExist, TarotCommunityComment.DoesNotExist):
            return None


class TarotVisualizationService:
    """塔罗牌可视化服务"""
    
    def __init__(self):
        self.colors = {
            'major': '#8B4513',  # 棕色
            'wands': '#FF4500',  # 橙红色
            'cups': '#4169E1',   # 蓝色
            'swords': '#708090',  # 灰色
            'pentacles': '#FFD700'  # 金色
        }
    
    def get_card_color(self, suit):
        """获取牌的颜色"""
        return self.colors.get(suit, '#000000')
    
    def generate_spread_layout(self, spread):
        """生成牌阵布局"""
        positions = spread.positions
        layout = {
            'type': 'grid',
            'positions': []
        }
        
        for pos in positions:
            layout['positions'].append({
                'id': pos['position'],
                'name': pos['name'],
                'description': pos['description'],
                'x': 0,  # 这里可以根据牌阵类型计算具体位置
                'y': 0
            })
        
        return layout
    
    def get_energy_visualization(self, energy):
        """获取能量可视化数据"""
        return {
            'level': energy.energy_level,
            'color': self._get_energy_color(energy.energy_level),
            'description': energy.description,
            'recommended_cards': energy.recommended_cards
        }
    
    def _get_energy_color(self, level):
        """根据能量等级获取颜色"""
        if level <= 3:
            return '#FF6B6B'  # 红色
        elif level <= 6:
            return '#4ECDC4'  # 青色
        else:
            return '#45B7D1'  # 蓝色 