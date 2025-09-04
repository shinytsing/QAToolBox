# QAToolbox/apps/tools/views/tarot_views.py
"""
塔罗牌相关的视图函数
"""

import json
import logging
import random
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import requests

from ..models.tarot_models import TarotCard, TarotEnergyCalendar, TarotReading, TarotSpread

logger = logging.getLogger(__name__)

# 完整的塔罗牌数据
TAROT_CARDS_DATA = [
    # 大阿卡纳
    {
        "name": "愚者",
        "name_en": "The Fool",
        "card_type": "major",
        "suit": "major",
        "number": 0,
        "upright_meaning": "新的开始、冒险、纯真、自由、可能性、自发性",
        "reversed_meaning": "鲁莽、不负责任、过度冒险、缺乏计划",
        "keywords": ["新开始", "冒险", "纯真", "自由", "可能性"],
        "description": "愚者代表新的开始和无限的可能性。他带着简单的行囊，站在悬崖边缘，准备踏上未知的旅程。",
    },
    {
        "name": "魔术师",
        "name_en": "The Magician",
        "card_type": "major",
        "suit": "major",
        "number": 1,
        "upright_meaning": "创造力、技能、意志力、自信、新机会、行动力",
        "reversed_meaning": "技能不足、机会错失、缺乏自信、滥用权力",
        "keywords": ["创造力", "技能", "意志力", "自信", "机会"],
        "description": "魔术师拥有所有的工具和技能，能够将想法转化为现实。他象征着创造力和行动力。",
    },
    {
        "name": "女祭司",
        "name_en": "The High Priestess",
        "card_type": "major",
        "suit": "major",
        "number": 2,
        "upright_meaning": "直觉、神秘、内在知识、智慧、潜意识、神秘学",
        "reversed_meaning": "隐藏的信息、表面化、缺乏深度、过度理性",
        "keywords": ["直觉", "神秘", "智慧", "潜意识", "内在知识"],
        "description": "女祭司坐在两根柱子之间，象征着平衡和内在的智慧。她代表直觉和神秘的知识。",
    },
    {
        "name": "女皇",
        "name_en": "The Empress",
        "card_type": "major",
        "suit": "major",
        "number": 3,
        "upright_meaning": "丰饶、母性、创造力、自然、繁荣、滋养",
        "reversed_meaning": "过度保护、依赖、缺乏创造力、生育问题",
        "keywords": ["丰饶", "母性", "创造力", "自然", "繁荣"],
        "description": "女皇象征着丰饶和创造力，她与自然和谐相处，代表生命的力量和母性的滋养。",
    },
    {
        "name": "皇帝",
        "name_en": "The Emperor",
        "card_type": "major",
        "suit": "major",
        "number": 4,
        "upright_meaning": "权威、领导力、稳定、结构、控制、成就",
        "reversed_meaning": "专制、控制欲过强、缺乏灵活性、权力滥用",
        "keywords": ["权威", "领导力", "稳定", "结构", "控制"],
        "description": "皇帝代表权威和领导力，他建立秩序和结构，确保稳定和安全。",
    },
    {
        "name": "教皇",
        "name_en": "The Hierophant",
        "card_type": "major",
        "suit": "major",
        "number": 5,
        "upright_meaning": "传统、教育、精神指导、信仰、道德、学习",
        "reversed_meaning": "教条主义、反叛、质疑权威、非传统方法",
        "keywords": ["传统", "教育", "精神指导", "信仰", "道德"],
        "description": "教皇代表传统教育和精神指导，他传授知识和道德价值观。",
    },
    {
        "name": "恋人",
        "name_en": "The Lovers",
        "card_type": "major",
        "suit": "major",
        "number": 6,
        "upright_meaning": "爱情、和谐、选择、关系、价值观、统一",
        "reversed_meaning": "不和谐、价值观冲突、分离、错误选择",
        "keywords": ["爱情", "和谐", "选择", "关系", "价值观"],
        "description": "恋人牌代表爱情和和谐的关系，也象征着重要的选择和价值观的统一。",
    },
    {
        "name": "战车",
        "name_en": "The Chariot",
        "card_type": "major",
        "suit": "major",
        "number": 7,
        "upright_meaning": "胜利、意志力、决心、控制、前进、成功",
        "reversed_meaning": "缺乏方向、失控、失败、意志力薄弱",
        "keywords": ["胜利", "意志力", "决心", "控制", "前进"],
        "description": "战车代表胜利和成功，通过意志力和决心克服困难，向前进发。",
    },
    {
        "name": "力量",
        "name_en": "Strength",
        "card_type": "major",
        "suit": "major",
        "number": 8,
        "upright_meaning": "内在力量、勇气、耐心、温和、控制、信心",
        "reversed_meaning": "自我怀疑、缺乏信心、过度控制、软弱",
        "keywords": ["内在力量", "勇气", "耐心", "温和", "控制"],
        "description": "力量牌代表内在的力量和勇气，通过温和和耐心来控制和引导能量。",
    },
    {
        "name": "隐者",
        "name_en": "The Hermit",
        "card_type": "major",
        "suit": "major",
        "number": 9,
        "upright_meaning": "独处、内省、智慧、指导、寻找、孤独",
        "reversed_meaning": "过度孤独、缺乏指导、迷失方向、拒绝帮助",
        "keywords": ["独处", "内省", "智慧", "指导", "寻找"],
        "description": "隐者代表独处和内省，通过内在的智慧寻找真理和指导他人。",
    },
    {
        "name": "命运之轮",
        "name_en": "Wheel of Fortune",
        "card_type": "major",
        "suit": "major",
        "number": 10,
        "upright_meaning": "变化、命运、转折点、机会、循环、运气",
        "reversed_meaning": "坏运气、停滞、抗拒变化、命运逆转",
        "keywords": ["变化", "命运", "转折点", "机会", "循环"],
        "description": "命运之轮代表变化和命运的转折点，提醒我们生命是不断变化的循环。",
    },
    {
        "name": "正义",
        "name_en": "Justice",
        "card_type": "major",
        "suit": "major",
        "number": 11,
        "upright_meaning": "正义、平衡、真理、诚实、公平、因果",
        "reversed_meaning": "不公正、偏见、不平衡、逃避责任",
        "keywords": ["正义", "平衡", "真理", "诚实", "公平"],
        "description": "正义牌代表公平和平衡，提醒我们要诚实面对真相，承担相应的责任。",
    },
    {
        "name": "倒吊人",
        "name_en": "The Hanged Man",
        "card_type": "major",
        "suit": "major",
        "number": 12,
        "upright_meaning": "牺牲、暂停、新视角、放下、等待、启示",
        "reversed_meaning": "无意义的牺牲、停滞、缺乏进展、浪费时间",
        "keywords": ["牺牲", "暂停", "新视角", "放下", "等待"],
        "description": "倒吊人代表牺牲和暂停，通过不同的视角看待问题，获得新的启示。",
    },
    {
        "name": "死神",
        "name_en": "Death",
        "card_type": "major",
        "suit": "major",
        "number": 13,
        "upright_meaning": "结束、转变、重生、释放、改变、新生",
        "reversed_meaning": "抗拒改变、停滞、无法放下、恐惧",
        "keywords": ["结束", "转变", "重生", "释放", "改变"],
        "description": "死神代表结束和转变，虽然看似可怕，但实际上是新生的开始。",
    },
    {
        "name": "节制",
        "name_en": "Temperance",
        "card_type": "major",
        "suit": "major",
        "number": 14,
        "upright_meaning": "平衡、适度、和谐、耐心、融合、治愈",
        "reversed_meaning": "不平衡、过度、缺乏耐心、冲突",
        "keywords": ["平衡", "适度", "和谐", "耐心", "融合"],
        "description": "节制代表平衡和和谐，通过适度和耐心来达到内在的平衡。",
    },
    {
        "name": "恶魔",
        "name_en": "The Devil",
        "card_type": "major",
        "suit": "major",
        "number": 15,
        "upright_meaning": "束缚、欲望、物质主义、阴影、诱惑、执着",
        "reversed_meaning": "释放、摆脱束缚、面对阴影、觉醒",
        "keywords": ["束缚", "欲望", "物质主义", "阴影", "诱惑"],
        "description": "恶魔代表束缚和欲望，提醒我们要面对内心的阴影和执着。",
    },
    {
        "name": "高塔",
        "name_en": "The Tower",
        "card_type": "major",
        "suit": "major",
        "number": 16,
        "upright_meaning": "突然变化、破坏、启示、混乱、解放、觉醒",
        "reversed_meaning": "避免灾难、渐进变化、恐惧变化",
        "keywords": ["突然变化", "破坏", "启示", "混乱", "解放"],
        "description": "高塔代表突然的变化和破坏，虽然痛苦，但能带来启示和解放。",
    },
    {
        "name": "星星",
        "name_en": "The Star",
        "card_type": "major",
        "suit": "major",
        "number": 17,
        "upright_meaning": "希望、灵感、信心、治愈、指引、乐观",
        "reversed_meaning": "失去希望、悲观、缺乏信心、迷失方向",
        "keywords": ["希望", "灵感", "信心", "治愈", "指引"],
        "description": "星星代表希望和灵感，在黑暗中为我们指引方向，带来治愈和信心。",
    },
    {
        "name": "月亮",
        "name_en": "The Moon",
        "card_type": "major",
        "suit": "major",
        "number": 18,
        "upright_meaning": "直觉、幻想、恐惧、潜意识、迷惑、神秘",
        "reversed_meaning": "面对恐惧、清晰、真相显现、摆脱迷惑",
        "keywords": ["直觉", "幻想", "恐惧", "潜意识", "迷惑"],
        "description": "月亮代表直觉和潜意识，但也可能带来恐惧和迷惑，需要面对内心的阴影。",
    },
    {
        "name": "太阳",
        "name_en": "The Sun",
        "card_type": "major",
        "suit": "major",
        "number": 19,
        "upright_meaning": "快乐、成功、活力、真理、乐观、温暖",
        "reversed_meaning": "暂时的困难、过度乐观、缺乏深度",
        "keywords": ["快乐", "成功", "活力", "真理", "乐观"],
        "description": "太阳代表快乐和成功，带来温暖和活力，象征着真理和乐观的态度。",
    },
    {
        "name": "审判",
        "name_en": "Judgement",
        "card_type": "major",
        "suit": "major",
        "number": 20,
        "upright_meaning": "重生、觉醒、救赎、召唤、转变、内在声音",
        "reversed_meaning": "拒绝召唤、自我怀疑、错过机会",
        "keywords": ["重生", "觉醒", "救赎", "召唤", "转变"],
        "description": "审判代表重生和觉醒，听到内在的召唤，获得救赎和转变。",
    },
    {
        "name": "世界",
        "name_en": "The World",
        "card_type": "major",
        "suit": "major",
        "number": 21,
        "upright_meaning": "完成、成就、圆满、旅行、和谐、成功",
        "reversed_meaning": "未完成、缺乏圆满、停滞、延迟",
        "keywords": ["完成", "成就", "圆满", "旅行", "和谐"],
        "description": "世界代表完成和成就，象征着圆满和成功，也代表旅行和和谐。",
    },
]

