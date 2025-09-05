"""
社交娱乐模块视图
"""
import random
import uuid
from datetime import datetime, timedelta
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from api.response import APIResponse, APIErrorCodes
from api.permissions import IsAuthenticated, FeaturePermission
from .serializers import (
    ChatRoomSerializer, ChatMessageSerializer,
    HeartLinkRequestSerializer, BuddyEventSerializer,
    BuddyEventMemberSerializer, TarotReadingSerializer,
    StoryGeneratorSerializer, TravelGuideSerializer,
    FortuneAnalyzerSerializer
)
from apps.tools.models import (
    ChatRoom, ChatMessage, HeartLinkRequest, BuddyEvent,
    BuddyEventMember, BuddyEventMessage, TarotReading
)


class ChatRoomViewSet(viewsets.ModelViewSet):
    """聊天室管理"""
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated, FeaturePermission('chat_room')]
    
    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            Q(members__user=user) | Q(creator=user)
        ).distinct().order_by('-updated_at')
    
    def list(self, request, *args, **kwargs):
        """获取聊天室列表"""
        queryset = self.get_queryset()
        
        # 过滤条件
        room_type = request.query_params.get('room_type')
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        
        is_private = request.query_params.get('is_private')
        if is_private is not None:
            queryset = queryset.filter(is_private=is_private.lower() == 'true')
        
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建聊天室"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            
            # 自动加入创建者
            room.members.create(user=request.user)
            
            return APIResponse.success(
                data=serializer.data,
                message="聊天室创建成功"
            )
        return APIResponse.error(
            message="创建失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """加入聊天室"""
        room = self.get_object()
        
        if room.members.filter(user=request.user).exists():
            return APIResponse.error(
                message="您已经在这个聊天室中了",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        if room.members.count() >= room.max_members:
            return APIResponse.error(
                message="聊天室已满",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        room.members.create(user=request.user)
        
        return APIResponse.success(message="成功加入聊天室")
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """离开聊天室"""
        room = self.get_object()
        
        if room.creator == request.user:
            return APIResponse.error(
                message="创建者不能离开聊天室",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        room.members.filter(user=request.user).delete()
        
        return APIResponse.success(message="已离开聊天室")
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """获取聊天室消息"""
        room = self.get_object()
        
        # 检查用户是否在聊天室中
        if not room.members.filter(user=request.user).exists() and room.creator != request.user:
            return APIResponse.error(
                message="您不在这个聊天室中",
                code=APIErrorCodes.FORBIDDEN
            )
        
        messages = room.messages.all().order_by('-created_at')[:50]
        serializer = ChatMessageSerializer(messages, many=True)
        
        return APIResponse.success(data=serializer.data)


class ChatMessageViewSet(viewsets.ModelViewSet):
    """聊天消息管理"""
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated, FeaturePermission('chat_room')]
    
    def get_queryset(self):
        return ChatMessage.objects.filter(
            room__members__user=self.request.user
        ).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """发送消息"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save()
            
            # 这里可以集成实时消息推送
            # 例如使用WebSocket或推送服务
            
            return APIResponse.success(
                data=serializer.data,
                message="消息发送成功"
            )
        return APIResponse.error(
            message="发送失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )


class HeartLinkViewSet(viewsets.ModelViewSet):
    """心链功能"""
    serializer_class = HeartLinkRequestSerializer
    permission_classes = [IsAuthenticated, FeaturePermission('heart_link')]
    
    def get_queryset(self):
        user = self.request.user
        return HeartLinkRequest.objects.filter(
            Q(requester=user) | Q(target=user)
        ).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """创建心链请求"""
        target_id = request.data.get('target')
        
        if not target_id:
            return APIResponse.error(
                message="请选择心链对象",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        # 检查是否已经存在心链请求
        existing_request = HeartLinkRequest.objects.filter(
            requester=request.user,
            target_id=target_id,
            status='pending'
        ).exists()
        
        if existing_request:
            return APIResponse.error(
                message="您已经向该用户发送过心链请求",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="心链请求已发送"
            )
        return APIResponse.error(
            message="发送失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """接受心链请求"""
        heart_link = self.get_object()
        
        if heart_link.target != request.user:
            return APIResponse.error(
                message="您不能接受此心链请求",
                code=APIErrorCodes.FORBIDDEN
            )
        
        heart_link.status = 'accepted'
        heart_link.responded_at = datetime.now()
        heart_link.save()
        
        return APIResponse.success(message="心链请求已接受")
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝心链请求"""
        heart_link = self.get_object()
        
        if heart_link.target != request.user:
            return APIResponse.error(
                message="您不能拒绝此心链请求",
                code=APIErrorCodes.FORBIDDEN
            )
        
        heart_link.status = 'rejected'
        heart_link.responded_at = datetime.now()
        heart_link.save()
        
        return APIResponse.success(message="心链请求已拒绝")


class BuddyEventViewSet(viewsets.ModelViewSet):
    """搭子活动管理"""
    serializer_class = BuddyEventSerializer
    permission_classes = [IsAuthenticated, FeaturePermission('buddy_event')]
    
    def get_queryset(self):
        return BuddyEvent.objects.filter(
            start_time__gte=datetime.now()
        ).order_by('start_time')
    
    def list(self, request, *args, **kwargs):
        """获取搭子活动列表"""
        queryset = self.get_queryset()
        
        # 过滤条件
        event_type = request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        location = request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(start_time__date__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(start_time__date__lte=date_to)
        
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """加入搭子活动"""
        event = self.get_object()
        
        if event.members.filter(user=request.user).exists():
            return APIResponse.error(
                message="您已经加入了这个活动",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        if event.members.count() >= event.max_participants:
            return APIResponse.error(
                message="活动人数已满",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        if event.start_time <= datetime.now():
            return APIResponse.error(
                message="活动已经开始，无法加入",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        event.members.create(user=request.user)
        
        return APIResponse.success(message="成功加入活动")
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """离开搭子活动"""
        event = self.get_object()
        
        if event.creator == request.user:
            return APIResponse.error(
                message="活动创建者不能离开活动",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        event.members.filter(user=request.user).delete()
        
        return APIResponse.success(message="已离开活动")


class TarotReadingViewSet(viewsets.ModelViewSet):
    """塔罗占卜"""
    serializer_class = TarotReadingSerializer
    permission_classes = [IsAuthenticated, FeaturePermission('tarot_reading')]
    
    def get_queryset(self):
        return TarotReading.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def draw_cards(self, request):
        """抽牌占卜"""
        question = request.data.get('question', '')
        spread_type = request.data.get('spread_type', 'single')
        
        if not question:
            return APIResponse.error(
                message="请输入您的问题",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        # 塔罗牌数据
        tarot_cards = [
            {'name': '愚者', 'meaning': '新的开始，冒险精神', 'upright': '自由，冒险，新开始', 'reversed': '鲁莽，缺乏计划'},
            {'name': '魔术师', 'meaning': '意志力，创造力', 'upright': '技能，意志力，创造力', 'reversed': '欺骗，操纵'},
            {'name': '女祭司', 'meaning': '直觉，潜意识', 'upright': '直觉，潜意识，神秘', 'reversed': '缺乏洞察力，秘密'},
            {'name': '皇后', 'meaning': '母性，丰饶', 'upright': '母性，丰饶，感性', 'reversed': '依赖，缺乏成长'},
            {'name': '皇帝', 'meaning': '权威，秩序', 'upright': '权威，秩序，控制', 'reversed': '专制，缺乏灵活性'},
            {'name': '教皇', 'meaning': '传统，精神指导', 'upright': '传统，精神指导，学习', 'reversed': '教条，缺乏独立思考'},
            {'name': '恋人', 'meaning': '爱情，选择', 'upright': '爱情，和谐，选择', 'reversed': '不和谐，错误选择'},
            {'name': '战车', 'meaning': '意志力，胜利', 'upright': '意志力，胜利，控制', 'reversed': '缺乏控制，失败'},
            {'name': '力量', 'meaning': '内在力量，勇气', 'upright': '内在力量，勇气，耐心', 'reversed': '软弱，缺乏自信'},
            {'name': '隐者', 'meaning': '内省，寻求真理', 'upright': '内省，寻求真理，指导', 'reversed': '孤独，缺乏指导'},
        ]
        
        # 根据牌阵类型抽牌
        if spread_type == 'single':
            cards_drawn = [random.choice(tarot_cards)]
        elif spread_type == 'three':
            cards_drawn = random.sample(tarot_cards, 3)
        else:  # celtic_cross
            cards_drawn = random.sample(tarot_cards, 10)
        
        # 生成解读
        interpretation = self.generate_interpretation(question, cards_drawn, spread_type)
        
        # 保存占卜记录
        reading = TarotReading.objects.create(
            user=request.user,
            question=question,
            spread_type=spread_type,
            cards_drawn=cards_drawn,
            interpretation=interpretation
        )
        
        return APIResponse.success(
            data={
                'reading_id': reading.id,
                'question': question,
                'spread_type': spread_type,
                'cards_drawn': cards_drawn,
                'interpretation': interpretation
            },
            message="占卜完成"
        )
    
    def generate_interpretation(self, question, cards, spread_type):
        """生成占卜解读"""
        if spread_type == 'single':
            card = cards[0]
            return f"关于您的问题「{question}」，抽到的牌是「{card['name']}」。{card['meaning']}。{card['upright']}。"
        elif spread_type == 'three':
            return f"关于您的问题「{question}」，三张牌分别代表过去、现在、未来。过去：{cards[0]['name']} - {cards[0]['meaning']}；现在：{cards[1]['name']} - {cards[1]['meaning']}；未来：{cards[2]['name']} - {cards[2]['meaning']}。"
        else:  # celtic_cross
            return f"关于您的问题「{question}」，凯尔特十字牌阵为您揭示了全面的指引。每张牌都有其特殊的意义，建议您仔细思考每张牌的含义。"
    
    def list(self, request, *args, **kwargs):
        """获取占卜历史"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)


class StoryGeneratorViewSet(viewsets.ViewSet):
    """故事生成器"""
    permission_classes = [IsAuthenticated, FeaturePermission('story_generator')]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """生成故事"""
        serializer = StoryGeneratorSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="参数验证失败",
                errors=serializer.errors,
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        data = serializer.validated_data
        story = self.generate_story(data)
        
        return APIResponse.success(
            data={
                'story': story,
                'story_type': data['story_type'],
                'theme': data['theme'],
                'length': data['length']
            },
            message="故事生成成功"
        )
    
    def generate_story(self, data):
        """生成故事内容"""
        story_type = data['story_type']
        theme = data['theme']
        characters = data.get('characters', ['主角'])
        setting = data.get('setting', '现代都市')
        length = data['length']
        style = data['style']
        
        # 故事模板
        story_templates = {
            'romance': f"在{setting}，{characters[0]}遇到了命中注定的那个人。",
            'adventure': f"{characters[0]}踏上了一段充满挑战的冒险之旅。",
            'mystery': f"一个神秘的{theme}事件改变了{characters[0]}的生活。",
            'fantasy': f"在魔法世界中，{characters[0]}发现了自己隐藏的力量。",
            'scifi': f"未来世界中，{characters[0]}面临着前所未有的科技挑战。",
            'horror': f"恐怖的{theme}事件让{characters[0]}陷入了噩梦。",
            'comedy': f"一个搞笑的{theme}事件让{characters[0]}的生活变得混乱而有趣。",
        }
        
        base_story = story_templates.get(story_type, f"关于{theme}的故事开始了。")
        
        # 根据长度扩展故事
        if length == 'short':
            return f"{base_story} 这是一个简短而精彩的故事。"
        elif length == 'medium':
            return f"{base_story} 故事逐渐展开，{characters[0]}面临着各种挑战和机遇。经过一系列的事件，最终找到了属于自己的答案。"
        else:  # long
            return f"{base_story} 这是一个长篇故事，{characters[0]}将经历许多波折和成长。故事中有多个角色，包括{', '.join(characters[1:])}。在{setting}这个背景下，他们将共同面对{theme}带来的挑战，最终实现自己的目标。"
        
        return base_story


class TravelGuideViewSet(viewsets.ViewSet):
    """旅游攻略生成器"""
    permission_classes = [IsAuthenticated, FeaturePermission('travel_guide')]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """生成旅游攻略"""
        serializer = TravelGuideSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="参数验证失败",
                errors=serializer.errors,
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        data = serializer.validated_data
        guide = self.generate_travel_guide(data)
        
        return APIResponse.success(
            data={
                'guide': guide,
                'destination': data['destination'],
                'travel_type': data['travel_type'],
                'duration': data['duration']
            },
            message="旅游攻略生成成功"
        )
    
    def generate_travel_guide(self, data):
        """生成旅游攻略内容"""
        destination = data['destination']
        travel_type = data['travel_type']
        duration = data['duration']
        budget = data['budget']
        interests = data.get('interests', [])
        season = data.get('season', '春季')
        
        guide = f"""
# {destination} {duration}天旅游攻略

## 基本信息
- 目的地：{destination}
- 旅行类型：{travel_type}
- 行程天数：{duration}天
- 预算等级：{budget}
- 最佳季节：{season}

## 行程安排
"""
        
        # 根据天数生成行程
        for day in range(1, duration + 1):
            guide += f"\n### 第{day}天\n"
            if day == 1:
                guide += f"- 抵达{destination}\n- 入住酒店\n- 市区观光\n- 品尝当地美食\n"
            elif day == duration:
                guide += f"- 最后一天购物\n- 准备返程\n- 机场送机\n"
            else:
                guide += f"- 深度游览{destination}著名景点\n- 体验当地文化\n- 品尝特色美食\n"
        
        # 根据兴趣添加推荐
        if interests:
            guide += f"\n## 特别推荐\n"
            for interest in interests:
                if interest == 'culture':
                    guide += f"- 文化景点：博物馆、历史建筑\n"
                elif interest == 'nature':
                    guide += f"- 自然风光：公园、山景、海景\n"
                elif interest == 'food':
                    guide += f"- 美食体验：当地特色餐厅、小吃街\n"
                elif interest == 'shopping':
                    guide += f"- 购物推荐：商业街、特色商店\n"
                elif interest == 'adventure':
                    guide += f"- 冒险活动：户外运动、极限体验\n"
                elif interest == 'relaxation':
                    guide += f"- 休闲放松：温泉、SPA、海滩\n"
        
        guide += f"""
## 实用信息
- 交通：建议使用公共交通或租车
- 住宿：根据预算选择合适的酒店
- 美食：尝试当地特色菜
- 购物：购买纪念品和特产
- 注意事项：遵守当地法律法规，注意安全

祝您旅途愉快！
"""
        
        return guide


class FortuneAnalyzerViewSet(viewsets.ViewSet):
    """命运分析器"""
    permission_classes = [IsAuthenticated, FeaturePermission('fortune_analyzer')]
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """命运分析"""
        serializer = FortuneAnalyzerSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="参数验证失败",
                errors=serializer.errors,
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        data = serializer.validated_data
        analysis = self.perform_fortune_analysis(data)
        
        return APIResponse.success(
            data={
                'analysis': analysis,
                'name': data['name'],
                'analysis_type': data['analysis_type']
            },
            message="命运分析完成"
        )
    
    def perform_fortune_analysis(self, data):
        """执行命运分析"""
        name = data['name']
        analysis_type = data['analysis_type']
        birth_date = data['birth_date']
        
        # 简单的命运分析（模拟）
        analysis_results = {
            'personality': f"根据您的出生日期，{name}具有独特的个性特征。您是一个富有创造力的人，善于思考，具有强烈的直觉能力。",
            'career': f"在事业方面，{name}适合从事需要创新思维的工作。建议关注科技、艺术或教育领域。",
            'love': f"在爱情方面，{name}是一个真诚而深情的人。您会找到与您心灵相通的伴侣。",
            'health': f"在健康方面，{name}需要注意保持良好的作息习惯。建议多进行户外运动。",
            'wealth': f"在财运方面，{name}具有很好的理财能力。通过努力工作和合理投资，您会获得不错的财富积累。",
            'comprehensive': f"综合分析，{name}是一个具有多方面才能的人。在人生的各个阶段，您都会遇到机遇和挑战，但凭借您的智慧和努力，一定能够取得成功。"
        }
        
        return analysis_results.get(analysis_type, "命运分析结果将为您的人生提供指引。")