# 牌阵数据
TAROT_SPREADS_DATA = [
    {
        "name": "单张牌阵",
        "spread_type": "classic",
        "description": "简单直接的问题解答，适合快速占卜和日常指导",
        "card_count": 1,
        "positions": ["主要信息"],
        "image_url": "/static/img/tarot/spreads/single.jpg",
    },
    {
        "name": "三张牌阵",
        "spread_type": "classic",
        "description": "过去、现在、未来的时间线，了解事情的发展脉络",
        "card_count": 3,
        "positions": ["过去", "现在", "未来"],
        "image_url": "/static/img/tarot/spreads/three_card.jpg",
    },
    {
        "name": "凯尔特十字",
        "spread_type": "classic",
        "description": "深度分析复杂情况，提供全面的解读和指导",
        "card_count": 10,
        "positions": ["现状", "挑战", "过去", "未来", "目标", "近期", "自我", "环境", "希望", "结果"],
        "image_url": "/static/img/tarot/spreads/celtic_cross.jpg",
    },
    {
        "name": "爱情十字",
        "spread_type": "situation",
        "description": "专门用于爱情关系的深度分析",
        "card_count": 5,
        "positions": ["你的感受", "对方的感受", "关系现状", "潜在问题", "未来发展"],
        "image_url": "/static/img/tarot/spreads/love_cross.jpg",
    },
    {
        "name": "事业阶梯",
        "spread_type": "situation",
        "description": "分析事业发展路径和机会",
        "card_count": 6,
        "positions": ["当前状况", "优势", "挑战", "机会", "建议", "结果"],
        "image_url": "/static/img/tarot/spreads/career_ladder.jpg",
    },
    {
        "name": "心灵花园",
        "spread_type": "spiritual",
        "description": "探索内心世界和灵性成长",
        "card_count": 7,
        "positions": ["内在状态", "隐藏的恐惧", "内在力量", "成长方向", "阻碍", "指导", "内在智慧"],
        "image_url": "/static/img/tarot/spreads/spiritual_garden.jpg",
    },
]


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def initialize_tarot_data_api(request):
    """初始化塔罗牌数据API"""
    try:
        # 检查是否已经初始化
        if TarotCard.objects.exists():
            return JsonResponse({"success": True, "message": "塔罗牌数据已存在", "cards_count": TarotCard.objects.count()})

        # 创建塔罗牌数据
        cards_created = 0
        for card_data in TAROT_CARDS_DATA:
            TarotCard.objects.create(
                name=card_data["name"],
                name_en=card_data["name_en"],
                card_type=card_data["card_type"],
                suit=card_data["suit"],
                number=card_data["number"],
                upright_meaning=card_data["upright_meaning"],
                reversed_meaning=card_data["reversed_meaning"],
                keywords=card_data["keywords"],
                description=card_data["description"],
            )
            cards_created += 1

        # 创建牌阵数据
        spreads_created = 0
        for spread_data in TAROT_SPREADS_DATA:
            TarotSpread.objects.create(
                name=spread_data["name"],
                spread_type=spread_data["spread_type"],
                description=spread_data["description"],
                card_count=spread_data["card_count"],
                positions=spread_data["positions"],
                image_url=spread_data["image_url"],
            )
            spreads_created += 1

        logger.info(f"初始化塔罗牌数据成功: {cards_created}张牌, {spreads_created}个牌阵")

        return JsonResponse(
            {
                "success": True,
                "message": f"塔罗牌数据初始化成功: {cards_created}张牌, {spreads_created}个牌阵",
                "cards_count": cards_created,
                "spreads_count": spreads_created,
            }
        )

    except Exception as e:
        logger.error(f"初始化塔罗牌数据失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"初始化失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
# @login_required  # 暂时注释掉登录要求，用于测试
def tarot_spreads_api(request):
    """获取塔罗牌阵型API"""
    try:
        spreads = TarotSpread.objects.filter(is_active=True)
        spreads_data = []

        for spread in spreads:
            spreads_data.append(
                {
                    "id": spread.id,
                    "name": spread.name,
                    "spread_type": spread.spread_type,
                    "description": spread.description,
                    "card_count": spread.card_count,
                    "positions": spread.positions,
                    "image_url": spread.image_url,
                }
            )

        logger.info(f"获取塔罗牌阵型: 用户 {request.user.id}, 共{len(spreads_data)}个牌阵")

        return JsonResponse({"success": True, "spreads": spreads_data})

    except Exception as e:
        logger.error(f"获取塔罗牌阵型失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取阵型失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def tarot_create_reading_api(request):
    """创建塔罗牌解读API"""
    try:
        data = json.loads(request.body)
        spread_id = data.get("spread_id")
        reading_type = data.get("reading_type", "custom")
        question = data.get("question", "")
        mood_before = data.get("mood_before", "")

        if not spread_id:
            return JsonResponse({"success": False, "error": "请选择牌阵"}, status=400)

        if not question:
            return JsonResponse({"success": False, "error": "请输入问题"}, status=400)

        # 获取牌阵
        try:
            spread = TarotSpread.objects.get(id=spread_id)
        except TarotSpread.DoesNotExist:
            return JsonResponse({"success": False, "error": "牌阵不存在"}, status=404)

        # 获取所有塔罗牌
        all_cards = list(TarotCard.objects.all())
        if not all_cards:
            return JsonResponse({"success": False, "error": "塔罗牌数据未初始化"}, status=500)

        # 随机抽取牌
        drawn_cards = []
        selected_cards = random.sample(all_cards, min(spread.card_count, len(all_cards)))

        for i, card in enumerate(selected_cards):
            is_reversed = random.choice([True, False])
            position = spread.positions[i] if i < len(spread.positions) else f"位置{i+1}"

            drawn_cards.append(
                {
                    "card": {
                        "id": card.id,
                        "name": card.name,
                        "name_en": card.name_en,
                        "card_type": card.card_type,
                        "suit": card.suit,
                        "number": card.number,
                        "image_url": card.image_url,
                    },
                    "position": position,
                    "is_reversed": is_reversed,
                    "meaning": card.reversed_meaning if is_reversed else card.upright_meaning,
                    "keywords": card.keywords,
                }
            )

        # 生成AI解读
        ai_interpretation = generate_ai_interpretation(spread, drawn_cards, question, reading_type)

        # 保存占卜记录
        with transaction.atomic():
            reading = TarotReading.objects.create(
                user=request.user,
                spread=spread,
                reading_type=reading_type,
                question=question,
                drawn_cards=drawn_cards,
                card_positions=spread.positions,
                ai_interpretation=ai_interpretation,
                mood_before=mood_before,
            )

        # 构建返回数据
        reading_data = {
            "id": reading.id,
            "spread_name": spread.name,
            "reading_type": reading.get_reading_type_display(),
            "question": question,
            "drawn_cards": drawn_cards,
            "ai_interpretation": ai_interpretation,
            "created_at": reading.created_at.isoformat(),
            "drawn_cards_count": len(drawn_cards),
        }

        logger.info(f"创建塔罗牌解读成功: 用户 {request.user.id}, 牌阵 {spread.name}")

        return JsonResponse({"success": True, "message": "塔罗牌解读创建成功", "reading": reading_data})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"}, status=400)
    except Exception as e:
        logger.error(f"创建塔罗牌解读失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"创建解读失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def tarot_readings_api(request):
    """获取塔罗牌解读历史API"""
    try:
        readings = TarotReading.objects.filter(user=request.user).order_by("-created_at")[:20]
        readings_data = []

        for reading in readings:
            readings_data.append(
                {
                    "id": reading.id,
                    "spread_name": reading.spread.name,
                    "reading_type": reading.get_reading_type_display(),
                    "question": reading.question,
                    "created_at": reading.created_at.strftime("%Y-%m-%d %H:%M"),
                    "drawn_cards_count": len(reading.drawn_cards) if reading.drawn_cards else 0,
                }
            )

        logger.info(f"获取塔罗牌解读历史: 用户 {request.user.id}, 共{len(readings_data)}条记录")

        return JsonResponse({"success": True, "readings": readings_data})

    except Exception as e:
        logger.error(f"获取塔罗牌解读历史失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取历史失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def tarot_reading_detail_api(request, reading_id):
    """获取塔罗牌解读详情API"""
    try:
        reading = TarotReading.objects.get(id=reading_id, user=request.user)

        reading_data = {
            "id": reading.id,
            "spread_name": reading.spread.name,
            "reading_type": reading.get_reading_type_display(),
            "question": reading.question,
            "drawn_cards": reading.drawn_cards,
            "ai_interpretation": reading.ai_interpretation,
            "mood_before": reading.mood_before,
            "mood_after": reading.mood_after,
            "user_feedback": reading.user_feedback,
            "accuracy_rating": reading.accuracy_rating,
            "created_at": reading.created_at.isoformat(),
            "drawn_cards_count": len(reading.drawn_cards) if reading.drawn_cards else 0,
        }

        return JsonResponse({"success": True, "reading": reading_data})

    except TarotReading.DoesNotExist:
        return JsonResponse({"success": False, "error": "占卜记录不存在"}, status=404)
    except Exception as e:
        logger.error(f"获取塔罗牌解读详情失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取详情失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def tarot_feedback_api(request, reading_id):
    """提交塔罗牌解读反馈API"""
    try:
        data = json.loads(request.body)
        feedback = data.get("feedback", "")
        rating = data.get("rating")
        mood_after = data.get("mood_after", "")

        reading = TarotReading.objects.get(id=reading_id, user=request.user)
        reading.user_feedback = feedback
        reading.accuracy_rating = rating
        reading.mood_after = mood_after
        reading.save()

        return JsonResponse({"success": True, "message": "反馈提交成功"})

    except TarotReading.DoesNotExist:
        return JsonResponse({"success": False, "error": "占卜记录不存在"}, status=404)
    except Exception as e:
        logger.error(f"提交塔罗牌解读反馈失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"提交反馈失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
# @login_required  # 暂时注释掉登录要求，用于测试
def tarot_daily_energy_api(request):
    """获取每日塔罗牌能量API"""
    try:
        today = datetime.now().date()

        # 检查缓存
        cache_key = f"tarot_daily_energy_{today}"
        daily_energy = cache.get(cache_key)

        if not daily_energy:
            # 获取今日能量日历
            try:
                energy_calendar = TarotEnergyCalendar.objects.get(date=today)
                daily_energy = {
                    "date": today.isoformat(),
                    "energy_type": energy_calendar.get_energy_type_display(),
                    "energy_level": energy_calendar.energy_level,
                    "description": energy_calendar.description,
                    "recommended_cards": energy_calendar.recommended_cards,
                    "special_reading": energy_calendar.special_reading,
                }
            except TarotEnergyCalendar.DoesNotExist:
                # 生成默认每日能量
                all_cards = list(TarotCard.objects.all())
                daily_card = random.choice(all_cards) if all_cards else None

                daily_energy = {
                    "date": today.isoformat(),
                    "energy_type": "日常能量",
                    "energy_level": random.randint(6, 10),
                    "description": f"今天是充满活力的一天，适合尝试新事物，保持开放的心态。",
                    "recommended_cards": [daily_card.name] if daily_card else [],
                    "special_reading": "今天是一个适合突破自我的日子，勇敢地面对挑战吧！",
                    "lucky_color": random.choice(["红色", "蓝色", "绿色", "黄色", "紫色"]),
                    "lucky_number": random.randint(1, 99),
                }

            # 缓存24小时
            cache.set(cache_key, daily_energy, 86400)

        logger.info(f"获取每日塔罗牌能量: 用户 {request.user.id}")

        return JsonResponse({"success": True, "daily_energy": daily_energy})

    except Exception as e:
        logger.error(f"获取每日塔罗牌能量失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取能量失败: {str(e)}"}, status=500)


def generate_ai_interpretation(spread, drawn_cards, question, reading_type):
    """生成AI解读"""
    try:
        # 构建提示词
        prompt = f"""
作为一位经验丰富的塔罗牌解读师，请为以下占卜提供专业的解读：

占卜类型：{reading_type}
问题：{question}
牌阵：{spread.name}（{spread.card_count}张牌）

抽到的牌：
"""

        for card_data in drawn_cards:
            card = card_data["card"]
            position = card_data["position"]
            is_reversed = card_data["is_reversed"]
            meaning = card_data["meaning"]

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

        # 调用AI API（这里使用DeepSeek作为示例）
        api_key = getattr(settings, "DEEPSEEK_API_KEY", None)
        if api_key:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.7,
            }

            response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]

        # 如果AI API不可用，返回默认解读
        return generate_default_interpretation(spread, drawn_cards, question, reading_type)

    except Exception as e:
        logger.error(f"生成AI解读失败: {str(e)}")
        return generate_default_interpretation(spread, drawn_cards, question, reading_type)


def generate_default_interpretation(spread, drawn_cards, question, reading_type):
    """生成默认解读"""
    interpretation = f"基于{spread.name}的占卜结果，为您解读如下：\n\n"

    # 整体解读
    interpretation += "【整体解读】\n"
    interpretation += f"您的问题是关于{reading_type}的，通过{spread.name}的指引，我们可以看到一些重要的信息。\n\n"

    # 各位置解读
    interpretation += "【各位置解读】\n"
    for card_data in drawn_cards:
        card = card_data["card"]
        position = card_data["position"]
        is_reversed = card_data["is_reversed"]
        meaning = card_data["meaning"]

        interpretation += f"{position}：{card['name']}（{'逆位' if is_reversed else '正位'}）\n"
        interpretation += f"{meaning}\n\n"

    # 建议指导
    interpretation += "【建议指导】\n"
    interpretation += "请保持开放的心态，相信自己的直觉。塔罗牌是指导而非决定，最终的选择权在您手中。\n\n"

    # 注意事项
    interpretation += "【注意事项】\n"
    interpretation += "塔罗牌解读仅供参考，请理性对待。重要的决定需要结合实际情况综合考虑。"

    return interpretation
