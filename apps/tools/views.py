from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import requests
import random
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import models
import uuid
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.cache import cache
import time

# 管理员权限检查函数
def is_admin(user):
    """检查用户是否为管理员"""
    try:
        return user.role.role == 'admin'
    except:
        return False

# 管理员权限装饰器
def admin_required(view_func):
    """管理员权限装饰器"""
    decorated_view = user_passes_test(is_admin, login_url='/users/login/')(view_func)
    return decorated_view

from .models import LifeDiaryEntry, LifeStatistics, LifeGoal, LifeGoalProgress
from .models import ChatRoom, HeartLinkRequest, UserOnlineStatus, ChatMessage

def validate_budget_range(budget_min, budget_max):
    """验证预算范围的合法性"""
    try:
        budget_min = int(budget_min) if budget_min else 0
        budget_max = int(budget_max) if budget_max else 0
    except (ValueError, TypeError):
        return "预算必须为有效数字"
    
    if budget_min <= 0 or budget_max <= 0:
        return "预算必须大于0"
    
    if budget_min >= budget_max:
        return "最低预算必须小于最高预算"
    
    if budget_min < 500:
        return "最低预算不能低于500元"
    
    if budget_max > 100000:
        return "最高预算不能超过100000元"
    
    if budget_max - budget_min < 500:
        return "预算范围差距至少需要500元"
    
    return None  # 验证通过

# 三重觉醒改造计划API
from .services.triple_awakening import TripleAwakeningService, WorkoutAudioProcessor
from .models import (
    FitnessWorkoutSession, CodeWorkoutSession, ExhaustionProof,
    AIDependencyMeter, CoPilotCollaboration, DailyWorkoutChallenge,
    PainCurrency, WorkoutDashboard
)

# 欲望仪表盘API
from .services.desire_dashboard import DesireDashboardService, DesireVisualizationService
from .models import DesireDashboard, DesireItem, DesireFulfillment

# VanityOS 模型导入
from .models import (
    VanityWealth, SinPoints, Sponsor, VanityTask, BasedDevAvatar
)

# 旅游攻略相关模型导入
from .models import TravelGuide

# 自动求职机相关模型导入 - 已隐藏
# from .models import JobSearchRequest, JobApplication, JobSearchProfile, JobSearchStatistics
# from .services.job_search_service import JobSearchService

# 塔罗牌相关导入
from .services.tarot_service import TarotService, TarotVisualizationService
from .models import (
    TarotCard, TarotSpread, TarotReading, TarotDiary, 
    TarotEnergyCalendar, TarotCommunity, TarotCommunityComment
)

# 食物随机选择器相关导入
from .models import (
    FoodRandomizer, FoodItem, FoodRandomizationSession, FoodHistory
)

# 用户资料相关导入
from django.contrib.auth.models import User
from apps.users.models import Profile, UserMembership, UserTheme
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

@login_required
def test_case_generator(request):
    """测试用例生成器页面"""
    return render(request, 'tools/test_case_generator.html')

@login_required
def redbook_generator(request):
    """小红书文案生成器页面"""
    return render(request, 'tools/redbook_generator.html')

@login_required
def pdf_converter(request):
    """PDF转换器页面"""
    return render(request, 'tools/pdf_converter_modern.html')

@login_required
def fortune_analyzer(request):
    """姻缘分析器页面"""
    return render(request, 'tools/fortune_analyzer.html')

@login_required
def web_crawler(request):
    """社交媒体订阅页面"""
    return render(request, 'tools/web_crawler.html')

def social_subscription_demo(request):
    """社交媒体订阅功能演示页面"""
    return render(request, 'tools/social_subscription_demo.html')

@login_required
def self_analysis(request):
    """人生百态镜页面"""
    return render(request, 'tools/self_analysis.html')

@login_required
def storyboard(request):
    """故事板页面"""
    return render(request, 'tools/storyboard.html')

@login_required
def fitness_center(request):
    """FitMatrix健身矩阵页面"""
    return render(request, 'tools/fitness_center.html')

@login_required
def training_plan_editor(request):
    """训练计划编辑器页面"""
    return render(request, 'tools/training_plan_editor.html')

@login_required
def life_diary(request):
    """生活日记页面 - 重定向到层层递进版本"""
    return redirect('life_diary_progressive')

@login_required
def life_diary_progressive(request):
    """层层递进生活日记页面"""
    return render(request, 'tools/life_diary_progressive.html')

@csrf_exempt
@require_http_methods(["POST"])
def deepseek_api(request):
    """DeepSeek API接口"""
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 500)
        temperature = data.get('temperature', 0.8)
        
        if not prompt:
            return JsonResponse({'success': False, 'error': '提示词不能为空'}, content_type='application/json')
        
        # DeepSeek API配置
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            return JsonResponse({'success': False, 'error': 'DeepSeek API密钥未配置'}, content_type='application/json')
        
        # 调用DeepSeek API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'model': 'deepseek-chat',
            'max_tokens': max_tokens,
            'temperature': temperature
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            return JsonResponse({
                'success': True,
                'content': content
            }, content_type='application/json')
        else:
            return JsonResponse({
                'success': False,
                'error': f'DeepSeek API调用失败: {response.status_code}'
            }, content_type='application/json')
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '无效的JSON数据'}, content_type='application/json')
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def emo_diary(request):
    """Emo情感日记页面"""
    return render(request, 'tools/emo_diary.html')

@login_required
def creative_writer(request):
    """创意文案生成器页面"""
    return render(request, 'tools/creative_writer.html')

@login_required
def meditation_guide(request):
    """冥想引导师页面"""
    return render(request, 'tools/meditation_guide.html')

@login_required
def peace_meditation_view(request):
    """和平冥想页面"""
    return render(request, 'tools/peace_meditation.html')

@login_required
def music_healing(request):
    """音乐疗愈页面"""
    return render(request, 'tools/music_healing.html')

@login_required
def heart_link(request):
    """心动链接页面"""
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'tools/heart_link.html')

@login_required
def heart_link_chat(request, room_id):
    """心动链接聊天页面"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        chat_room = ChatRoom.objects.get(room_id=room_id)
        # 检查用户是否是聊天室的参与者
        participants = [chat_room.user1]
        if chat_room.user2:
            participants.append(chat_room.user2)
        
        if request.user not in participants:
            return redirect('heart_link')
    except ChatRoom.DoesNotExist:
        return redirect('heart_link')
    
    context = {
        'room_id': room_id,
        'chat_room': chat_room,
        'other_user': chat_room.user2 if request.user == chat_room.user1 else chat_room.user1
    }
    
    # 使用新的WebSocket版本的聊天页面
    return render(request, 'tools/heart_link_chat_websocket_new.html', context)

@login_required
def chat_entrance_view(request):
    """聊天入口页面"""
    return render(request, 'tools/chat_entrance.html')

def heart_link_test_view(request):
    """心动链接测试页面（无需登录）"""
    return render(request, 'tools/heart_link_test.html')

def click_test_view(request):
    """点击测试页面（无需登录）"""
    return render(request, 'tools/click_test_standalone.html')

@login_required
def number_match_view(request):
    """数字匹配页面"""
    return render(request, 'tools/number_match.html')

@login_required
def video_chat_view(request, room_id):
    """视频对话页面"""
    try:
        # 获取聊天室
        chat_room = ChatRoom.objects.get(room_id=room_id)
        
        # 检查用户是否是聊天室的参与者
        if request.user not in [chat_room.user1, chat_room.user2]:
            return JsonResponse({
                'success': False,
                'error': '您没有权限访问此聊天室'
            }, status=403)
        
        # 获取对方用户信息
        other_user = chat_room.user2 if request.user == chat_room.user1 else chat_room.user1
        other_user_profile = get_user_profile_data(other_user)
        
        context = {
            'room_id': room_id,
            'other_user': other_user_profile,
            'chat_room': chat_room
        }
        
        return render(request, 'tools/video_chat.html', context)
        
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '聊天室不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'访问视频对话失败: {str(e)}'
        }, status=500)

@login_required
def chat_enhanced(request, room_id):
    """增强聊天页面 - 展示用户头像、昵称、信息和标签"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        chat_room = ChatRoom.objects.get(room_id=room_id)
        # 检查用户是否是聊天室的参与者
        participants = [chat_room.user1]
        if chat_room.user2:
            participants.append(chat_room.user2)
        
        if request.user not in participants:
            return redirect('heart_link')
    except ChatRoom.DoesNotExist:
        return redirect('heart_link')
    
    context = {
        'room_id': room_id,
        'chat_room': chat_room,
        'other_user': chat_room.user2 if request.user == chat_room.user1 else chat_room.user1
    }
    
    # 使用增强的聊天页面
    return render(request, 'tools/chat_enhanced.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def self_analysis_api(request):
    """自我分析API"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        # DeepSeek API配置
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            return JsonResponse({'error': 'API密钥未配置'}, status=500, content_type='application/json')
        
        # 构建系统提示词
        system_prompt = """你是一位专业的心理咨询师和人生导师，专门帮助用户进行自我认知和深度分析。

你的任务是：
1. 通过提问了解用户的性格、价值观、生活经历
2. 分析用户的核心特质和潜在问题
3. 提供温暖而专业的建议和指导
4. 帮助用户更好地认识自己

对话指导原则：
- 让用户回答你的问题来了解他们
- 用户回答完后，询问是否有遗漏的部分，继续提问
- 如果用户看不懂问题，用直白的语言重新询问
- 如果用户不知道答案，鼓励他们回答"不知道"
- 适时进行总结
- 如果用户觉得总结不够完整，询问是否有遗漏
- 最后深入分析用户这个人，综合考虑，提炼核心特质
- 最后可以帮用户生成十个他们最不敢面对的问题

对话原则：
- 保持温暖、理解和支持的态度
- 用简单易懂的语言交流
- 鼓励用户深入思考和表达
- 提供建设性的建议，而不是简单的安慰
- 尊重用户的隐私和感受

请根据用户的回答，继续提问或进行分析。"""

        # 构建消息列表
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加历史对话
        for msg in conversation_history[-10:]:  # 保留最近10轮对话
            messages.append(msg)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 调用DeepSeek API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            return JsonResponse({
                'success': True,
                'response': ai_response
            }, content_type='application/json')
        else:
            return JsonResponse({
                'error': f'API调用失败: {response.status_code}'
            }, status=500, content_type='application/json')
            
    except Exception as e:
        return JsonResponse({
            'error': f'处理请求时出错: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def storyboard_api(request):
    """故事板API"""
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        
        # DeepSeek API配置
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            return JsonResponse({'error': 'API密钥未配置'}, status=500, content_type='application/json')
        
        # 构建系统提示词
        system_prompt = """你是一位富有同理心和创造力的故事作家，专门创作治愈系故事。

你的任务是：
1. 根据用户的描述创作温暖治愈的故事
2. 故事要有情感共鸣和深度
3. 语言优美，富有诗意和想象力
4. 传递积极向上的价值观
5. 结尾要有启发性和治愈感

创作要求：
- 故事长度控制在400-600字
- 情节要引人入胜
- 人物形象要生动
- 情感表达要真实
- 要有哲思和启发

请根据用户的描述，创作一个独特而治愈的故事。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请根据以下描述创作一个治愈故事：{prompt}"}
        ]
        
        # 调用DeepSeek API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': messages,
            'temperature': 0.8,
            'max_tokens': 1000
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            story = result['choices'][0]['message']['content']
            
            return JsonResponse({
                'success': True,
                'story': story
            }, content_type='application/json')
        else:
            return JsonResponse({
                'error': f'API调用失败: {response.status_code}'
            }, status=500, content_type='application/json')
            
    except Exception as e:
        return JsonResponse({
            'error': f'处理请求时出错: {str(e)}'
        }, status=500)

# 音乐API相关视图
def music_api(request):
    """免费音乐API接口"""
    if request.method == 'GET':
        mode = request.GET.get('mode', 'work')
        action = request.GET.get('action', 'random')
        
        try:
            # 导入免费音乐API
            from .utils.music_api import free_music_api
            
            if action == 'random':
                # 获取随机歌曲
                song = free_music_api.get_random_song(mode)
                if song:
                    return JsonResponse({
                        'success': True,
                        'data': song
                    }, content_type='application/json')
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '获取歌曲失败'
                    }, content_type='application/json')
            
            elif action == 'playlist':
                # 获取模式所有歌曲
                tracks = free_music_api.get_music_by_mode(mode)
                return JsonResponse({
                    'success': True,
                    'data': tracks
                }, content_type='application/json')
            
            elif action == 'search':
                # 搜索歌曲
                keyword = request.GET.get('keyword', '')
                if keyword:
                    songs = free_music_api.search_song(keyword, mode)
                    return JsonResponse({
                        'success': True,
                        'data': songs
                    }, content_type='application/json')
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '搜索关键词不能为空'
                    }, content_type='application/json')
            
            elif action == 'netease_search':
                # 网易云音乐搜索
                keyword = request.GET.get('keyword', '')
                if keyword:
                    songs = search_netease_music(keyword)
                    return JsonResponse({
                        'success': True,
                        'data': songs
                    }, content_type='application/json')
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '搜索关键词不能为空'
                    }, content_type='application/json')
            
            elif action == 'modes':
                # 获取所有可用模式
                modes = free_music_api.get_available_modes()
                mode_info = []
                for mode_name in modes:
                    mode_info.append(free_music_api.get_mode_info(mode_name))
                return JsonResponse({
                    'success': True,
                    'data': mode_info
                }, content_type='application/json')
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': '不支持的操作'
                }, content_type='application/json')
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'服务器错误: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': '不支持的请求方法'
    }, content_type='application/json')


def search_netease_music(keyword):
    """搜索网易云音乐"""
    try:
        import requests
        import re
        from urllib.parse import quote
        
        # 网易云音乐搜索API
        search_url = f"https://music.163.com/api/search/get/web?csrf_token=&s={quote(keyword)}&type=1&offset=0&total=true&limit=10"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://music.163.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('code') == 200 and data.get('result', {}).get('songs'):
            songs = []
            for song in data['result']['songs'][:5]:  # 只取前5首
                song_info = {
                    'id': song.get('id'),
                    'name': song.get('name', '未知歌曲'),
                    'artist': song.get('artists', [{}])[0].get('name', '未知艺术家') if song.get('artists') else '未知艺术家',
                    'album': song.get('album', {}).get('name', '未知专辑'),
                    'duration': format_duration(song.get('duration', 0)),
                    'play_url': f"https://music.163.com/song/media/outer/url?id={song.get('id')}.mp3",
                    'cover_url': song.get('album', {}).get('picUrl', ''),
                    'source': 'netease'
                }
                songs.append(song_info)
            
            return songs
        else:
            return []
            
    except Exception as e:
        print(f"网易云音乐搜索失败: {str(e)}")
        return []


def format_duration(ms):
    """格式化时长（毫秒转分:秒）"""
    if not ms:
        return "0:00"
    
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"

@csrf_exempt
@require_http_methods(["POST"])
def next_song_api(request):
    """下一首歌曲API"""
    try:
        data = json.loads(request.body)
        mode = data.get('mode', 'work')
        
        # 导入免费音乐API
        from .utils.music_api import free_music_api
        
        song = free_music_api.get_random_song(mode)
        if song:
            # 转换为前端期望的格式
            next_song = {
                'title': song.get('name', '未知歌曲'),
                'artist': song.get('artist', '未知艺术家'),
                'url': song.get('play_url', ''),
                'duration': '3:45'  # 在线音乐通常无法获取准确时长
            }
            
            return JsonResponse({
                'success': True,
                'next_song': next_song
            }, content_type='application/json')
        else:
            return JsonResponse({
                'success': False,
                'error': '获取下一首歌曲失败'
            }, content_type='application/json')
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


# 社交媒体订阅相关API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_social_subscription_api(request):
    """添加社交媒体订阅API"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform')
        target_user_id = data.get('target_user_id')
        target_user_name = data.get('target_user_name', target_user_id)
        subscription_types = data.get('subscription_types', [])
        check_frequency = data.get('check_frequency', 15)
        
        if not platform or not target_user_id:
            return JsonResponse({
                'success': False,
                'error': '平台和用户ID不能为空'
            }, status=400, content_type='application/json')
        
        # 检查是否已存在相同订阅
        from apps.tools.models import SocialMediaSubscription
        existing = SocialMediaSubscription.objects.filter(
            user=request.user,
            platform=platform,
            target_user_id=target_user_id
        ).first()
        
        if existing:
            return JsonResponse({
                'success': False,
                'error': '该用户已订阅'
            }, status=400, content_type='application/json')
        
        # 创建新订阅
        subscription = SocialMediaSubscription.objects.create(
            user=request.user,
            platform=platform,
            target_user_id=target_user_id,
            target_user_name=target_user_name,
            subscription_types=subscription_types,
            check_frequency=check_frequency
        )
        
        return JsonResponse({
            'success': True,
            'subscription': {
                'id': subscription.id,
                'platform': subscription.platform,
                'target_user_id': subscription.target_user_id,
                'target_user_name': subscription.target_user_name,
                'subscription_types': subscription.subscription_types,
                'check_frequency': subscription.check_frequency,
                'status': subscription.status,
                'created_at': subscription.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_subscriptions_api(request):
    """获取用户订阅列表API"""
    try:
        from apps.tools.models import SocialMediaSubscription
        
        subscriptions = SocialMediaSubscription.objects.filter(user=request.user)
        subscription_list = []
        
        for sub in subscriptions:
            subscription_list.append({
                'id': sub.id,
                'platform': sub.platform,
                'target_user_id': sub.target_user_id,
                'target_user_name': sub.target_user_name,
                'subscription_types': sub.subscription_types,
                'check_frequency': sub.check_frequency,
                'status': sub.status,
                'last_check': sub.last_check.isoformat() if sub.last_check else None,
                'avatar_url': sub.avatar_url,
                'created_at': sub.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'subscriptions': subscription_list
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_subscription_api(request):
    """更新订阅状态API"""
    try:
        data = json.loads(request.body)
        subscription_id = data.get('subscription_id')
        status = data.get('status')
        action = data.get('action')  # 'delete'
        
        from apps.tools.models import SocialMediaSubscription
        
        try:
            subscription = SocialMediaSubscription.objects.get(
                id=subscription_id,
                user=request.user
            )
        except SocialMediaSubscription.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '订阅不存在'
            }, status=404, content_type='application/json')
        
        if action == 'delete':
            subscription.delete()
            return JsonResponse({
                'success': True,
                'message': '订阅已删除'
            }, content_type='application/json')
        
        elif status:
            subscription.status = status
            subscription.save()
            return JsonResponse({
                'success': True,
                'status': subscription.status
            }, content_type='application/json')
        
        else:
            return JsonResponse({
                'success': False,
                'error': '无效的操作'
            }, status=400, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_notifications_api(request):
    """获取通知列表API"""
    try:
        from apps.tools.models import SocialMediaNotification
        
        # 获取所有通知
        notifications = SocialMediaNotification.objects.filter(
            subscription__user=request.user
        ).select_related('subscription').order_by('-created_at')
        
        notification_list = []
        for notif in notifications:
            notification_data = {
                'id': notif.id,
                'notification_type': notif.notification_type,
                'title': notif.title,
                'content': notif.content,
                'is_read': notif.is_read,
                'created_at': notif.created_at.isoformat(),
                'subscription': {
                    'platform': notif.subscription.platform,
                    'target_user_name': notif.subscription.target_user_name
                }
            }
            
            # 根据通知类型添加详细字段
            if notif.notification_type == 'newPosts':
                notification_data.update({
                    'post_content': notif.post_content,
                    'post_images': notif.post_images or [],
                    'post_video_url': notif.post_video_url,
                    'post_tags': notif.post_tags or [],
                    'post_likes': notif.post_likes,
                    'post_comments': notif.post_comments,
                    'post_shares': notif.post_shares,
                })
            
            elif notif.notification_type == 'newFollowers':
                notification_data.update({
                    'follower_name': notif.follower_name,
                    'follower_avatar': notif.follower_avatar,
                    'follower_id': notif.follower_id,
                    'follower_count': notif.follower_count,
                })
            
            elif notif.notification_type == 'newFollowing':
                notification_data.update({
                    'following_name': notif.following_name,
                    'following_avatar': notif.following_avatar,
                    'following_id': notif.following_id,
                    'following_count': notif.following_count,
                })
            
            elif notif.notification_type == 'profileChanges':
                notification_data.update({
                    'profile_changes': notif.profile_changes or {},
                    'old_profile_data': notif.old_profile_data or {},
                    'new_profile_data': notif.new_profile_data or {},
                })
            
            # 添加通用字段
            notification_data.update({
                'external_url': notif.external_url,
                'platform_specific_data': notif.platform_specific_data or {},
            })
            
            notification_list.append(notification_data)
        
        return JsonResponse({
            'success': True,
            'notifications': notification_list
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def mark_notification_read_api(request):
    """标记通知为已读API"""
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        action = data.get('action')  # 'mark_all_read'
        
        from apps.tools.models import SocialMediaNotification
        
        if action == 'mark_all_read':
            # 标记所有通知为已读
            SocialMediaNotification.objects.filter(
                subscription__user=request.user,
                is_read=False
            ).update(is_read=True)
            
            return JsonResponse({
                'success': True,
                'message': '所有通知已标记为已读'
            }, content_type='application/json')
        
        elif notification_id:
            # 标记单个通知为已读
            try:
                notification = SocialMediaNotification.objects.get(
                    id=notification_id,
                    subscription__user=request.user
                )
                notification.is_read = True
                notification.save()
                
                return JsonResponse({
                    'success': True,
                    'message': '已标记为已读'
                }, content_type='application/json')
                
            except SocialMediaNotification.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': '通知不存在'
                }, status=404, content_type='application/json')
        
        else:
            return JsonResponse({
                'success': False,
                'error': '缺少必要参数'
            }, status=400, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_subscription_stats_api(request):
    """获取订阅统计信息API"""
    try:
        from apps.tools.models import SocialMediaSubscription, SocialMediaNotification
        
        total_subscriptions = SocialMediaSubscription.objects.filter(user=request.user).count()
        active_subscriptions = SocialMediaSubscription.objects.filter(
            user=request.user, 
            status='active'
        ).count()
        new_notifications = SocialMediaNotification.objects.filter(
            subscription__user=request.user,
            is_read=False
        ).count()
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_subscriptions': total_subscriptions,
                'active_subscriptions': active_subscriptions,
                'new_notifications': new_notifications
            }
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# 生活日记相关API
@csrf_exempt
@login_required
def life_diary_api(request):
    """生活日记API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'save_diary':
                return save_life_diary(request, data)
            elif action == 'get_diary':
                return get_life_diary(request, data)
            elif action == 'get_statistics':
                return get_life_statistics(request)
            elif action == 'save_goal':
                return save_life_goal(request, data)
            elif action == 'get_goals':
                return get_life_goals(request)
            elif action == 'update_goal_progress':
                return update_goal_progress(request, data)
            elif action == 'get_history':
                return get_life_history(request, data)
            elif action == 'get_diary_list':
                return get_diary_list(request)
            elif action == 'get_happy_days_list':
                return get_happy_days_list(request)
            elif action == 'get_active_goals_list':
                return get_active_goals_list(request)
            elif action == 'get_completed_goals_list':
                return get_completed_goals_list(request)
            elif action == 'search_diaries':
                return search_diaries(request, data)
            elif action == 'get_mood_analysis':
                return get_mood_analysis(request, data)
            elif action == 'delete_diary':
                return delete_diary(request, data)
            elif action == 'delete_goal':
                return delete_goal(request, data)
            elif action == 'export_data':
                return export_diary_data(request, data)


            else:
                return JsonResponse({'success': False, 'error': '未知操作'}, content_type='application/json')
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': '无效的JSON数据'}, content_type='application/json')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': '不支持的请求方法'}, content_type='application/json')


def save_life_diary(request, data):
    """保存生活日记"""
    try:
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        mood = data.get('mood', 'neutral')
        mood_note = data.get('mood_note', '').strip()
        tags = data.get('tags', [])
        question_answers = data.get('question_answers', [])
        music_recommendation = data.get('music_recommendation', '').strip()
        date_str = data.get('date', '')  # 获取日期参数
        
        # 数据验证
        if not title:
            return JsonResponse({'success': False, 'error': '标题不能为空'}, content_type='application/json')
        if not content:
            return JsonResponse({'success': False, 'error': '内容不能为空'}, content_type='application/json')
        if len(title) > 200:
            return JsonResponse({'success': False, 'error': '标题长度不能超过200个字符'}, content_type='application/json')
        if len(content) > 5000:
            return JsonResponse({'success': False, 'error': '内容长度不能超过5000个字符'}, content_type='application/json')
        
        # 验证心情值
        valid_moods = ['happy', 'calm', 'excited', 'sad', 'angry', 'neutral']
        if mood not in valid_moods:
            return JsonResponse({'success': False, 'error': '无效的心情值'}, content_type='application/json')
        
        # 验证标签
        if not isinstance(tags, list):
            tags = []
        tags = [tag.strip() for tag in tags if tag.strip()][:10]  # 限制最多10个标签
        
        # 处理日期
        if date_str:
            try:
                from datetime import datetime
                diary_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'error': '日期格式无效，请使用YYYY-MM-DD格式'}, content_type='application/json')
        else:
            diary_date = timezone.now().date()
        
        # 创建新的日记记录
        diary_entry = LifeDiaryEntry.objects.create(
            user=request.user,
            date=diary_date,
            title=title,
            content=content,
            mood=mood,
            mood_note=mood_note,
            tags=tags,
            question_answers=question_answers,
            music_recommendation=music_recommendation
        )
        
        # 更新统计数据
        update_life_statistics(request.user)
        
        return JsonResponse({
            'success': True,
            'message': '日记保存成功',
            'diary_id': diary_entry.id
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'保存失败: {str(e)}'})


def get_life_diary(request, data):
    """获取生活日记"""
    try:
        date_str = data.get('date')
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = timezone.now().date()
        
        diary_entry = LifeDiaryEntry.objects.filter(
            user=request.user,
            date=target_date
        ).first()
        
        if diary_entry:
            return JsonResponse({
                'success': True,
                'data': {
                    'title': diary_entry.title,
                    'content': diary_entry.content,
                    'mood': diary_entry.mood,
                    'mood_note': diary_entry.mood_note,
                    'tags': diary_entry.tags,
                    'question_answers': diary_entry.question_answers,
                    'music_recommendation': diary_entry.music_recommendation,
                    'date': diary_entry.date.strftime('%Y-%m-%d')
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'data': None
            }, content_type='application/json')
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_life_statistics(request):
    """获取生活统计数据"""
    try:
        # 获取用户统计数据
        stats = LifeStatistics.objects.filter(user=request.user).first()
        
        if not stats:
            # 如果没有统计数据，创建一个
            stats = create_life_statistics(request.user)
        
        # 获取实时统计数据
        total_diary_count = LifeDiaryEntry.objects.filter(user=request.user).count()
        
        # 日记总天数（不同日期的数量）
        from django.db.models import Count
        total_diary_days = LifeDiaryEntry.objects.filter(user=request.user).values('date').annotate(
            day_count=Count('date')
        ).count()
        
        # 开心天数（不同日期中心情为开心的天数）
        happy_days = LifeDiaryEntry.objects.filter(
            user=request.user,
            mood='happy'
        ).values('date').distinct().count()
        
        # 计算总字数
        total_words = 0
        diary_entries = LifeDiaryEntry.objects.filter(user=request.user)
        for entry in diary_entries:
            if entry.content:
                total_words += len(entry.content)
        
        active_goals = LifeGoal.objects.filter(user=request.user, status='active').count()
        completed_goals = LifeGoal.objects.filter(
            user=request.user,
            status='completed'
        ).count()
        
        # 计算心情分布
        mood_distribution = {}
        diary_entries = LifeDiaryEntry.objects.filter(user=request.user)
        for entry in diary_entries:
            mood = entry.mood
            mood_distribution[mood] = mood_distribution.get(mood, 0) + 1
        
        # 计算目标完成率
        total_goals = active_goals + completed_goals
        goal_completion_rate = 0
        if total_goals > 0:
            goal_completion_rate = (completed_goals / total_goals) * 100
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_diary_count': total_diary_count,
                'total_diary_days': total_diary_days,
                'happy_days': happy_days,
                'total_words': total_words,
                'active_goals': active_goals,
                'completed_goals': completed_goals,
                'mood_distribution': mood_distribution,
                'goal_completion_rate': round(goal_completion_rate, 1)
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def save_life_goal(request, data):
    """保存生活目标"""
    try:
        goal_id = data.get('goal_id')
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        category = data.get('category', 'other')
        goal_type = data.get('goal_type', 'daily')
        start_date = data.get('start_date')
        target_date = data.get('target_date')
        priority = data.get('priority', 5)
        difficulty = data.get('difficulty', 'medium')
        milestones = data.get('milestones', [])
        tags = data.get('tags', [])
        reminder_enabled = data.get('reminder_enabled', True)
        reminder_frequency = data.get('reminder_frequency', 'daily')
        reminder_time = data.get('reminder_time', '09:00')
        
        # 数据验证
        if not title:
            return JsonResponse({'success': False, 'error': '目标标题不能为空'}, content_type='application/json')
        if len(title) > 200:
            return JsonResponse({'success': False, 'error': '目标标题长度不能超过200个字符'}, content_type='application/json')
        if len(description) > 1000:
            return JsonResponse({'success': False, 'error': '目标描述长度不能超过1000个字符'}, content_type='application/json')
        
        # 验证优先级
        try:
            priority = int(priority)
            if priority < 1 or priority > 10:
                return JsonResponse({'success': False, 'error': '优先级必须在1-10之间'}, content_type='application/json')
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': '优先级必须是数字'}, content_type='application/json')
        
        # 验证日期
        start_date_obj = None
        target_date_obj = None
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'error': '开始日期格式无效'}, content_type='application/json')
        
        if target_date:
            try:
                target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
                if start_date_obj and target_date_obj < start_date_obj:
                    return JsonResponse({'success': False, 'error': '目标日期不能早于开始日期'}, content_type='application/json')
            except ValueError:
                return JsonResponse({'success': False, 'error': '目标日期格式无效'}, content_type='application/json')
        
        # 验证里程碑
        if not isinstance(milestones, list):
            milestones = []
        validated_milestones = []
        for milestone in milestones[:10]:  # 限制最多10个里程碑
            if isinstance(milestone, dict) and milestone.get('text') and milestone.get('date'):
                try:
                    milestone_date = datetime.strptime(milestone['date'], '%Y-%m-%d').date()
                    validated_milestones.append({
                        'text': milestone['text'].strip()[:100],  # 限制长度
                        'date': milestone['date']
                    })
                except ValueError:
                    continue  # 跳过无效的里程碑
        
        # 验证标签
        if not isinstance(tags, list):
            tags = []
        tags = [tag.strip() for tag in tags if tag.strip()][:10]  # 限制最多10个标签
        
        if goal_id:
            # 更新现有目标
            try:
                goal = LifeGoal.objects.get(id=goal_id, user=request.user)
            except LifeGoal.DoesNotExist:
                return JsonResponse({'success': False, 'error': '目标不存在或无权限修改'}, content_type='application/json')
            
            goal.title = title
            goal.description = description
            goal.category = category
            goal.goal_type = goal_type
            goal.priority = priority
            goal.difficulty = difficulty
            goal.milestones = validated_milestones
            goal.tags = tags
            goal.reminder_enabled = reminder_enabled
            goal.reminder_frequency = reminder_frequency
            goal.reminder_time = reminder_time
            
            if start_date_obj:
                goal.start_date = start_date_obj
            if target_date_obj:
                goal.target_date = target_date_obj
            
            goal.save()
            created = False
        else:
            # 创建新目标
            goal_data = {
                'user': request.user,
                'title': title,
                'description': description,
                'category': category,
                'goal_type': goal_type,
                'priority': priority,
                'difficulty': difficulty,
                'milestones': validated_milestones,
                'tags': tags,
                'reminder_enabled': reminder_enabled,
                'reminder_frequency': reminder_frequency,
                'reminder_time': reminder_time
            }
            
            if start_date_obj:
                goal_data['start_date'] = start_date_obj
            if target_date_obj:
                goal_data['target_date'] = target_date_obj
            
            goal = LifeGoal.objects.create(**goal_data)
            created = True
        
        return JsonResponse({
            'success': True,
            'message': '目标保存成功',
            'goal_id': goal.id,
            'created': created
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'保存失败: {str(e)}'})


def get_life_goals(request):
    """获取生活目标列表"""
    try:
        goals = LifeGoal.objects.filter(user=request.user).order_by('-priority', '-created_at')
        
        goals_data = []
        for goal in goals:
            goals_data.append({
                'id': goal.id,
                'title': goal.title,
                'description': goal.description,
                'category': goal.category,
                'status': goal.status,
                'progress': goal.progress,
                'priority': goal.priority,
                'target_date': goal.target_date.strftime('%Y-%m-%d') if goal.target_date else None,
                'created_at': goal.created_at.strftime('%Y-%m-%d')
            })
        
        return JsonResponse({
            'success': True,
            'data': goals_data
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def update_goal_progress(request, data):
    """更新目标进度"""
    try:
        print(f"更新目标进度 - 接收数据: {data}")
        
        goal_id = data.get('goal_id')
        progress = data.get('progress', 0)
        notes = data.get('notes', '')
        goal_action = data.get('goal_action', 'update')  # update, complete, pause, cancel
        
        print(f"目标ID: {goal_id}, 动作: {goal_action}")
        
        goal = LifeGoal.objects.get(id=goal_id, user=request.user)
        print(f"找到目标: {goal.title}, 当前状态: {goal.status}")
        
        if goal_action == 'complete':
            goal.status = 'completed'
            goal.progress = 100
            goal.completed_at = timezone.now()
            print(f"目标已完成: {goal.title}")
        elif goal_action == 'pause':
            goal.status = 'paused'
        elif goal_action == 'cancel':
            goal.status = 'cancelled'
        else:
            goal.progress = progress
        
        goal.save()
        print(f"目标已保存，新状态: {goal.status}")
        
        # 记录进度
        if goal_action == 'update' and progress > 0:
            LifeGoalProgress.objects.create(
                goal=goal,
                progress_value=progress,
                notes=notes
            )
        
        return JsonResponse({
            'success': True,
            'message': '目标进度更新成功'
        }, content_type='application/json')
        
    except Exception as e:
        print(f"更新目标进度时出错: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


def get_life_history(request, data):
    """获取生活历史记录"""
    try:
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        limit = data.get('limit', 30)
        
        query = LifeDiaryEntry.objects.filter(user=request.user)
        
        if start_date:
            query = query.filter(date__gte=datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(date__lte=datetime.strptime(end_date, '%Y-%m-%d').date())
        
        entries = query.order_by('-date')[:limit]
        
        history_data = []
        for entry in entries:
            history_data.append({
                'date': entry.date.strftime('%Y-%m-%d'),
                'title': entry.title,
                'content': entry.content[:100] + '...' if len(entry.content) > 100 else entry.content,
                'mood': entry.mood,
                'tags': entry.tags
            })
        
        return JsonResponse({
            'success': True,
            'data': history_data
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def create_life_statistics(user):
    """创建生活统计数据"""
    # 日记总次数（所有日记条目的总数）
    total_diary_count = LifeDiaryEntry.objects.filter(user=user).count()
    
    # 日记总天数（不同日期的数量）
    diary_days = LifeDiaryEntry.objects.filter(user=user).values('date').distinct().count()
    
    # 开心天数（不同日期中心情为开心的天数）
    happy_days = LifeDiaryEntry.objects.filter(
        user=user, 
        mood='happy'
    ).values('date').distinct().count()
    
    total_goals = LifeGoal.objects.filter(user=user).count()
    completed_goals = LifeGoal.objects.filter(user=user, status='completed').count()
    
    # 计算心情分布
    mood_distribution = {}
    diary_entries = LifeDiaryEntry.objects.filter(user=user)
    for entry in diary_entries:
        mood = entry.mood
        mood_distribution[mood] = mood_distribution.get(mood, 0) + 1
    
    # 计算目标完成率
    goal_completion_rate = 0
    if total_goals > 0:
        goal_completion_rate = (completed_goals / total_goals) * 100
    
    return LifeStatistics.objects.create(
        user=user,
        total_diary_days=diary_days,
        total_diary_count=total_diary_count,
        happy_days=happy_days,
        total_goals=total_goals,
        completed_goals=completed_goals,
        mood_distribution=mood_distribution,
        goal_completion_rate=goal_completion_rate
    )


def update_life_statistics(user):
    """更新生活统计数据"""
    stats = LifeStatistics.objects.filter(user=user).first()
    if stats:
        # 更新统计数据
        # 日记总次数（所有日记条目的总数）
        stats.total_diary_count = LifeDiaryEntry.objects.filter(user=user).count()
        
        # 日记总天数（不同日期的数量）
        diary_days = LifeDiaryEntry.objects.filter(user=user).values('date').distinct().count()
        stats.total_diary_days = diary_days
        
        # 开心天数（不同日期中心情为开心的天数）
        happy_days = LifeDiaryEntry.objects.filter(
            user=user, 
            mood='happy'
        ).values('date').distinct().count()
        stats.happy_days = happy_days
        
        active_goals = LifeGoal.objects.filter(user=user, status='active').count()
        stats.completed_goals = LifeGoal.objects.filter(user=user, status='completed').count()
        stats.total_goals = active_goals + stats.completed_goals
        
        # 更新心情分布
        mood_distribution = {}
        diary_entries = LifeDiaryEntry.objects.filter(user=user)
        for entry in diary_entries:
            mood = entry.mood
            mood_distribution[mood] = mood_distribution.get(mood, 0) + 1
        stats.mood_distribution = mood_distribution
        
        # 更新目标完成率
        goal_completion_rate = 0
        if stats.total_goals > 0:
            goal_completion_rate = (stats.completed_goals / stats.total_goals) * 100
        stats.goal_completion_rate = goal_completion_rate
        
        stats.save()
    else:
        create_life_statistics(user)


def get_diary_list(request):
    """获取日记列表"""
    try:
        entries = LifeDiaryEntry.objects.filter(user=request.user).order_by('-created_at')
        diaries = []
        for entry in entries:
            diaries.append({
                'title': entry.title,
                'content': entry.content,
                'mood': entry.mood,
                'mood_note': entry.mood_note,
                'tags': entry.tags,
                'question_answers': entry.question_answers,
                'music_recommendation': entry.music_recommendation,
                'created_at': entry.created_at.isoformat(),
                'date': entry.date.strftime('%Y-%m-%d')
            })
        return JsonResponse({'success': True, 'diaries': diaries}, content_type='application/json')
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_happy_days_list(request):
    """获取开心天数列表"""
    try:
        entries = LifeDiaryEntry.objects.filter(user=request.user, mood='happy').order_by('-date')
        data = []
        for entry in entries:
            data.append({
                'type': 'diary',
                'date': entry.date.strftime('%Y-%m-%d'),
                'title': entry.title,
                'content': entry.content[:100] + '...' if len(entry.content) > 100 else entry.content,
                'mood': entry.mood
            })
        return JsonResponse({'success': True, 'data': data}, content_type='application/json')
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_active_goals_list(request):
    """获取未完成目标列表"""
    try:
        goals = LifeGoal.objects.filter(user=request.user, status='active').order_by('-priority', '-created_at')
        data = []
        for goal in goals:
            data.append({
                'type': 'goal',
                'created_date': goal.created_at.strftime('%Y-%m-%d'),
                'title': goal.title,
                'description': goal.description,
                'progress': goal.progress,
                'category': goal.category
            })
        return JsonResponse({'success': True, 'data': data}, content_type='application/json')
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_completed_goals_list(request):
    """获取已完成目标列表"""
    try:
        goals = LifeGoal.objects.filter(user=request.user, status='completed').order_by('-completed_at')
        data = []
        for goal in goals:
            data.append({
                'type': 'goal',
                'created_date': goal.created_at.strftime('%Y-%m-%d'),
                'completed_date': goal.completed_at.strftime('%Y-%m-%d') if goal.completed_at else '',
                'title': goal.title,
                'description': goal.description,
                'progress': goal.progress,
                'category': goal.category
            })
        return JsonResponse({'success': True, 'data': data}, content_type='application/json')
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def search_diaries(request, data):
    """搜索日记"""
    try:
        query = data.get('query', '').strip()
        mood_filter = data.get('mood', '')
        date_from = data.get('date_from', '')
        date_to = data.get('date_to', '')
        tags_filter = data.get('tags', [])
        limit = data.get('limit', 50)
        
        if not query and not mood_filter and not date_from and not date_to and not tags_filter:
            return JsonResponse({'success': False, 'error': '请提供搜索条件'}, content_type='application/json')
        
        diaries = LifeDiaryEntry.objects.filter(user=request.user)
        
        # 文本搜索
        if query:
            diaries = diaries.filter(
                models.Q(title__icontains=query) |
                models.Q(content__icontains=query) |
                models.Q(mood_note__icontains=query)
            )
        
        # 心情过滤
        if mood_filter:
            diaries = diaries.filter(mood=mood_filter)
        
        # 日期范围过滤
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                diaries = diaries.filter(date__gte=from_date)
            except ValueError:
                return JsonResponse({'success': False, 'error': '开始日期格式无效'}, content_type='application/json')
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                diaries = diaries.filter(date__lte=to_date)
            except ValueError:
                return JsonResponse({'success': False, 'error': '结束日期格式无效'}, content_type='application/json')
        
        # 标签过滤
        if tags_filter and isinstance(tags_filter, list):
            for tag in tags_filter:
                diaries = diaries.filter(tags__contains=[tag])
        
        diaries = diaries.order_by('-date')[:limit]
        
        results = []
        for diary in diaries:
            results.append({
                'id': diary.id,
                'date': diary.date.strftime('%Y-%m-%d'),
                'title': diary.title,
                'content': diary.content[:200] + '...' if len(diary.content) > 200 else diary.content,
                'mood': diary.mood,
                'tags': diary.tags,
                'created_at': diary.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'data': results,
            'total': len(results)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'搜索失败: {str(e)}'})


def get_mood_analysis(request, data):
    """获取心情分析"""
    try:
        days = data.get('days', 30)
        if days > 365:
            days = 365
        
        from_date = timezone.now().date() - timezone.timedelta(days=days)
        
        diaries = LifeDiaryEntry.objects.filter(
            user=request.user,
            date__gte=from_date
        ).order_by('date')
        
        # 心情分布统计
        mood_counts = {}
        mood_timeline = []
        
        for diary in diaries:
            mood = diary.mood
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            mood_timeline.append({
                'date': diary.date.strftime('%Y-%m-%d'),
                'mood': mood,
                'title': diary.title
            })
        
        # 计算心情趋势 - 优化算法
        mood_trend = 'stable'
        if len(mood_timeline) >= 5:  # 至少需要5天数据
            # 定义心情权重（正数表示积极，负数表示消极）
            mood_weights = {
                'happy': 3,      # 非常积极
                'excited': 2,    # 兴奋
                'content': 1,    # 满足
                'neutral': 0,    # 中性
                'worried': -1,   # 担心
                'sad': -2,       # 悲伤
                'angry': -3,     # 愤怒
                'anxious': -2,   # 焦虑
                'stressed': -2,  # 压力
                'calm': 1,       # 平静
                'grateful': 2,   # 感恩
                'inspired': 2,   # 受启发
                'confident': 2,  # 自信
                'tired': -1,     # 疲惫
                'frustrated': -2 # 沮丧
            }
            
            # 计算最近14天的加权平均心情
            recent_days = min(14, len(mood_timeline))
            recent_moods = mood_timeline[-recent_days:]
            
            # 计算加权总分
            total_score = 0
            valid_entries = 0
            
            for item in recent_moods:
                mood = item['mood']
                if mood in mood_weights:
                    total_score += mood_weights[mood]
                    valid_entries += 1
            
            if valid_entries > 0:
                average_score = total_score / valid_entries
                
                # 计算趋势变化（比较前半段和后半段）
                if len(recent_moods) >= 8:
                    first_half = recent_moods[:len(recent_moods)//2]
                    second_half = recent_moods[len(recent_moods)//2:]
                    
                    first_score = sum(mood_weights.get(item['mood'], 0) for item in first_half)
                    second_score = sum(mood_weights.get(item['mood'], 0) for item in second_half)
                    
                    first_avg = first_score / len(first_half) if first_half else 0
                    second_avg = second_score / len(second_half) if second_half else 0
                    
                    # 判断趋势
                    if second_avg > first_avg + 0.5:  # 有明显改善
                        mood_trend = 'improving'
                    elif second_avg < first_avg - 0.5:  # 有明显下降
                        mood_trend = 'declining'
                    else:
                        # 基于整体平均分判断
                        if average_score > 0.5:
                            mood_trend = 'improving'
                        elif average_score < -0.5:
                            mood_trend = 'declining'
                        else:
                            mood_trend = 'stable'
                else:
                    # 数据不足时基于平均分判断
                    if average_score > 0.5:
                        mood_trend = 'improving'
                    elif average_score < -0.5:
                        mood_trend = 'declining'
                    else:
                        mood_trend = 'stable'
        
        # 最常出现的心情
        most_common_mood = max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else 'neutral'
        
        # 计算心情统计信息
        mood_stats = {
            'total_entries': len(diaries),
            'analysis_period': f'最近{days}天',
            'mood_distribution': mood_counts,
            'mood_timeline': mood_timeline,
            'mood_trend': mood_trend,
            'most_common_mood': most_common_mood,
            'trend_confidence': 'high' if len(mood_timeline) >= 10 else 'medium' if len(mood_timeline) >= 5 else 'low',
            'positive_days': sum(1 for item in mood_timeline if item['mood'] in ['happy', 'excited', 'content', 'calm', 'grateful', 'inspired', 'confident']),
            'negative_days': sum(1 for item in mood_timeline if item['mood'] in ['sad', 'angry', 'anxious', 'stressed', 'frustrated']),
            'neutral_days': sum(1 for item in mood_timeline if item['mood'] in ['neutral', 'worried', 'tired'])
        }
        
        # 计算心情稳定性
        if len(mood_timeline) >= 7:
            mood_changes = 0
            for i in range(1, len(mood_timeline)):
                if mood_timeline[i]['mood'] != mood_timeline[i-1]['mood']:
                    mood_changes += 1
            mood_stats['stability'] = 'stable' if mood_changes <= len(mood_timeline) * 0.3 else 'volatile' if mood_changes >= len(mood_timeline) * 0.7 else 'moderate'
        else:
            mood_stats['stability'] = 'insufficient_data'
        
        return JsonResponse({
            'success': True,
            'data': mood_stats
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'分析失败: {str(e)}'})


def delete_diary(request, data):
    """删除日记"""
    try:
        diary_id = data.get('diary_id')
        if not diary_id:
            return JsonResponse({'success': False, 'error': '日记ID不能为空'}, content_type='application/json')
        
        try:
            diary = LifeDiaryEntry.objects.get(id=diary_id, user=request.user)
            diary.delete()
            
            # 更新统计数据
            update_life_statistics(request.user)
            
            return JsonResponse({
                'success': True,
                'message': '日记删除成功'
            }, content_type='application/json')
        except LifeDiaryEntry.DoesNotExist:
            return JsonResponse({'success': False, 'error': '日记不存在或无权限删除'}, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'删除失败: {str(e)}'})


def delete_goal(request, data):
    """删除目标"""
    try:
        goal_id = data.get('goal_id')
        if not goal_id:
            return JsonResponse({'success': False, 'error': '目标ID不能为空'}, content_type='application/json')
        
        try:
            goal = LifeGoal.objects.get(id=goal_id, user=request.user)
            goal.delete()
            
            # 更新统计数据
            update_life_statistics(request.user)
            
            return JsonResponse({
                'success': True,
                'message': '目标删除成功'
            }, content_type='application/json')
        except LifeGoal.DoesNotExist:
            return JsonResponse({'success': False, 'error': '目标不存在或无权限删除'}, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'删除失败: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
def emo_diary_api(request):
    """情感日记API"""
    try:
        data = json.loads(request.body)
        action = data.get('action', '')
        
        if action == 'save_diary':
            # 保存情感日记
            title = data.get('title', '')
            content = data.get('content', '')
            emotion = data.get('emotion', '')
            intensity = data.get('intensity', 5)
            triggers = data.get('triggers', '')
            emotion_note = data.get('emotion_note', '')
            
            if not title or not content:
                return JsonResponse({'success': False, 'error': '请填写标题和内容'}, content_type='application/json')
            
            # 这里可以保存到数据库，暂时返回成功
            return JsonResponse({
                'success': True,
                'message': '情感日记保存成功',
                'data': {
                    'title': title,
                    'content': content,
                    'emotion': emotion,
                    'intensity': intensity,
                    'triggers': triggers,
                    'emotion_note': emotion_note,
                    'created_at': timezone.now().isoformat()
                }
            })
        
        elif action == 'get_statistics':
            # 获取情感统计
            return JsonResponse({
                'success': True,
                'data': {
                    'total_entries': 0,
                    'happy_days': 0,
                    'sad_days': 0,
                    'calm_days': 0,
                    'average_intensity': 5.0
                }
            }, content_type='application/json')
        
        elif action == 'get_history':
            # 获取历史记录
            return JsonResponse({
                'success': True,
                'data': []
            }, content_type='application/json')
        
        else:
            return JsonResponse({'success': False, 'error': '未知操作'}, content_type='application/json')
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def creative_writer_api(request):
    """创意写作API"""
    try:
        data = json.loads(request.body)
        action = data.get('action', '')
        
        if action == 'generate_content':
            # 生成创意内容
            prompt = data.get('prompt', '')
            style = data.get('style', 'creative')
            length = data.get('length', 'medium')
            
            if not prompt:
                return JsonResponse({'success': False, 'error': '请提供写作提示'}, content_type='application/json')
            
            # 这里可以调用AI生成内容，暂时返回示例
            generated_content = f"基于您的提示'{prompt}'，我为您生成了{style}风格的{length}长度内容..."
            
            return JsonResponse({
                'success': True,
                'data': {
                    'content': generated_content,
                    'style': style,
                    'length': length,
                    'generated_at': timezone.now().isoformat()
                }
            })
        
        elif action == 'save_draft':
            # 保存草稿
            title = data.get('title', '')
            content = data.get('content', '')
            
            if not title or not content:
                return JsonResponse({'success': False, 'error': '请填写标题和内容'}, content_type='application/json')
            
            return JsonResponse({
                'success': True,
                'message': '草稿保存成功',
                'data': {
                    'title': title,
                    'content': content,
                    'saved_at': timezone.now().isoformat()
                }
            })
        
        else:
            return JsonResponse({'success': False, 'error': '未知操作'}, content_type='application/json')
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def fitness_api(request):
    """FitMatrix健身矩阵API"""
    try:
        data = json.loads(request.body)
        action = data.get('action', '')
        
        if action == 'save_workout':
            # 保存健身记录
            workout_type = data.get('workout_type', '')
            duration = data.get('duration', 0)
            calories = data.get('calories', 0)
            notes = data.get('notes', '')
            
            if not workout_type:
                return JsonResponse({'success': False, 'error': '请选择运动类型'}, content_type='application/json')
            
            return JsonResponse({
                'success': True,
                'message': '健身记录保存成功',
                'data': {
                    'workout_type': workout_type,
                    'duration': duration,
                    'calories': calories,
                    'notes': notes,
                    'recorded_at': timezone.now().isoformat()
                }
            })
        
        elif action == 'get_statistics':
            # 获取健身统计
            return JsonResponse({
                'success': True,
                'data': {
                    'total_workouts': 0,
                    'total_calories': 0,
                    'total_duration': 0,
                    'weekly_goal_progress': 0,
                    'monthly_goal_progress': 0
                }
            }, content_type='application/json')
        
        elif action == 'get_workout_history':
            # 获取健身历史
            return JsonResponse({
                'success': True,
                'data': []
            }, content_type='application/json')
        
        else:
            return JsonResponse({'success': False, 'error': '未知操作'}, content_type='application/json')
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# 辅助函数
def is_user_active(user):
    """检查用户是否活跃（10分钟内有过活动）"""
    from django.utils import timezone
    from datetime import timedelta
    
    # 检查用户最后活动时间
    try:
        online_status = UserOnlineStatus.objects.filter(user=user).first()
        if online_status and online_status.last_seen:
            return timezone.now() - online_status.last_seen < timedelta(minutes=10)
    except:
        pass
    
    # 如果没有在线状态记录，检查最后登录时间
    if user.last_login:
        return timezone.now() - user.last_login < timedelta(minutes=20)
    
    # 如果用户没有登录记录，但用户存在，认为用户是活跃的
    return True

def cleanup_expired_heart_link_requests():
    """清理过期的心动链接请求"""
    from django.utils import timezone
    from datetime import timedelta
    
    # 清理超过10分钟的pending请求
    expired_requests = HeartLinkRequest.objects.filter(
        status='pending',
        created_at__lt=timezone.now() - timedelta(minutes=10)
    )
    
    for request in expired_requests:
        request.status = 'expired'
        request.save()
    
    # 清理不活跃用户的pending请求（更宽松的条件，只有在用户超过15分钟不活跃时才清理）
    inactive_requests = HeartLinkRequest.objects.filter(status='pending')
    for request in inactive_requests:
        # 检查用户是否超过15分钟不活跃
        try:
            online_status = UserOnlineStatus.objects.filter(user=request.requester).first()
            if online_status and online_status.last_seen:
                if timezone.now() - online_status.last_seen > timedelta(minutes=15):
                    request.status = 'expired'
                    request.save()
            elif request.requester.last_login:
                if timezone.now() - request.requester.last_login > timedelta(minutes=25):
                    request.status = 'expired'
                    request.save()
        except:
            pass

def disconnect_inactive_users():
    """断开不活跃用户的连接"""
    from django.utils import timezone
    from datetime import timedelta
    
    # 查找活跃的聊天室
    active_rooms = ChatRoom.objects.filter(status='active')
    
    for room in active_rooms:
        # 检查聊天室是否刚创建（5分钟内不结束）
        if timezone.now() - room.created_at < timedelta(minutes=5):
            continue
            
        # 检查房间中的用户是否都活跃（更宽松的条件）
        # 只有在两个用户都超过30分钟不活跃时才结束聊天室
        user1_inactive = False
        user2_inactive = False
        
        # 检查用户1是否超过30分钟不活跃
        try:
            online_status1 = UserOnlineStatus.objects.filter(user=room.user1).first()
            if online_status1 and online_status1.last_seen:
                user1_inactive = timezone.now() - online_status1.last_seen > timedelta(minutes=30)
            elif room.user1.last_login:
                user1_inactive = timezone.now() - room.user1.last_login > timedelta(minutes=45)
        except:
            pass
        
        # 检查用户2是否超过30分钟不活跃
        if room.user2:
            try:
                online_status2 = UserOnlineStatus.objects.filter(user=room.user2).first()
                if online_status2 and online_status2.last_seen:
                    user2_inactive = timezone.now() - online_status2.last_seen > timedelta(minutes=30)
                elif room.user2.last_login:
                    user2_inactive = timezone.now() - room.user2.last_login > timedelta(minutes=45)
            except:
                pass
        
        # 只有在两个用户都不活跃时才结束聊天室
        if user1_inactive and user2_inactive:
            room.status = 'ended'
            room.ended_at = timezone.now()
            room.save()
            
            # 更新相关的心动链接请求状态
            HeartLinkRequest.objects.filter(
                chat_room=room,
                status='matched'
            ).update(status='expired')

# API视图函数
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_heart_link_request_api(request):
    """创建心动链接请求API"""
    # 设置响应头，确保返回JSON
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False, 
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    if request.method == 'POST':
        try:
            # 减少清理频率，只在必要时清理（10%的概率）
            import random
            if random.random() < 0.1:
                cleanup_expired_heart_link_requests()
            
            # 检查用户是否已有待处理的请求
            existing_request = HeartLinkRequest.objects.filter(
                requester=request.user,
                status='pending'
            ).first()
            
            if existing_request:
                # 检查请求是否过期
                if existing_request.is_expired:
                    existing_request.status = 'expired'
                    existing_request.save()
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '您已有一个正在等待匹配的心动链接请求，请稍后再试或先取消当前请求'
                    }, status=400, content_type='application/json', headers=response_headers)
            
            # 检查用户是否在活跃的聊天室中
            active_chat_room = ChatRoom.objects.filter(
                (models.Q(user1=request.user) | models.Q(user2=request.user)),
                status='active'
            ).first()
            
            if active_chat_room:
                # 如果用户已有活跃的聊天室，直接返回重连信息
                return JsonResponse({
                    'success': True,
                    'reconnect': True,
                    'room_id': active_chat_room.room_id,
                    'matched_user': active_chat_room.user2.username if active_chat_room.user1 == request.user else active_chat_room.user1.username,
                    'message': '您已有一个活跃的聊天室，正在为您重连...'
                }, content_type='application/json', headers=response_headers)
            
            # 创建新的心动链接请求
            heart_link_request = HeartLinkRequest.objects.create(requester=request.user)
            
            # 使用智能匹配服务
            from apps.tools.services.heart_link_matcher import matcher
            
            # 清理过期请求（减少频率）
            if random.random() < 0.1:
                matcher.cleanup_expired_requests()
            
            # 尝试智能匹配
            chat_room, matched_user = matcher.match_users(request.user, heart_link_request)
            
            if chat_room and matched_user:
                return JsonResponse({
                    'success': True,
                    'matched': True,
                    'request_id': heart_link_request.id,
                    'room_id': chat_room.room_id,
                    'matched_user': matched_user.username
                }, content_type='application/json', headers=response_headers)
            
            # 如果没有匹配到，返回等待状态
            return JsonResponse({
                'success': True,
                'matched': False,
                'request_id': heart_link_request.id,
                'message': '正在等待匹配...'
            }, content_type='application/json', headers=response_headers)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'创建心动链接请求失败: {str(e)}'
            }, status=500, content_type='application/json', headers=response_headers)
    
    return JsonResponse({
        'success': False,
        'error': '无效的请求方法'
    }, status=405, content_type='application/json', headers=response_headers)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def cancel_heart_link_request_api(request):
    """取消心动链接请求API"""
    # 设置响应头，确保返回JSON
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False, 
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    if request.method == 'POST':
        try:
            # 查找用户的所有pending请求
            pending_requests = HeartLinkRequest.objects.filter(
                requester=request.user,
                status='pending'
            )
            
            if not pending_requests.exists():
                return JsonResponse({
                    'success': False,
                    'error': '没有找到待处理的请求'
                }, status=404, content_type='application/json', headers=response_headers)
            
            # 取消所有pending请求
            cancelled_count = pending_requests.update(status='cancelled')
            
            return JsonResponse({
                'success': True,
                'message': f'已取消 {cancelled_count} 个匹配请求'
            }, content_type='application/json', headers=response_headers)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'取消请求失败: {str(e)}'
            }, status=500, content_type='application/json', headers=response_headers)
    
    return JsonResponse({
        'success': False,
        'error': '无效的请求方法'
    }, status=405, content_type='application/json', headers=response_headers)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def check_heart_link_status_api(request):
    """检查心动链接状态API"""
    # 设置响应头，确保返回JSON
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False, 
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    try:
        # 减少过期清理的频率，只在必要时清理
        # 清理超过10分钟的pending请求（只清理真正过期的）
        from datetime import timedelta
        import random
        
        # 只有5%的概率执行清理，进一步减少数据库压力和避免影响等待用户
        if random.random() < 0.05:
            expired_requests = HeartLinkRequest.objects.filter(
                status='pending',
                created_at__lt=timezone.now() - timedelta(minutes=10)
            )
            for request in expired_requests:
                request.status = 'expired'
                request.save()
        
        # 查找用户的最新请求（包括所有状态）
        heart_link_request = HeartLinkRequest.objects.filter(
            requester=request.user
        ).order_by('-created_at').first()
        
        if not heart_link_request:
            return JsonResponse({
                'success': True,
                'status': 'not_found',
                'message': '没有找到请求记录'
            }, content_type='application/json', headers=response_headers)
        
        # 检查pending状态的请求是否已过期（更宽松的检查）
        if heart_link_request.status == 'pending':
            # 检查用户是否活跃，如果活跃则自动续期
            try:
                online_status = UserOnlineStatus.objects.filter(user=request.user).first()
                is_user_active = False
                
                if online_status and online_status.last_seen:
                    # 如果用户5分钟内活跃，自动续期
                    if timezone.now() - online_status.last_seen < timedelta(minutes=5):
                        is_user_active = True
                        # 自动续期：更新创建时间（延长5分钟）
                        heart_link_request.created_at = timezone.now() - timedelta(minutes=5)
                        heart_link_request.save()
                
                # 检查是否需要显示过期警告
                from apps.tools.services.heart_link_notification import notification_service
                warning_message = None
                if notification_service.should_show_warning(heart_link_request):
                    warning_message = notification_service.get_expiry_warning_message(heart_link_request)
                
                # 只有在请求确实超过15分钟且用户不活跃时才标记为过期
                if timezone.now() - heart_link_request.created_at > timedelta(minutes=15):
                    heart_link_request.status = 'expired'
                    heart_link_request.save()
                    return JsonResponse({
                        'success': True,
                        'status': 'expired',
                        'message': '匹配请求已过期'
                    }, content_type='application/json', headers=response_headers)
                
                # 返回pending状态，包含警告信息
                response_data = {
                    'success': True,
                    'status': 'pending',
                    'message': '正在等待匹配...'
                }
                if warning_message:
                    response_data['warning'] = warning_message
                return JsonResponse(response_data, content_type='application/json', headers=response_headers)
                    
            except Exception as e:
                # 如果检查失败，使用原来的10分钟过期逻辑
                if timezone.now() - heart_link_request.created_at > timedelta(minutes=10):
                    heart_link_request.status = 'expired'
                    heart_link_request.save()
                    return JsonResponse({
                        'success': True,
                        'status': 'expired',
                        'message': '匹配请求已过期'
                    }, content_type='application/json', headers=response_headers)
        
        # 检查已匹配的请求是否应该过期（更宽松的条件）
        if heart_link_request.status == 'matched' and heart_link_request.chat_room:
            # 对于已匹配的请求，使用更宽松的活跃检查
            # 只有在匹配时间超过60分钟且对方用户确实不活跃时才标记为过期
            from datetime import timedelta
            match_time_threshold = timedelta(minutes=60)
            
            if (heart_link_request.matched_at and 
                timezone.now() - heart_link_request.matched_at > match_time_threshold and
                heart_link_request.matched_with):
                
                # 检查对方用户是否超过20分钟不活跃
                try:
                    online_status = UserOnlineStatus.objects.filter(user=heart_link_request.matched_with).first()
                    if online_status and online_status.last_seen:
                        if timezone.now() - online_status.last_seen > timedelta(minutes=20):
                            heart_link_request.status = 'expired'
                            heart_link_request.save()
                            return JsonResponse({
                                'success': True,
                                'status': 'expired',
                                'message': '对方用户已离线，连接已断开'
                            }, content_type='application/json', headers=response_headers)
                    elif heart_link_request.matched_with.last_login:
                        if timezone.now() - heart_link_request.matched_with.last_login > timedelta(minutes=30):
                            heart_link_request.status = 'expired'
                            heart_link_request.save()
                            return JsonResponse({
                                'success': True,
                                'status': 'expired',
                                'message': '对方用户已离线，连接已断开'
                            }, content_type='application/json', headers=response_headers)
                except:
                    pass
        
        # 检查是否已被匹配
        if heart_link_request.status == 'matched' and heart_link_request.chat_room:
            return JsonResponse({
                'success': True,
                'status': 'matched',
                'room_id': heart_link_request.chat_room.room_id,
                'matched_user': heart_link_request.matched_with.username if heart_link_request.matched_with else '未知用户'
            }, content_type='application/json', headers=response_headers)
        
        # 检查其他状态
        if heart_link_request.status == 'pending':
            return JsonResponse({
                'success': True,
                'status': 'pending',
                'message': '正在等待匹配...'
            }, content_type='application/json', headers=response_headers)
        elif heart_link_request.status == 'expired':
            return JsonResponse({
                'success': True,
                'status': 'expired',
                'message': '请求已过期'
            }, content_type='application/json', headers=response_headers)
        elif heart_link_request.status == 'cancelled':
            return JsonResponse({
                'success': True,
                'status': 'cancelled',
                'message': '请求已取消'
            }, content_type='application/json', headers=response_headers)
        
        return JsonResponse({
            'success': True,
            'status': heart_link_request.status,
            'message': f'当前状态: {heart_link_request.get_status_display()}'
        }, content_type='application/json', headers=response_headers)
        
    except HeartLinkRequest.DoesNotExist:
        return JsonResponse({
            'success': True,
            'status': 'not_found',
            'message': '没有找到待处理的请求'
        }, content_type='application/json', headers=response_headers)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'检查状态失败: {str(e)}'
        }, status=500, content_type='application/json', headers=response_headers)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def cleanup_heart_link_api(request):
    """清理心动链接API - 强制清理所有过期请求"""
    # 设置响应头，确保返回JSON
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    if request.method == 'POST':
        try:
            # 检查是否有指定要结束的聊天室
            try:
                data = json.loads(request.body) if request.body else {}
                room_id = data.get('room_id')
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试从POST数据获取
                room_id = request.POST.get('room_id')
                data = {}
            
            if room_id:
                # 结束指定的聊天室
                try:
                    chat_room = ChatRoom.objects.get(room_id=room_id)
                    
                    # 检查用户是否是聊天室的参与者
                    participants = [chat_room.user1]
                    if chat_room.user2:
                        participants.append(chat_room.user2)
                    
                    if request.user not in participants:
                        return JsonResponse({
                            'success': False,
                            'error': '您没有权限结束此聊天室'
                        }, status=403, content_type='application/json', headers=response_headers)
                    
                    # 结束聊天室
                    chat_room.status = 'ended'
                    chat_room.ended_at = timezone.now()
                    chat_room.save()
                    
                    # 更新相关的心动链接请求状态为过期
                    HeartLinkRequest.objects.filter(
                        chat_room=chat_room,
                        status='matched'
                    ).update(status='expired')
                    
                    return JsonResponse({
                        'success': True,
                        'message': '聊天室已结束',
                        'room_id': room_id
                    }, content_type='application/json', headers=response_headers)
                    
                except ChatRoom.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': '聊天室不存在'
                    }, status=404, content_type='application/json', headers=response_headers)
            else:
                # 执行全局清理
                cleanup_expired_heart_link_requests()
                disconnect_inactive_users()
                
                # 统计清理结果
                expired_count = HeartLinkRequest.objects.filter(status='expired').count()
                ended_rooms = ChatRoom.objects.filter(status='ended').count()
                
                return JsonResponse({
                    'success': True,
                    'message': f'清理完成！已清理 {expired_count} 个过期请求，结束 {ended_rooms} 个聊天室',
                    'expired_requests': expired_count,
                    'ended_rooms': ended_rooms
                }, content_type='application/json', headers=response_headers)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'清理失败: {str(e)}'
            }, status=500, content_type='application/json', headers=response_headers)
    
    return JsonResponse({
        'success': False,
        'error': '无效的请求方法'
    }, status=405, content_type='application/json', headers=response_headers)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_chat_messages_api(request, room_id):
    """获取聊天消息API"""
    # 设置响应头，确保返回JSON
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    try:
        # 获取聊天室
        chat_room = ChatRoom.objects.get(room_id=room_id)
        
        # 检查聊天室状态
        if chat_room.status == 'ended':
            return JsonResponse({
                'success': False,
                'error': '聊天室已结束',
                'room_ended': True
            }, status=410, content_type='application/json', headers=response_headers)
        
        # 检查用户是否是聊天室的参与者
        participants = [chat_room.user1]
        if chat_room.user2:
            participants.append(chat_room.user2)
        
        if request.user not in participants:
            return JsonResponse({
                'success': False,
                'error': '您没有权限访问此聊天室'
            }, status=403, content_type='application/json', headers=response_headers)
        
        # 获取消息
        messages = ChatMessage.objects.filter(room=chat_room).order_by('created_at')
        
        # 格式化消息
        message_list = []
        for message in messages:
            # 处理文件URL，确保返回完整的URL路径
            file_url = message.file_url
            if file_url and not file_url.startswith('http') and not file_url.startswith('/'):
                file_url = f'/media/{file_url}'
            
            message_list.append({
                'id': message.id,
                'sender': message.sender.username,
                'content': message.content,
                'message_type': message.message_type,
                'file_url': file_url,
                'created_at': message.created_at.isoformat(),
                'is_own': message.sender == request.user,
                'is_read': message.is_read
            })
        
        return JsonResponse({
            'success': True,
            'messages': message_list,
            'room_id': room_id
        }, content_type='application/json', headers=response_headers)
        
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '聊天室不存在'
        }, status=404, content_type='application/json', headers=response_headers)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取消息失败: {str(e)}'
        }, status=500, content_type='application/json', headers=response_headers)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def send_message_api(request, room_id):
    """发送消息API"""
    # 设置响应头，确保返回JSON
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    if request.method == 'POST':
        try:
            # 获取聊天室
            chat_room = ChatRoom.objects.get(room_id=room_id)
            
            # 检查聊天室状态
            if chat_room.status == 'ended':
                return JsonResponse({
                    'success': False,
                    'error': '聊天室已结束，无法发送消息',
                    'room_ended': True
                }, status=410, content_type='application/json', headers=response_headers)
            
            # 检查用户是否是聊天室的参与者
            participants = [chat_room.user1]
            if chat_room.user2:
                participants.append(chat_room.user2)
            
            if request.user not in participants:
                return JsonResponse({
                    'success': False,
                    'error': '您没有权限在此聊天室发送消息'
                }, status=403, content_type='application/json', headers=response_headers)
            
            # 获取消息内容
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            
            if not content:
                return JsonResponse({
                    'success': False,
                    'error': '消息内容不能为空'
                }, status=400, content_type='application/json', headers=response_headers)
            
            # 防重复发送检查：检查最近1秒内是否有相同内容的消息
            recent_message = ChatMessage.objects.filter(
                room=chat_room,
                sender=request.user,
                content=content,
                created_at__gte=timezone.now() - timezone.timedelta(seconds=1)
            ).first()
            
            if recent_message:
                return JsonResponse({
                    'success': False,
                    'error': '消息发送过于频繁，请稍后再试'
                }, status=429, content_type='application/json', headers=response_headers)
            
            # 创建消息
            message = ChatMessage.objects.create(
                room=chat_room,
                sender=request.user,
                content=content,
                message_type='text'
            )
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'sender': message.sender.username,
                    'content': message.content,
                    'message_type': message.message_type,
                    'created_at': message.created_at.isoformat(),
                    'is_own': True,
                    'is_read': False
                }
            }, content_type='application/json', headers=response_headers)
            
        except ChatRoom.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '聊天室不存在'
            }, status=404, content_type='application/json', headers=response_headers)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': '无效的JSON格式'
            }, status=400, content_type='application/json', headers=response_headers)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'发送消息失败: {str(e)}'
            }, status=500, content_type='application/json', headers=response_headers)
    
    return JsonResponse({
        'success': False,
        'error': '无效的请求方法'
    }, status=405, content_type='application/json', headers=response_headers)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_online_status_api(request):
    """更新在线状态API"""
    # 设置响应头，确保返回JSON
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    if request.method == 'POST':
        try:
            # 解析JSON请求体
            data = json.loads(request.body)
            status = data.get('status', 'online')
            room_id = data.get('room_id', '')
            
            # 更新用户在线状态
            update_data = {
                'last_seen': timezone.now(),
                'status': status
            }
            
            # 如果提供了room_id，更新当前房间
            if room_id:
                try:
                    chat_room = ChatRoom.objects.get(room_id=room_id)
                    update_data['current_room'] = chat_room
                except ChatRoom.DoesNotExist:
                    # 如果房间不存在，记录错误但不影响在线状态更新
                    pass
            
            # 添加重试逻辑处理数据库锁
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    UserOnlineStatus.objects.update_or_create(
                        user=request.user,
                        defaults=update_data
                    )
                    break  # 成功则跳出循环
                except Exception as db_error:
                    retry_count += 1
                    import logging
                    logger = logging.getLogger(__name__)
                    
                    # 如果是数据库锁错误且还有重试次数
                    if 'database is locked' in str(db_error) and retry_count < max_retries:
                        logger.warning(f'数据库锁错误，重试第{retry_count}次: {str(db_error)}')
                        import time
                        time.sleep(0.1 * retry_count)  # 递增延迟
                        continue
                    else:
                        # 其他错误或重试次数用完
                        logger.error(f'更新在线状态失败: {str(db_error)}', exc_info=True)
                        return JsonResponse({
                            'success': False,
                            'error': '服务器内部错误，请稍后重试'
                        }, status=500, content_type='application/json', headers=response_headers)
            
            return JsonResponse({
                'success': True,
                'message': '在线状态已更新'
            }, content_type='application/json', headers=response_headers)
            
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': '无效的JSON数据格式'
            }, status=400, content_type='application/json', headers=response_headers)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'更新在线状态失败: {str(e)}', exc_info=True)
            return JsonResponse({
                'success': False,
                'error': '服务器内部错误，请稍后重试'
            }, status=500, content_type='application/json', headers=response_headers)
    
    return JsonResponse({
        'success': False,
        'error': '无效的请求方法'
    }, status=405, content_type='application/json', headers=response_headers)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_online_users_api(request, room_id):
    """获取在线用户API"""
    # 设置响应头，确保返回JSON
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    try:
        # 获取聊天室
        chat_room = ChatRoom.objects.get(room_id=room_id)
        
        # 检查用户是否是聊天室的参与者
        participants = [chat_room.user1]
        if chat_room.user2:
            participants.append(chat_room.user2)
        
        if request.user not in participants:
            return JsonResponse({
                'success': False,
                'error': '您没有权限访问此聊天室'
            }, status=403, content_type='application/json', headers=response_headers)
        
        # 获取聊天室中的在线用户
        online_users = []
        for user in [chat_room.user1, chat_room.user2]:
            if user:
                online_status = UserOnlineStatus.objects.filter(user=user).first()
                if online_status and online_status.status == 'online':
                    online_users.append({
                        'username': user.username,
                        'last_seen': online_status.last_seen.isoformat(),
                        'is_online': True
                    })
                else:
                    online_users.append({
                        'username': user.username,
                        'last_seen': None,
                        'is_online': False
                    })
        
        return JsonResponse({
            'success': True,
            'online_users': online_users,
            'room_id': room_id
        }, content_type='application/json', headers=response_headers)
        
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '聊天室不存在'
        }, status=404, content_type='application/json', headers=response_headers)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取在线用户失败: {str(e)}'
        }, status=500, content_type='application/json', headers=response_headers)


def export_diary_data(request, data):
    """导出日记数据"""
    try:
        import csv
        from io import StringIO
        from django.http import HttpResponse
        
        export_type = data.get('type', 'diary')  # diary, goals, all
        date_from = data.get('date_from', '')
        date_to = data.get('date_to', '')
        
        # 创建CSV数据
        output = StringIO()
        writer = csv.writer(output)
        
        if export_type in ['diary', 'all']:
            # 导出日记数据
            diaries = LifeDiaryEntry.objects.filter(user=request.user)
            
            if date_from:
                try:
                    from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                    diaries = diaries.filter(date__gte=from_date)
                except ValueError:
                    return JsonResponse({'success': False, 'error': '开始日期格式无效'}, content_type='application/json')
            
            if date_to:
                try:
                    to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                    diaries = diaries.filter(date__lte=to_date)
                except ValueError:
                    return JsonResponse({'success': False, 'error': '结束日期格式无效'}, content_type='application/json')
            
            diaries = diaries.order_by('-date')
            
            # 写入日记CSV
            writer.writerow(['日期', '标题', '内容', '心情', '心情备注', '标签', '创建时间'])
            for diary in diaries:
                writer.writerow([
                    diary.date.strftime('%Y-%m-%d'),
                    diary.title,
                    diary.content,
                    diary.get_mood_display(),
                    diary.mood_note or '',
                    ', '.join(diary.tags) if diary.tags else '',
                    diary.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        if export_type in ['goals', 'all']:
            # 导出目标数据
            goals = LifeGoal.objects.filter(user=request.user).order_by('-created_at')
            
            if export_type == 'all':
                writer.writerow([])  # 空行分隔
                writer.writerow(['=== 生活目标数据 ==='])
            
            writer.writerow(['目标标题', '描述', '类别', '类型', '状态', '进度', '优先级', '难度', '开始日期', '目标日期', '标签', '创建时间'])
            for goal in goals:
                writer.writerow([
                    goal.title,
                    goal.description or '',
                    goal.get_category_display(),
                    goal.get_goal_type_display(),
                    goal.get_status_display(),
                    f'{goal.progress}%',
                    goal.priority,
                    goal.get_difficulty_display(),
                    goal.start_date.strftime('%Y-%m-%d') if goal.start_date else '',
                    goal.target_date.strftime('%Y-%m-%d') if goal.target_date else '',
                    ', '.join(goal.tags) if goal.tags else '',
                    goal.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        # 生成文件名
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'life_diary_export_{export_type}_{timestamp}.csv'
        
        # 创建HTTP响应
        response = HttpResponse(
            output.getvalue(),
            content_type='text/csv; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'导出失败: {str(e)}'})

@login_required
def douyin_analyzer(request):
    """抖音视频分析页面"""
    return render(request, 'tools/douyin_analyzer.html')

@csrf_exempt
@require_http_methods(["POST"])
def douyin_analysis_api(request):
    """抖音视频分析API"""
    try:
        data = json.loads(request.body)
        up主_url = data.get('up主_url', '').strip()
        
        if not up主_url:
            return JsonResponse({
                'success': False,
                'error': '请输入UP主主页URL'
            }, content_type='application/json')
        
        # 验证URL格式 - 支持多种抖音URL格式
        valid_domains = ['douyin.com', 'v.douyin.com']
        if not any(domain in up主_url for domain in valid_domains):
            return JsonResponse({
                'success': False,
                'error': '请输入有效的抖音URL（支持v.douyin.com短链接和douyin.com主页链接）'
            }, content_type='application/json')
        
        # 导入分析服务
        from .services.douyin_analyzer import DouyinAnalyzer
        
        # 开始分析
        analyzer = DouyinAnalyzer()
        result = analyzer.analyze_up主(up主_url, request.user.id)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'analysis_id': result['analysis_id'],
                'message': result['message']
            }, content_type='application/json')
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, content_type='application/json')
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'处理请求时出错: {str(e)}'
        }, content_type='application/json')

@csrf_exempt
@require_http_methods(["GET"])
def get_douyin_analysis_api(request):
    """获取抖音分析结果API"""
    try:
        analysis_id = request.GET.get('analysis_id')
        
        if not analysis_id:
            return JsonResponse({
                'success': False,
                'error': '缺少分析ID'
            }, content_type='application/json')
        
        from .models import DouyinVideoAnalysis, DouyinVideo
        
        analysis = DouyinVideoAnalysis.objects.get(id=analysis_id, user=request.user)
        videos = DouyinVideo.objects.filter(analysis=analysis).order_by('-likes')[:10]
        
        # 构建响应数据
        analysis_data = {
            'id': analysis.id,
            'up主_name': analysis.up主_name,
            'up主_url': analysis.up主_url,
            'analysis_status': analysis.analysis_status,
            'progress_percentage': analysis.get_progress_percentage(),
            'video_count': analysis.video_count,
            'total_likes': analysis.total_likes,
            'total_comments': analysis.total_comments,
            'total_shares': analysis.total_shares,
            'follower_count': analysis.follower_count,
            'content_themes': analysis.content_themes,
            'video_tags': analysis.video_tags,
            'popular_videos': analysis.popular_videos,
            'posting_frequency': analysis.posting_frequency,
            'screenshots': analysis.screenshots,
            'analysis_summary': analysis.analysis_summary,
            'product_preview': analysis.product_preview,
            'created_at': analysis.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'completed_at': analysis.completed_at.strftime('%Y-%m-%d %H:%M:%S') if analysis.completed_at else None,
            'videos': []
        }
        
        for video in videos:
            analysis_data['videos'].append({
                'id': video.id,
                'title': video.title,
                'description': video.description,
                'likes': video.likes,
                'comments': video.comments,
                'shares': video.shares,
                'views': video.views,
                'tags': video.tags,
                'theme': video.theme,
                'duration': video.duration,
                'thumbnail_url': video.thumbnail_url,
                'screenshot_urls': video.screenshot_urls,
                'engagement_rate': video.get_engagement_rate(),
                'published_at': video.published_at.strftime('%Y-%m-%d') if video.published_at else None
            })
        
        return JsonResponse({
            'success': True,
            'analysis': analysis_data
        }, content_type='application/json')
        
    except DouyinVideoAnalysis.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '分析记录不存在'
        }, content_type='application/json')
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取分析结果时出错: {str(e)}'
        }, content_type='application/json')

@csrf_exempt
@require_http_methods(["POST"])
def generate_product_preview_api(request):
    """生成产品功能预览API"""
    try:
        data = json.loads(request.body)
        analysis_id = data.get('analysis_id')
        
        if not analysis_id:
            return JsonResponse({
                'success': False,
                'error': '缺少分析ID'
            }, content_type='application/json')
        
        # 导入分析服务
        from .services.douyin_analyzer import DouyinAnalyzer
        
        # 生成产品预览
        analyzer = DouyinAnalyzer()
        result = analyzer.generate_product_preview(analysis_id)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'product_preview': result['product_preview']
            }, content_type='application/json')
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, content_type='application/json')
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'生成产品预览时出错: {str(e)}'
        }, content_type='application/json')

@csrf_exempt
@require_http_methods(["GET"])
def get_douyin_analysis_list_api(request):
    """获取抖音分析列表API"""
    try:
        from .models import DouyinVideoAnalysis
        
        analyses = DouyinVideoAnalysis.objects.filter(user=request.user).order_by('-created_at')
        
        analysis_list = []
        for analysis in analyses:
            analysis_list.append({
                'id': analysis.id,
                'up主_name': analysis.up主_name,
                'up主_url': analysis.up主_url,
                'analysis_status': analysis.analysis_status,
                'progress_percentage': analysis.get_progress_percentage(),
                'video_count': analysis.video_count,
                'follower_count': analysis.follower_count,
                'created_at': analysis.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'completed_at': analysis.completed_at.strftime('%Y-%m-%d %H:%M:%S') if analysis.completed_at else None
            })
        
        return JsonResponse({
            'success': True,
            'analyses': analysis_list
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取分析列表时出错: {str(e)}'
        }, content_type='application/json')



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def record_mode_click_api(request):
    """记录用户模式点击次数的API"""
    try:
        data = json.loads(request.body)
        mode = data.get('mode')
        
        if not mode:
            return JsonResponse({
                'success': False, 
                'error': '模式参数不能为空'
            })
        
        # 验证模式是否有效
        valid_modes = ['work', 'life', 'training', 'emo']
        if mode not in valid_modes:
            return JsonResponse({
                'success': False, 
                'error': '无效的模式参数'
            })
        
        # 导入用户模型
        from apps.users.models import UserModePreference
        
        # 记录模式点击
        success = UserModePreference.record_mode_click(request.user, mode)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'成功记录{mode}模式点击'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '记录模式点击失败'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_user_preferred_mode_api(request):
    """获取用户最偏好模式的API"""
    try:
        # 导入用户模型
        from apps.users.models import UserModePreference
        
        # 获取用户最偏好的模式
        preferred_mode = UserModePreference.get_user_preferred_mode(request.user)
        
        # 获取用户所有模式的点击统计
        mode_stats = []
        for mode in ['work', 'life', 'training', 'emo']:
            try:
                preference = UserModePreference.objects.get(user=request.user, mode=mode)
                mode_stats.append({
                    'mode': mode,
                    'click_count': preference.click_count,
                    'last_click_time': preference.last_click_time.isoformat() if preference.last_click_time else None
                })
            except UserModePreference.DoesNotExist:
                mode_stats.append({
                    'mode': mode,
                    'click_count': 0,
                    'last_click_time': None
                })
        
        return JsonResponse({
            'success': True,
            'preferred_mode': preferred_mode,
            'mode_stats': mode_stats
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })

@login_required
def triple_awakening_dashboard(request):
    """三重觉醒仪表盘"""
    service = TripleAwakeningService()
    
    # 获取用户数据
    workout_data = service.get_workout_dashboard_data(request.user)
    ai_dependency_data = service.get_ai_dependency_data(request.user)
    pain_currency_data = service.get_pain_currency_data(request.user)
    daily_challenge = service.get_daily_challenge(request.user)
    
    context = {
        'workout_data': workout_data,
        'ai_dependency_data': ai_dependency_data,
        'pain_currency_data': pain_currency_data,
        'daily_challenge': daily_challenge,
    }
    
    return render(request, 'tools/triple_awakening_dashboard.html', context)


@login_required
def create_fitness_workout_api(request):
    """创建健身训练API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            service = TripleAwakeningService()
            
            workout = service.create_fitness_workout(request.user, data)
            
            return JsonResponse({
                'success': True,
                'workout_id': workout.id,
                'message': '健身训练记录创建成功'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'创建失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '只支持POST请求'})


@login_required
def create_code_workout_api(request):
    """创建代码训练API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            service = TripleAwakeningService()
            
            workout = service.create_code_workout(request.user, data)
            
            return JsonResponse({
                'success': True,
                'workout_id': workout.id,
                'message': '代码训练记录创建成功'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'创建失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '只支持POST请求'})


@login_required
def complete_daily_task_api(request):
    """完成每日任务API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            
            if not task_id:
                return JsonResponse({
                    'success': False,
                    'message': '缺少任务ID'
                })
            
            service = TripleAwakeningService()
            result = service.complete_task(request.user, task_id)
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'操作失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '只支持POST请求'})


@login_required
def get_workout_dashboard_api(request):
    """获取训练仪表盘数据API"""
    try:
        service = TripleAwakeningService()
        data = service.get_workout_dashboard_data(request.user)
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取数据失败: {str(e)}'
        })


@login_required
def get_ai_dependency_api(request):
    """获取AI依赖度数据API"""
    try:
        service = TripleAwakeningService()
        data = service.get_ai_dependency_data(request.user)
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取数据失败: {str(e)}'
        })


@login_required
def get_pain_currency_api(request):
    """获取痛苦货币数据API"""
    try:
        service = TripleAwakeningService()
        data = service.get_pain_currency_data(request.user)
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取数据失败: {str(e)}'
        })


@login_required
def record_exhaustion_audio_api(request):
    """记录力竭音频API"""
    if request.method == 'POST':
        try:
            # 获取音频数据
            audio_file = request.FILES.get('audio')
            workout_session_id = request.POST.get('workout_session_id')
            
            if not audio_file or not workout_session_id:
                return JsonResponse({
                    'success': False,
                    'message': '缺少音频文件或训练会话ID'
                })
            
            # 读取音频数据
            audio_data = audio_file.read()
            
            # 处理音频
            processor = WorkoutAudioProcessor()
            audio_analysis = processor.process_exhaustion_audio(audio_data)
            
            # 生成CSS动画
            css_animation = processor.generate_css_animation(audio_analysis['intensity'])
            
            # 记录音频
            service = TripleAwakeningService()
            audio_url = service.record_audio_exhaustion(
                request.user, 
                audio_data, 
                int(workout_session_id)
            )
            
            return JsonResponse({
                'success': True,
                'audio_url': audio_url,
                'analysis': audio_analysis,
                'css_animation': css_animation
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'处理失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '只支持POST请求'})


@login_required
def create_exhaustion_proof_api(request):
    """创建力竭证明API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            proof_type = data.get('proof_type', 'fitness')
            workout_session_id = data.get('workout_session_id')
            
            service = TripleAwakeningService()
            
            # 获取训练会话
            if proof_type == 'fitness':
                workout_session = FitnessWorkoutSession.objects.get(
                    id=workout_session_id, 
                    user=request.user
                )
            else:
                workout_session = CodeWorkoutSession.objects.get(
                    id=workout_session_id, 
                    user=request.user
                )
            
            # 创建力竭证明
            proof = service._create_exhaustion_proof(
                request.user, 
                proof_type, 
                workout_session
            )
            
            # 生成推特内容
            tweet_content = service.generate_exhaustion_tweet(request.user, proof_type)
            
            return JsonResponse({
                'success': True,
                'proof_id': proof.id,
                'tweet_content': tweet_content,
                'nft_metadata': proof.nft_metadata
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'创建失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '只支持POST请求'})


@login_required
def create_copilot_collaboration_api(request):
    """创建AI协作声明API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            service = TripleAwakeningService()
            
            collaboration = service.create_copilot_collaboration(request.user, data)
            
            return JsonResponse({
                'success': True,
                'collaboration_id': collaboration.id,
                'message': 'AI协作声明创建成功'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'创建失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '只支持POST请求'})


@login_required
def copilot_page(request):
    """AI协作声明页面"""
    service = TripleAwakeningService()
    
    # 获取用户的协作记录
    collaborations = CoPilotCollaboration.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'collaborations': collaborations
    }
    
    return render(request, 'tools/copilot_page.html', context)

@login_required
def desire_dashboard(request):
    """欲望仪表盘页面"""
    service = DesireDashboardService()
    data = service.get_dashboard_data(request.user)
    
    context = {
        'dashboard_data': data,
        'desire_progress': service.get_desire_progress(request.user),
        'fulfillment_history': service.get_fulfillment_history(request.user)
    }
    
    return render(request, 'tools/desire_dashboard.html', context)


@login_required
def get_desire_dashboard_api(request):
    """获取欲望仪表盘数据API"""
    try:
        service = DesireDashboardService()
        data = service.get_dashboard_data(request.user)
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取数据失败: {str(e)}'
        })


@login_required
def add_desire_api(request):
    """添加欲望API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            service = DesireDashboardService()
            
            desire = service.add_desire(request.user, data)
            
            return JsonResponse({
                'success': True,
                'desire_id': desire.id,
                'message': '欲望添加成功'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'添加失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '只支持POST请求'})


@login_required
def check_desire_fulfillment_api(request):
    """检查欲望满足API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_type = data.get('task_type')
            task_details = data.get('task_details')
            
            if not task_type or not task_details:
                return JsonResponse({
                    'success': False,
                    'message': '缺少任务类型或详情'
                })
            
            service = DesireDashboardService()
            fulfilled_desires = service.check_desire_fulfillment(request.user, task_type, task_details)
            
            if fulfilled_desires:
                return JsonResponse({
                    'success': True,
                    'fulfilled_desires': [
                        {
                            'desire_title': item['desire'].title,
                            'fulfillment_id': item['fulfillment'].id,
                            'ai_prompt': item['fulfillment'].ai_prompt
                        }
                        for item in fulfilled_desires
                    ],
                    'message': f'恭喜！满足了 {len(fulfilled_desires)} 个欲望！'
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': '继续努力，还没有满足的欲望'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'检查失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '只支持POST请求'})


@login_required
def generate_ai_image_api(request):
    """生成AI图片API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            fulfillment_id = data.get('fulfillment_id')
            
            if not fulfillment_id:
                return JsonResponse({
                    'success': False,
                    'message': '缺少兑现记录ID'
                })
            
            service = DesireDashboardService()
            image_url = service.generate_ai_image(fulfillment_id)
            
            return JsonResponse({
                'success': True,
                'image_url': image_url,
                'message': 'AI图片生成成功！'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'生成失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '只支持POST请求'})


@login_required
def get_desire_progress_api(request):
    """获取欲望进度API"""
    try:
        service = DesireDashboardService()
        progress = service.get_desire_progress(request.user)
        
        return JsonResponse({
            'success': True,
            'data': progress
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取进度失败: {str(e)}'
        })


@login_required
def get_fulfillment_history_api(request):
    """获取兑现历史API"""
    try:
        service = DesireDashboardService()
        history = service.get_fulfillment_history(request.user)
        
        return JsonResponse({
            'success': True,
            'data': history
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取历史失败: {str(e)}'
        })


# VanityOS 欲望驱动的开发者激励系统视图

def vanity_os_dashboard(request):
    """VanityOS 主仪表盘页面 - 里世界入口（公开访问）"""
    return render(request, 'tools/vanity_os_dashboard.html')


@login_required
def vanity_rewards(request):
    """罪恶积分系统页面"""
    return render(request, 'tools/vanity_rewards.html')


@login_required
def sponsor_hall_of_fame(request):
    """金主荣耀墙页面"""
    return render(request, 'tools/sponsor_hall_of_fame.html')


@login_required
def based_dev_avatar(request):
    """反程序员形象生成器页面"""
    return render(request, 'tools/based_dev_avatar.html')


@login_required
def vanity_todo_list(request):
    """欲望驱动待办清单页面"""
    return render(request, 'tools/vanity_todo_list.html')




# VanityOS API 视图

@csrf_exempt
@require_http_methods(["GET"])
def get_vanity_wealth_api(request):
    """获取虚拟财富API（公开访问）"""
    try:
        # 如果没有登录用户，返回演示数据
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': True,
                'virtual_wealth': 1250.50,
                'code_lines': 125050,
                'page_views': 50000,
                'donations': 100.00,
                'car_progress': 0.25,  # 玛莎拉蒂进度
                'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M')
            })
        
        user = request.user
        wealth, created = VanityWealth.objects.get_or_create(user=user)
        
        # 计算虚拟财富
        wealth.calculate_wealth()
        wealth.save()
        
        return JsonResponse({
            'success': True,
            'virtual_wealth': float(wealth.virtual_wealth),
            'code_lines': wealth.code_lines,
            'page_views': wealth.page_views,
            'donations': float(wealth.donations),
            'car_progress': min((float(wealth.virtual_wealth) / 500000) * 100, 100),  # 玛莎拉蒂进度
            'last_updated': wealth.last_updated.strftime('%Y-%m-%d %H:%M')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
def add_sin_points_api(request):
    """添加罪恶积分API（公开访问）"""
    try:
        data = json.loads(request.body)
        action_type = data.get('action_type')
        points = data.get('points', 0)
        metadata = data.get('metadata', {})
        
        if not action_type:
            return JsonResponse({
                'success': False,
                'error': '行为类型不能为空'
            })
        
        # 如果没有登录用户，返回演示响应
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': True,
                'points_earned': points,
                'total_points': 150,
                'virtual_wealth': 1350.50,
                'message': '演示模式：积分已记录'
            })
        
        user = request.user
        
        # 创建罪恶积分记录
        sin_points = SinPoints.objects.create(
            user=user,
            action_type=action_type,
            points_earned=points,
            metadata=metadata
        )
        
        # 更新虚拟财富
        wealth, created = VanityWealth.objects.get_or_create(user=user)
        if action_type == 'code_line':
            wealth.code_lines += metadata.get('lines', 1)
        elif action_type == 'donation':
            wealth.donations += metadata.get('amount', 0)
        
        wealth.calculate_wealth()
        wealth.save()
        
        return JsonResponse({
            'success': True,
            'points_earned': points,
            'total_points': SinPoints.objects.filter(user=user).aggregate(
                total=models.Sum('points_earned')
            )['total'] or 0,
            'virtual_wealth': float(wealth.virtual_wealth)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_sponsors_api(request):
    """获取赞助者列表API"""
    try:
        sponsors = Sponsor.objects.all().order_by('-amount', '-created_at')[:20]
        
        sponsors_data = []
        for sponsor in sponsors:
            sponsors_data.append({
                'id': sponsor.id,
                'name': "匿名土豪" if sponsor.is_anonymous else sponsor.name,
                'amount': float(sponsor.amount),
                'message': sponsor.message,
                'effect': sponsor.effect,
                'created_at': sponsor.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'sponsors': sponsors_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_sponsor_api(request):
    """添加赞助者API"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '匿名土豪')
        amount = data.get('amount', 0)
        message = data.get('message', '')
        is_anonymous = data.get('is_anonymous', False)
        
        if amount <= 0:
            return JsonResponse({
                'success': False,
                'error': '赞助金额必须大于0'
            })
        
        # 根据金额确定特效类型
        if amount >= 1000:
            effect = 'diamond-sparkle'
        elif amount >= 500:
            effect = 'platinum-glow'
        elif amount >= 100:
            effect = 'golden-bling'
        else:
            effect = 'silver-shine'
        
        sponsor = Sponsor.objects.create(
            name=name,
            amount=amount,
            message=message,
            effect=effect,
            is_anonymous=is_anonymous
        )
        
        # 更新用户虚拟财富
        user = request.user
        wealth, created = VanityWealth.objects.get_or_create(user=user)
        wealth.donations += amount
        wealth.calculate_wealth()
        wealth.save()
        
        return JsonResponse({
            'success': True,
            'sponsor_id': sponsor.id,
            'effect': effect
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_vanity_tasks_api(request):
    """获取欲望任务列表API"""
    try:
        user = request.user
        tasks = VanityTask.objects.filter(user=user, is_completed=False).order_by('-created_at')
        
        tasks_data = []
        for task in tasks:
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'task_type': task.get_task_type_display(),
                'difficulty': task.difficulty,
                'reward_value': task.reward_value,
                'reward_description': task.reward_description,
                'created_at': task.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'tasks': tasks_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_vanity_task_api(request):
    """添加欲望任务API"""
    try:
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description', '')
        task_type = data.get('task_type')
        difficulty = data.get('difficulty', 1)
        
        if not title or not task_type:
            return JsonResponse({
                'success': False,
                'error': '任务标题和类型不能为空'
            })
        
        user = request.user
        
        # 根据难度生成奖励描述
        reward_descriptions = {
            1: '虚拟咖啡券',
            2: '星巴克虚拟券',
            3: '虚拟劳力士+3%豪车进度',
            4: '米其林虚拟体验',
            5: '虚拟游艇体验',
            6: '虚拟私人飞机',
            7: '虚拟岛屿',
            8: '虚拟太空旅行',
            9: '虚拟时间机器',
            10: '虚拟平行宇宙'
        }
        
        task = VanityTask.objects.create(
            user=user,
            title=title,
            description=description,
            task_type=task_type,
            difficulty=difficulty,
            reward_description=reward_descriptions.get(difficulty, '神秘奖励')
        )
        
        # 计算奖励价值
        task.calculate_reward()
        task.save()
        
        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'reward_value': task.reward_value
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def complete_vanity_task_api(request):
    """完成欲望任务API"""
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        
        if not task_id:
            return JsonResponse({
                'success': False,
                'error': '任务ID不能为空'
            })
        
        user = request.user
        task = VanityTask.objects.get(id=task_id, user=user, is_completed=False)
        
        # 标记任务完成
        task.is_completed = True
        task.completed_at = timezone.now()
        task.save()
        
        # 添加罪恶积分
        sin_points = SinPoints.objects.create(
            user=user,
            action_type='deep_work',
            points_earned=task.reward_value,
            metadata={'task_id': task_id, 'task_title': task.title}
        )
        
        # 更新虚拟财富
        wealth, created = VanityWealth.objects.get_or_create(user=user)
        wealth.code_lines += task.difficulty * 10  # 根据难度增加代码行数
        wealth.calculate_wealth()
        wealth.save()
        
        return JsonResponse({
            'success': True,
            'points_earned': task.reward_value,
            'reward_description': task.reward_description,
            'virtual_wealth': float(wealth.virtual_wealth)
        })
    except VanityTask.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '任务不存在或已完成'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_based_dev_avatar_api(request):
    """创建反程序员形象API"""
    try:
        data = json.loads(request.body)
        code_snippet = data.get('code_snippet')
        caption = data.get('caption')
        
        if not code_snippet or not caption:
            return JsonResponse({
                'success': False,
                'error': '代码片段和配文不能为空'
            })
        
        user = request.user
        
        # 这里应该处理图片上传，暂时使用默认图片
        avatar = BasedDevAvatar.objects.create(
            user=user,
            code_snippet=code_snippet,
            caption=caption
        )
        
        return JsonResponse({
            'success': True,
            'avatar_id': avatar.id,
            'caption': caption
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def send_image_api(request, room_id):
    """发送图片消息API"""
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    try:
        # 获取聊天室
        chat_room = ChatRoom.objects.get(room_id=room_id)
        
        # 检查聊天室状态
        if chat_room.status == 'ended':
            return JsonResponse({
                'success': False,
                'error': '聊天室已结束，无法发送消息',
                'room_ended': True
            }, status=410, content_type='application/json', headers=response_headers)
        
        # 检查用户是否是聊天室的参与者
        if request.user not in [chat_room.user1, chat_room.user2]:
            return JsonResponse({
                'success': False,
                'error': '您没有权限在此聊天室发送消息'
            }, status=403, content_type='application/json', headers=response_headers)
        
        # 获取上传的图片
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '请选择要发送的图片'
            }, status=400, content_type='application/json', headers=response_headers)
        
        image_file = request.FILES['image']
        
        # 检查文件大小（5MB限制）
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': '图片大小不能超过5MB'
            }, status=400, content_type='application/json', headers=response_headers)
        
        # 检查文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'error': '只支持JPEG、PNG、GIF、WebP格式的图片'
            }, status=400, content_type='application/json', headers=response_headers)
        
        # 处理图片（压缩和调整大小）
        try:
            img = Image.open(image_file)
            
            # 转换为RGB模式（如果是RGBA）
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # 调整图片大小（最大宽度800px）
            if img.width > 800:
                ratio = 800 / img.width
                new_size = (800, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 保存处理后的图片
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # 生成文件名
            filename = f"chat_images/{uuid.uuid4()}.jpg"
            
            # 创建消息
            message = ChatMessage.objects.create(
                room=chat_room,
                sender=request.user,
                message_type='image',
                content='图片消息',
                file_url=filename
            )
            
            # 保存文件到媒体目录
            media_path = os.path.join(settings.MEDIA_ROOT, filename)
            os.makedirs(os.path.dirname(media_path), exist_ok=True)
            
            with open(media_path, 'wb') as f:
                f.write(output.getvalue())
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'sender': message.sender.username,
                    'content': message.content,
                    'message_type': message.message_type,
                    'file_url': f'/media/{filename}',
                    'created_at': message.created_at.isoformat(),
                    'is_own': True
                },
                'upload_info': {
                    'file_name': image_file.name,
                    'file_size': f'{image_file.size / 1024:.1f}KB',
                    'file_type': '图片',
                    'upload_time': message.created_at.strftime('%H:%M:%S')
                }
            }, content_type='application/json', headers=response_headers)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'图片处理失败: {str(e)}'
            }, status=500, content_type='application/json', headers=response_headers)
            
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '聊天室不存在'
        }, status=404, content_type='application/json', headers=response_headers)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'发送图片失败: {str(e)}'
        }, status=500, content_type='application/json', headers=response_headers)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def send_audio_api(request, room_id):
    """发送语音消息API"""
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    try:
        # 获取聊天室
        chat_room = ChatRoom.objects.get(room_id=room_id)
        
        # 检查用户是否是聊天室的参与者
        if request.user not in [chat_room.user1, chat_room.user2]:
            return JsonResponse({
                'success': False,
                'error': '您没有权限在此聊天室发送消息'
            }, status=403, content_type='application/json', headers=response_headers)
        
        # 获取上传的音频文件
        if 'audio' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '请选择要发送的音频文件'
            }, status=400, content_type='application/json', headers=response_headers)
        
        audio_file = request.FILES['audio']
        
        # 检查文件大小（10MB限制）
        if audio_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': '音频文件大小不能超过10MB'
            }, status=400, content_type='application/json', headers=response_headers)
        
        # 检查文件类型
        allowed_types = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/ogg']
        if audio_file.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'error': '只支持WAV、MP3、OGG格式的音频文件'
            }, status=400, content_type='application/json', headers=response_headers)
        
        # 生成文件名
        filename = f"chat_audio/{uuid.uuid4()}.wav"
        
        # 创建消息
        message = ChatMessage.objects.create(
            room=chat_room,
            sender=request.user,
            message_type='audio',
            content='语音消息',
            file_url=filename
        )
        
        # 保存文件到媒体目录
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(os.path.dirname(media_path), exist_ok=True)
        
        with open(media_path, 'wb') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender': message.sender.username,
                'content': message.content,
                'message_type': message.message_type,
                'file_url': f'/media/{filename}',
                'created_at': message.created_at.isoformat(),
                'is_own': True
            },
            'upload_info': {
                'file_name': audio_file.name,
                'file_size': f'{audio_file.size / 1024:.1f}KB',
                'file_type': '音频',
                'upload_time': message.created_at.strftime('%H:%M:%S')
            }
        }, content_type='application/json', headers=response_headers)
        
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '聊天室不存在'
        }, status=404, content_type='application/json', headers=response_headers)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'发送语音失败: {str(e)}'
        }, status=500, content_type='application/json', headers=response_headers)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def send_file_api(request, room_id):
    """发送文件消息API"""
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    try:
        # 获取聊天室
        chat_room = ChatRoom.objects.get(room_id=room_id)
        
        # 检查用户是否是聊天室的参与者
        if request.user not in [chat_room.user1, chat_room.user2]:
            return JsonResponse({
                'success': False,
                'error': '您没有权限在此聊天室发送消息'
            }, status=403, content_type='application/json', headers=response_headers)
        
        # 获取上传的文件
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '请选择要发送的文件'
            }, status=400, content_type='application/json', headers=response_headers)
        
        file_obj = request.FILES['file']
        
        # 检查文件大小（10MB限制）
        if file_obj.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': '文件大小不能超过10MB'
            }, status=400, content_type='application/json', headers=response_headers)
        
        # 生成文件名
        original_filename = file_obj.name
        file_extension = os.path.splitext(original_filename)[1]
        filename = f"chat_files/{uuid.uuid4()}{file_extension}"
        
        # 创建消息
        message = ChatMessage.objects.create(
            room=chat_room,
            sender=request.user,
            message_type='file',
            content=original_filename,
            file_url=filename
        )
        
        # 保存文件到媒体目录
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(os.path.dirname(media_path), exist_ok=True)
        
        with open(media_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender': message.sender.username,
                'content': message.content,
                'message_type': message.message_type,
                'file_url': f'/media/{filename}',
                'created_at': message.created_at.isoformat(),
                'is_own': True
            },
            'upload_info': {
                'file_name': original_filename,
                'file_size': f'{file_obj.size / 1024:.1f}KB',
                'file_type': '文件',
                'upload_time': message.created_at.strftime('%H:%M:%S')
            }
        }, content_type='application/json', headers=response_headers)
        
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '聊天室不存在'
        }, status=404, content_type='application/json', headers=response_headers)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'发送文件失败: {str(e)}'
        }, status=500, content_type='application/json', headers=response_headers)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def send_video_api(request, room_id):
    """发送视频消息API"""
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    try:
        # 获取聊天室
        chat_room = ChatRoom.objects.get(room_id=room_id)
        
        # 检查用户是否是聊天室的参与者
        if request.user not in [chat_room.user1, chat_room.user2]:
            return JsonResponse({
                'success': False,
                'error': '您没有权限在此聊天室发送消息'
            }, status=403, content_type='application/json', headers=response_headers)
        
        # 获取上传的视频文件
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '请选择要发送的视频文件'
            }, status=400, content_type='application/json', headers=response_headers)
        
        video_file = request.FILES['file']
        
        # 检查文件大小（50MB限制）
        if video_file.size > 50 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': '视频文件大小不能超过50MB'
            }, status=400, content_type='application/json', headers=response_headers)
        
        # 检查文件类型
        allowed_types = ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv', 'video/webm']
        if video_file.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'error': '不支持的视频格式，请上传MP4、AVI、MOV、WMV、FLV或WebM格式'
            }, status=400, content_type='application/json', headers=response_headers)
        
        # 生成文件名
        original_filename = video_file.name
        file_extension = os.path.splitext(original_filename)[1]
        filename = f"chat_videos/{uuid.uuid4()}{file_extension}"
        
        # 创建消息
        message = ChatMessage.objects.create(
            room=chat_room,
            sender=request.user,
            message_type='video',
            content=original_filename,
            file_url=filename
        )
        
        # 保存视频文件到媒体目录
        media_path = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(os.path.dirname(media_path), exist_ok=True)
        
        with open(media_path, 'wb') as f:
            for chunk in video_file.chunks():
                f.write(chunk)
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender': message.sender.username,
                'content': message.content,
                'message_type': message.message_type,
                'file_url': f'/media/{filename}',
                'created_at': message.created_at.isoformat(),
                'is_own': True
            },
            'upload_info': {
                'file_name': original_filename,
                'file_size': f'{video_file.size / (1024*1024):.1f}MB',
                'file_type': '视频',
                'upload_time': message.created_at.strftime('%H:%M:%S')
            }
        }, content_type='application/json', headers=response_headers)
        
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '聊天室不存在'
        }, status=404, content_type='application/json', headers=response_headers)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'发送视频失败: {str(e)}'
        }, status=500, content_type='application/json', headers=response_headers)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_message_api(request, room_id, message_id):
    """删除消息API"""
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    try:
        # 获取聊天室
        chat_room = ChatRoom.objects.get(room_id=room_id)
        
        # 检查用户是否是聊天室的参与者
        if request.user not in [chat_room.user1, chat_room.user2]:
            return JsonResponse({
                'success': False,
                'error': '您没有权限在此聊天室操作'
            }, status=403, content_type='application/json', headers=response_headers)
        
        # 获取消息
        message = ChatMessage.objects.get(id=message_id, room=chat_room)
        
        # 检查是否是消息发送者
        if message.sender != request.user:
            return JsonResponse({
                'success': False,
                'error': '只能删除自己发送的消息'
            }, status=403, content_type='application/json', headers=response_headers)
        
        # 检查消息时间（只能删除5分钟内的消息）
        time_diff = timezone.now() - message.created_at
        if time_diff.total_seconds() > 300:  # 5分钟
            return JsonResponse({
                'success': False,
                'error': '只能删除5分钟内的消息'
            }, status=400, content_type='application/json', headers=response_headers)
        
        # 删除消息
        message.delete()
        
        return JsonResponse({
            'success': True,
            'message': '消息已删除'
        }, content_type='application/json', headers=response_headers)
        
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '聊天室不存在'
        }, status=404, content_type='application/json', headers=response_headers)
    except ChatMessage.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '消息不存在'
        }, status=404, content_type='application/json', headers=response_headers)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'删除消息失败: {str(e)}'
        }, status=500, content_type='application/json', headers=response_headers)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def mark_messages_read_api(request, room_id):
    """标记消息为已读API"""
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    try:
        # 获取聊天室
        chat_room = ChatRoom.objects.get(room_id=room_id)
        
        # 检查聊天室状态
        if chat_room.status == 'ended':
            return JsonResponse({
                'success': False,
                'error': '聊天室已结束，无法标记已读',
                'room_ended': True
            }, status=410, content_type='application/json', headers=response_headers)
        
        # 检查用户是否是聊天室的参与者
        if request.user not in [chat_room.user1, chat_room.user2]:
            return JsonResponse({
                'success': False,
                'error': '您没有权限在此聊天室操作'
            }, status=403, content_type='application/json', headers=response_headers)
        
        # 标记该用户收到的所有未读消息为已读
        # 只标记其他人发送给当前用户的消息
        other_user = chat_room.user2 if request.user == chat_room.user1 else chat_room.user1
        unread_messages = ChatMessage.objects.filter(
            room=chat_room,
            sender=other_user,  # 只标记对方发送的消息
            is_read=False
        )
        
        count = unread_messages.update(is_read=True)
        
        return JsonResponse({
            'success': True,
            'marked_count': count
        }, content_type='application/json', headers=response_headers)
        
    except ChatRoom.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '聊天室不存在'
        }, status=404, content_type='application/json', headers=response_headers)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'标记已读失败: {str(e)}'
        }, status=500, content_type='application/json', headers=response_headers)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_based_dev_avatar_api(request):
    """获取反程序员形象API"""
    try:
        user = request.user
        avatars = BasedDevAvatar.objects.filter(user=user).order_by('-created_at')
        
        # 计算用户统计数据
        total_code_lines = sum(len(avatar.code_snippet.split('\n')) for avatar in avatars)
        total_likes = sum(avatar.likes_count for avatar in avatars)
        
        # 计算等级和经验值
        level = min(10, (total_code_lines // 1000) + 1)
        experience = total_code_lines % 1000
        
        # 获取等级称号
        level_titles = {
            1: '代码新手',
            2: '代码学徒',
            3: '代码工匠',
            4: '代码大师',
            5: '算法巫师',
            6: '调试专家',
            7: '架构师',
            8: '代码诗人',
            9: '编程哲学家',
            10: '代码之神'
        }
        
        avatars_data = []
        for avatar in avatars:
            avatars_data.append({
                'id': avatar.id,
                'code_snippet': avatar.code_snippet,
                'caption': avatar.caption,
                'likes_count': avatar.likes_count,
                'is_public': avatar.is_public,
                'created_at': avatar.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'user_stats': {
                'level': level,
                'experience': experience,
                'title': level_titles.get(level, '代码新手'),
                'total_code_lines': total_code_lines,
                'total_likes': total_likes,
                'total_avatars': avatars.count()
            },
            'avatars': avatars_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_based_dev_stats_api(request):
    """更新反程序员统计数据API"""
    try:
        data = json.loads(request.body)
        action_type = data.get('action_type')  # 'code_line', 'ai_rejection', 'bug_fix'
        value = data.get('value', 1)
        
        user = request.user
        
        # 这里可以添加更复杂的统计逻辑
        # 暂时返回成功响应
        return JsonResponse({
            'success': True,
            'message': f'成功记录{action_type}行为',
            'value': value
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def like_based_dev_avatar_api(request):
    """点赞反程序员形象API"""
    try:
        data = json.loads(request.body)
        avatar_id = data.get('avatar_id')
        
        if not avatar_id:
            return JsonResponse({
                'success': False,
                'error': '形象ID不能为空'
            })
        
        avatar = BasedDevAvatar.objects.get(id=avatar_id)
        avatar.likes_count += 1
        avatar.save()
        
        return JsonResponse({
            'success': True,
            'likes_count': avatar.likes_count
        })
    except BasedDevAvatar.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '形象不存在'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_based_dev_achievements_api(request):
    """获取反程序员成就API"""
    try:
        user = request.user
        avatars = BasedDevAvatar.objects.filter(user=user)
        
        # 计算成就
        total_code_lines = sum(len(avatar.code_snippet.split('\n')) for avatar in avatars)
        total_likes = sum(avatar.likes_count for avatar in avatars)
        total_avatars = avatars.count()
        
        achievements = []
        
        # 代码行数成就
        if total_code_lines >= 1000:
            achievements.append({
                'name': '代码工匠',
                'description': '手写1000行代码',
                'icon': '💻',
                'unlocked': True
            })
        elif total_code_lines >= 500:
            achievements.append({
                'name': '代码学徒',
                'description': '手写500行代码',
                'icon': '📝',
                'unlocked': True
            })
        
        # 点赞成就
        if total_likes >= 100:
            achievements.append({
                'name': '社区明星',
                'description': '获得100个点赞',
                'icon': '⭐',
                'unlocked': True
            })
        elif total_likes >= 50:
            achievements.append({
                'name': '受欢迎',
                'description': '获得50个点赞',
                'icon': '👍',
                'unlocked': True
            })
        
        # 形象数量成就
        if total_avatars >= 10:
            achievements.append({
                'name': '形象大师',
                'description': '创建10个反程序员形象',
                'icon': '🎭',
                'unlocked': True
            })
        elif total_avatars >= 5:
            achievements.append({
                'name': '形象创造者',
                'description': '创建5个反程序员形象',
                'icon': '🎨',
                'unlocked': True
            })
        
        return JsonResponse({
            'success': True,
            'achievements': achievements,
            'stats': {
                'total_code_lines': total_code_lines,
                'total_likes': total_likes,
                'total_avatars': total_avatars
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_desire_todos_api(request):
    """获取欲望代办列表API"""
    try:
        user = request.user
        category = request.GET.get('category', 'all')
        
        # 这里应该从数据库获取代办，暂时返回模拟数据
        todos_data = [
            {
                'id': 1,
                'title': '完成项目重构',
                'description': '重构现有代码架构，提高系统性能和可维护性',
                'category': 'work',
                'priority': 'high',
                'reward': '¥1,000',
                'is_completed': False,
                'created_at': '2024-01-15 10:30'
            },
            {
                'id': 2,
                'title': '学习新编程语言',
                'description': '学习Rust编程语言，掌握系统级编程技能',
                'category': 'personal',
                'priority': 'medium',
                'reward': '¥500',
                'is_completed': True,
                'created_at': '2024-01-10 14:20'
            },
            {
                'id': 3,
                'title': '健身30天',
                'description': '连续30天进行健身锻炼，改善身体状况',
                'category': 'health',
                'priority': 'medium',
                'reward': '买一双新跑鞋',
                'is_completed': False,
                'created_at': '2024-01-12 09:15'
            }
        ]
        
        # 按分类筛选
        if category != 'all':
            todos_data = [todo for todo in todos_data if todo['category'] == category]
        
        return JsonResponse({
            'success': True,
            'todos': todos_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_desire_todo_api(request):
    """添加欲望代办API"""
    try:
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description', '')
        category = data.get('category')
        priority = data.get('priority')
        reward = data.get('reward', '')
        
        if not title or not category or not priority:
            return JsonResponse({
                'success': False,
                'error': '标题、分类和优先级不能为空'
            })
        
        # 这里应该保存到数据库，暂时返回成功响应
        todo_id = int(time.time())  # 模拟ID
        
        return JsonResponse({
            'success': True,
            'todo_id': todo_id,
            'message': '欲望代办添加成功'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def complete_desire_todo_api(request):
    """完成欲望代办API"""
    try:
        data = json.loads(request.body)
        todo_id = data.get('todo_id')
        
        if not todo_id:
            return JsonResponse({
                'success': False,
                'error': '代办ID不能为空'
            })
        
        # 这里应该更新数据库，暂时返回成功响应
        return JsonResponse({
            'success': True,
            'message': '欲望代办完成！',
            'reward_unlocked': True
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_desire_todo_api(request):
    """删除欲望代办API"""
    try:
        data = json.loads(request.body)
        todo_id = data.get('todo_id')
        
        if not todo_id:
            return JsonResponse({
                'success': False,
                'error': '代办ID不能为空'
            })
        
        # 这里应该从数据库删除，暂时返回成功响应
        return JsonResponse({
            'success': True,
            'message': '欲望代办删除成功'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def edit_desire_todo_api(request):
    """编辑欲望代办API"""
    try:
        data = json.loads(request.body)
        todo_id = data.get('todo_id')
        title = data.get('title')
        description = data.get('description', '')
        category = data.get('category')
        priority = data.get('priority')
        reward = data.get('reward', '')
        
        if not todo_id or not title or not category or not priority:
            return JsonResponse({
                'success': False,
                'error': 'ID、标题、分类和优先级不能为空'
            })
        
        # 这里应该更新数据库，暂时返回成功响应
        return JsonResponse({
            'success': True,
            'message': '欲望代办编辑成功'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_desire_todo_stats_api(request):
    """获取欲望代办统计API"""
    try:
        # 这里应该从数据库获取统计数据，暂时返回模拟数据
        stats = {
            'total_todos': 12,
            'completed_todos': 8,
            'pending_todos': 4,
            'total_rewards': '¥2,450',
            'completion_rate': 67
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def travel_guide(request):
    """旅游攻略页面"""
    return render(request, 'tools/travel_guide.html')


@csrf_exempt
@require_http_methods(["GET"])
def check_local_travel_data_api(request):
    """检测本地旅游数据API"""
    try:
        destination = request.GET.get('destination', '').strip()
        
        if not destination:
            return JsonResponse({
                'has_local_data': False,
                'message': '请输入目的地'
            })
        
        # 检查是否有本地数据
        from .services.enhanced_travel_service_v2 import MultiAPITravelService
        
        try:
            service = MultiAPITravelService()
            has_local_data = destination in service.real_travel_data
            
            return JsonResponse({
                'has_local_data': has_local_data,
                'destination': destination,
                'message': f'{"有" if has_local_data else "没有"}本地数据'
            })
            
        except Exception as e:
            print(f"检测本地数据失败: {e}")
            return JsonResponse({
                'has_local_data': False,
                'message': '检测失败，默认显示标准模式'
            })
            
    except Exception as e:
        return JsonResponse({
            'has_local_data': False,
            'message': f'检测失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def travel_guide_api(request):
    """旅游攻略API - 优先使用本地数据，否则使用DeepSeek功能"""
    try:
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': '请先登录后再使用此功能'
            }, status=401)
        
        data = json.loads(request.body)
        destination = data.get('destination', '').strip()
        travel_style = data.get('travel_style', 'general')
        budget_min = data.get('budget_min', 3000)  # 预算最小值
        budget_max = data.get('budget_max', 8000)  # 预算最大值
        budget_amount = data.get('budget_amount', 5000)  # 新增具体预算金额（平均值）
        budget_range = data.get('budget_range', 'medium')  # 保留分类，用于兼容
        travel_duration = data.get('travel_duration', '3-5天')
        interests = data.get('interests', [])
        fast_mode = data.get('fast_mode', False)  # 新增快速模式选项
        
        # 后端预算范围校验
        validation_error = validate_budget_range(budget_min, budget_max)
        if validation_error:
            return JsonResponse({'error': validation_error}, status=400)
        
        if not destination:
            return JsonResponse({'error': '请输入目的地'}, status=400)
        
        # 生成旅游攻略内容
        try:
            # 使用新的多API服务 - 延迟创建实例以避免启动时的API调用
            from .services.enhanced_travel_service_v2 import MultiAPITravelService
            
            # 只在需要时创建服务实例
            service = None
            try:
                service = MultiAPITravelService()
                
                # 检查是否有本地数据
                has_local_data = destination in service.real_travel_data
                
                # 如果有本地数据，优先使用本地数据
                if has_local_data:
                    print(f"✅ {destination}有本地数据，使用本地数据生成攻略")
                    guide_content = service.get_travel_guide_with_local_data(
                        destination=destination,
                        travel_style=travel_style,
                        budget_min=budget_min,
                        budget_max=budget_max,
                        budget_amount=budget_amount,
                        budget_range=budget_range,
                        travel_duration=travel_duration,
                        interests=interests,
                        fast_mode=fast_mode
                    )
                else:
                    print(f"❌ {destination}没有本地数据，使用DeepSeek功能")
                    guide_content = service.get_travel_guide(
                        destination=destination,
                        travel_style=travel_style,
                        budget_min=budget_min,
                        budget_max=budget_max,
                        budget_amount=budget_amount,
                        budget_range=budget_range,
                        travel_duration=travel_duration,
                        interests=interests,
                        fast_mode=fast_mode
                    )
                    
            except Exception as service_error:
                # 如果服务创建失败，使用备用方案
                print(f"旅游服务创建失败，使用备用方案: {service_error}")
                guide_content = {
                    'must_visit_attractions': [],
                    'food_recommendations': [],
                    'transportation_guide': '暂无交通信息',
                    'hidden_gems': [],
                    'weather_info': {},
                    'best_time_to_visit': '全年适合',
                    'budget_estimate': {},
                    'travel_tips': ['请稍后重试'],
                    'detailed_guide': '服务暂时不可用，请稍后重试',
                    'daily_schedule': [],
                    'activity_timeline': [],
                    'cost_breakdown': {}
                }
            
            # 过滤掉TravelGuide模型中不存在的字段
            valid_fields = {
                'must_visit_attractions', 'food_recommendations', 'transportation_guide',
                'hidden_gems', 'weather_info', 'destination_info', 'currency_info', 'timezone_info',
                'best_time_to_visit', 'budget_estimate', 'travel_tips',
                'detailed_guide', 'daily_schedule', 'activity_timeline', 'cost_breakdown'
            }
            filtered_content = {k: v for k, v in guide_content.items() if k in valid_fields}
            
            # 保存到数据库
            travel_guide = TravelGuide.objects.create(
                user=request.user,
                destination=destination,
                travel_style=travel_style,
                budget_min=budget_min,
                budget_max=budget_max,
                budget_amount=budget_amount,
                budget_range=budget_range,
                travel_duration=travel_duration,
                interests=interests,
                **filtered_content
            )
            
            # 构建响应数据
            response_data = {
                'id': travel_guide.id,
                'destination': travel_guide.destination,
                'must_visit_attractions': travel_guide.must_visit_attractions,
                'food_recommendations': travel_guide.food_recommendations,
                'transportation_guide': travel_guide.transportation_guide,
                'hidden_gems': travel_guide.hidden_gems,
                'weather_info': travel_guide.weather_info,
                'destination_info': travel_guide.destination_info,
                'currency_info': travel_guide.currency_info,
                'timezone_info': travel_guide.timezone_info,
                'best_time_to_visit': travel_guide.best_time_to_visit,
                'budget_estimate': travel_guide.budget_estimate,
                'travel_tips': travel_guide.travel_tips,
                'detailed_guide': travel_guide.detailed_guide,
                'daily_schedule': travel_guide.daily_schedule,
                'activity_timeline': travel_guide.activity_timeline,
                'cost_breakdown': travel_guide.cost_breakdown,
                'created_at': travel_guide.created_at.strftime('%Y-%m-%d %H:%M'),
            }
            
            # 添加缓存和API信息
            if hasattr(guide_content, 'get'):
                response_data.update({
                    'is_cached': guide_content.get('is_cached', False),
                    'api_used': guide_content.get('api_used', 'unknown'),
                    'generation_time': guide_content.get('generation_time', 0),
                    'generation_mode': guide_content.get('generation_mode', 'standard'),
                    'data_quality_score': guide_content.get('data_quality_score', 0.0),
                    'usage_count': guide_content.get('usage_count', 0),
                    'cached_at': guide_content.get('cached_at'),
                    'expires_at': guide_content.get('expires_at'),
                    'data_source': 'local' if has_local_data else 'deepseek'
                })
            
            return JsonResponse({
                'success': True,
                'guide_id': travel_guide.id,
                'guide': response_data
            })
        except Exception as e:
            error_message = str(e)
            if "无法获取有效的旅游数据" in error_message or "API" in error_message:
                return JsonResponse({
                    'error': '服务暂时不可用，请稍后重试。错误详情：' + error_message
                }, status=503)  # 503 Service Unavailable
            else:
                return JsonResponse({
                    'error': '生成攻略失败：' + error_message
                }, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        print(f"生成旅游攻略失败: {str(e)}")
        return JsonResponse({'error': f'生成攻略失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_travel_guides_api(request):
    """获取用户的旅游攻略列表"""
    try:
        guides = TravelGuide.objects.filter(user=request.user).order_by('-created_at')
        guides_data = []
        
        for guide in guides:
            try:
                # 安全地获取计数，避免None值错误
                attractions_count = len(guide.must_visit_attractions) if guide.must_visit_attractions else 0
                food_count = len(guide.food_recommendations) if guide.food_recommendations else 0
                hidden_gems_count = len(guide.hidden_gems) if guide.hidden_gems else 0
                
                guides_data.append({
                    'id': guide.id,
                    'destination': guide.destination,
                    'travel_style': guide.travel_style,
                    'budget_range': guide.budget_range,
                    'travel_duration': guide.travel_duration,
                    'attractions_count': attractions_count,
                    'food_count': food_count,
                    'hidden_gems_count': hidden_gems_count,
                    'is_favorite': guide.is_favorite,
                    'created_at': guide.created_at.strftime('%Y-%m-%d %H:%M'),
                })
            except Exception as guide_error:
                print(f"处理攻略 {guide.id} 时出错: {str(guide_error)}")
                # 跳过有问题的攻略，继续处理其他攻略
                continue
        
        return JsonResponse({
            'success': True,
            'guides': guides_data
        })
        
    except Exception as e:
        print(f"获取旅游攻略列表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'获取攻略列表失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_travel_guide_detail_api(request, guide_id):
    """获取旅游攻略详情"""
    try:
        guide = TravelGuide.objects.get(id=guide_id, user=request.user)
        
        return JsonResponse({
            'success': True,
            'guide': {
                'id': guide.id,
                'destination': guide.destination,
                'must_visit_attractions': guide.must_visit_attractions,
                'food_recommendations': guide.food_recommendations,
                'transportation_guide': guide.transportation_guide,
                'hidden_gems': guide.hidden_gems,
                'weather_info': guide.weather_info,
                'best_time_to_visit': guide.best_time_to_visit,
                'budget_estimate': guide.budget_estimate,
                'travel_tips': guide.travel_tips,
                'travel_style': guide.travel_style,
                'budget_range': guide.budget_range,
                'travel_duration': guide.travel_duration,
                'interests': guide.interests,
                'is_favorite': guide.is_favorite,
                'created_at': guide.created_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
        
    except TravelGuide.DoesNotExist:
        return JsonResponse({'error': '攻略不存在'}, status=404)
    except Exception as e:
        print(f"获取旅游攻略详情失败: {str(e)}")
        return JsonResponse({'error': f'获取攻略详情失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def toggle_favorite_guide_api(request, guide_id):
    """切换攻略收藏状态"""
    try:
        guide = TravelGuide.objects.get(id=guide_id, user=request.user)
        guide.is_favorite = not guide.is_favorite
        guide.save()
        
        return JsonResponse({
            'success': True,
            'is_favorite': guide.is_favorite
        })
        
    except TravelGuide.DoesNotExist:
        return JsonResponse({'error': '攻略不存在'}, status=404)
    except Exception as e:
        print(f"切换收藏状态失败: {str(e)}")
        return JsonResponse({'error': f'操作失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_travel_guide_api(request, guide_id):
    """删除旅游攻略"""
    try:
        guide = TravelGuide.objects.get(id=guide_id, user=request.user)
        guide.delete()
        
        return JsonResponse({'success': True})
        
    except TravelGuide.DoesNotExist:
        return JsonResponse({'error': '攻略不存在'}, status=404)
    except Exception as e:
        print(f"删除旅游攻略失败: {str(e)}")
        return JsonResponse({'error': f'删除失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def export_travel_guide_api(request, guide_id):
    """导出旅游攻略为PDF"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # 检查guide_id是否有效
        if not guide_id or str(guide_id) == 'undefined':
            return JsonResponse({
                'success': False,
                'error': '无效的攻略ID'
            }, status=400)
        
        # 尝试获取攻略
        try:
            guide = TravelGuide.objects.get(id=guide_id, user=request.user)
        except TravelGuide.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '攻略不存在或您没有权限访问'
            }, status=404)
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': '攻略ID格式错误'
            }, status=400)
        
        # 格式化攻略内容
        formatted_content = format_travel_guide_for_export(guide)
        
        # 检查内容是否为空
        if not formatted_content or len(formatted_content.strip()) < 50:
            return JsonResponse({
                'success': False,
                'error': '攻略内容为空或数据不完整，请重新生成攻略'
            }, status=400)
        
        # 尝试使用多种PDF生成方式
        pdf_content = None
        
        # 直接返回格式化的文本内容，提供更好的用户体验
        logger.info("✅ 返回格式化的文本内容")
        return JsonResponse({
            'success': True,
            'message': '攻略转换成功！已导出为txt格式',
            'formatted_content': formatted_content,
            'format': 'txt',
            'filename': f"{guide.destination}_旅游攻略_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        })
        

        
    except Exception as e:
        logger.error(f"导出攻略失败: {e}")
        return JsonResponse({
            'success': False,
            'error': f'导出失败: {str(e)}'
        }, status=500)


def format_travel_guide_for_export(guide):
    """格式化旅游攻略用于导出 - 增强版"""
    content = []
    
    try:
        # 标题
        destination = getattr(guide, 'destination', '未知目的地')
        content.append(f"🗺️ {destination} 旅游攻略")
        content.append("=" * 60)
        content.append("")
        
        # 基本信息
        content.append("📋 基本信息")
        content.append("-" * 30)
        content.append(f"📍 目的地: {destination}")
        content.append(f"🎯 旅行风格: {getattr(guide, 'travel_style', '未指定')}")
        content.append(f"💰 预算范围: {getattr(guide, 'budget_range', '未指定')}")
        content.append(f"⏰ 旅行时长: {getattr(guide, 'travel_duration', '未指定')}")
        
        interests = getattr(guide, 'interests', [])
        if interests and isinstance(interests, list) and len(interests) > 0:
            content.append(f"🎨 兴趣偏好: {', '.join(interests)}")
        else:
            content.append("🎨 兴趣偏好: 无")
        content.append("")
        
        # 最佳旅行时间
        best_time = getattr(guide, 'best_time_to_visit', None)
        if best_time:
            content.append("📅 最佳旅行时间")
            content.append("-" * 30)
            content.append(str(best_time))
            content.append("")
        
        # 天气信息
        weather_info = getattr(guide, 'weather_info', None)
        if weather_info:
            content.append("🌤️ 天气信息")
            content.append("-" * 30)
            try:
                if isinstance(weather_info, dict):
                    for season, info in weather_info.items():
                        content.append(f"• {season}: {info}")
                else:
                    content.append(str(weather_info))
            except:
                content.append(str(weather_info))
            content.append("")
        
        # 必去景点
        attractions = getattr(guide, 'must_visit_attractions', None)
        if attractions:
            content.append("🎯 必去景点")
            content.append("-" * 30)
            try:
                if isinstance(attractions, list):
                    for i, attraction in enumerate(attractions, 1):
                        if isinstance(attraction, dict):
                            name = attraction.get('name', '')
                            description = attraction.get('description', '')
                            ticket_price = attraction.get('ticket_price', '')
                            open_time = attraction.get('open_time', '')
                            
                            content.append(f"{i}. {name}")
                            if description:
                                content.append(f"   描述: {description}")
                            if ticket_price:
                                content.append(f"   门票: {ticket_price}")
                            if open_time:
                                content.append(f"   开放时间: {open_time}")
                            content.append("")
                        else:
                            content.append(f"{i}. {str(attraction)}")
                else:
                    content.append(str(attractions))
            except Exception as e:
                content.append("景点数据解析错误")
            content.append("")
        
        # 美食推荐
        foods = getattr(guide, 'food_recommendations', None)
        if foods:
            content.append("🍜 美食推荐")
            content.append("-" * 30)
            try:
                if isinstance(foods, list):
                    for i, food in enumerate(foods, 1):
                        if isinstance(food, dict):
                            name = food.get('name', '')
                            specialty = food.get('specialty', '')
                            price_range = food.get('price_range', '')
                            recommendation = food.get('recommendation', '')
                            
                            content.append(f"{i}. {name}")
                            if specialty:
                                content.append(f"   特色: {specialty}")
                            if price_range:
                                content.append(f"   价格: {price_range}")
                            if recommendation:
                                content.append(f"   推荐理由: {recommendation}")
                            content.append("")
                        else:
                            content.append(f"{i}. {str(food)}")
                else:
                    content.append(str(foods))
            except Exception as e:
                content.append("美食数据解析错误")
            content.append("")
        
        # 每日行程
        daily_schedule = getattr(guide, 'daily_schedule', None)
        if daily_schedule:
            content.append("🚥 每日行程")
            content.append("-" * 30)
            try:
                if isinstance(daily_schedule, list):
                    for i, day_schedule in enumerate(daily_schedule, 1):
                        content.append(f"第{i}天:")
                        
                        if isinstance(day_schedule, dict):
                            # 早晨
                            morning = day_schedule.get('morning', [])
                            if morning:
                                content.append("   🌅 早晨:")
                                if isinstance(morning, list):
                                    for activity in morning:
                                        if isinstance(activity, dict):
                                            activity_name = activity.get('activity', '')
                                            location = activity.get('location', '')
                                            time = activity.get('time', '')
                                            cost = activity.get('cost', '')
                                            
                                            content.append(f"     • {activity_name}")
                                            if location:
                                                content.append(f"       地点: {location}")
                                            if time:
                                                content.append(f"       时间: {time}")
                                            if cost:
                                                content.append(f"       费用: {cost}")
                                        else:
                                            content.append(f"     • {str(activity)}")
                                else:
                                    content.append(f"     • {str(morning)}")
                            
                            # 下午
                            afternoon = day_schedule.get('afternoon', [])
                            if afternoon:
                                content.append("   ☀️ 下午:")
                                if isinstance(afternoon, list):
                                    for activity in afternoon:
                                        if isinstance(activity, dict):
                                            activity_name = activity.get('activity', '')
                                            location = activity.get('location', '')
                                            time = activity.get('time', '')
                                            cost = activity.get('cost', '')
                                            
                                            content.append(f"     • {activity_name}")
                                            if location:
                                                content.append(f"       地点: {location}")
                                            if time:
                                                content.append(f"       时间: {time}")
                                            if cost:
                                                content.append(f"       费用: {cost}")
                                        else:
                                            content.append(f"     • {str(activity)}")
                                else:
                                    content.append(f"     • {str(afternoon)}")
                            
                            # 晚上
                            evening = day_schedule.get('evening', [])
                            if evening:
                                content.append("   🌙 晚上:")
                                if isinstance(evening, list):
                                    for activity in evening:
                                        if isinstance(activity, dict):
                                            activity_name = activity.get('activity', '')
                                            location = activity.get('location', '')
                                            time = activity.get('time', '')
                                            cost = activity.get('cost', '')
                                            
                                            content.append(f"     • {activity_name}")
                                            if location:
                                                content.append(f"       地点: {location}")
                                            if time:
                                                content.append(f"       时间: {time}")
                                            if cost:
                                                content.append(f"       费用: {cost}")
                                        else:
                                            content.append(f"     • {str(activity)}")
                                else:
                                    content.append(f"     • {str(evening)}")
                        else:
                            content.append(f"   {str(day_schedule)}")
                        content.append("")
                else:
                    content.append(str(daily_schedule))
            except Exception as e:
                content.append("行程数据解析错误")
            content.append("")
        
        # 交通指南
        transport = getattr(guide, 'transportation_guide', None)
        if transport:
            content.append("🚗 交通指南")
            content.append("-" * 30)
            try:
                if isinstance(transport, dict):
                    for key, value in transport.items():
                        content.append(f"• {key}: {value}")
                else:
                    content.append(str(transport))
            except Exception as e:
                content.append("交通数据解析错误")
            content.append("")
        
        # 预算估算
        budget = getattr(guide, 'budget_estimate', None)
        if budget:
            content.append("💰 预算估算")
            content.append("-" * 30)
            try:
                if isinstance(budget, dict):
                    for budget_type, amount in budget.items():
                        content.append(f"• {budget_type}: {amount}")
                else:
                    content.append(str(budget))
            except Exception as e:
                content.append("预算数据解析错误")
            content.append("")
        
        # 费用明细
        cost_breakdown = getattr(guide, 'cost_breakdown', None)
        if cost_breakdown:
            content.append("💸 费用明细")
            content.append("-" * 30)
            try:
                if isinstance(cost_breakdown, dict):
                    total_cost = cost_breakdown.get('total_cost', 0)
                    content.append(f"总费用: ¥{total_cost}")
                    content.append("")
                    
                    for category, details in cost_breakdown.items():
                        if category != 'total_cost':
                            if isinstance(details, dict):
                                description = details.get('description', category)
                                cost = details.get('total_cost', 0)
                                daily_cost = details.get('daily_cost', 0)
                                
                                content.append(f"• {description}: ¥{cost}")
                                if daily_cost:
                                    content.append(f"  日均: ¥{daily_cost}")
                            else:
                                content.append(f"• {category}: {details}")
                else:
                    content.append(str(cost_breakdown))
            except Exception as e:
                content.append("费用数据解析错误")
            content.append("")
        
        # 隐藏玩法
        hidden_gems = getattr(guide, 'hidden_gems', None)
        if hidden_gems:
            content.append("💎 隐藏玩法")
            content.append("-" * 30)
            try:
                if isinstance(hidden_gems, list):
                    for i, gem in enumerate(hidden_gems, 1):
                        content.append(f"{i}. {str(gem)}")
                else:
                    content.append(str(hidden_gems))
            except Exception as e:
                content.append("隐藏玩法数据解析错误")
            content.append("")
        
        # 旅行贴士
        tips = getattr(guide, 'travel_tips', None)
        if tips:
            content.append("💡 旅行贴士")
            content.append("-" * 30)
            try:
                if isinstance(tips, list):
                    for i, tip in enumerate(tips, 1):
                        content.append(f"{i}. {str(tip)}")
                else:
                    content.append(str(tips))
            except Exception as e:
                content.append("贴士数据解析错误")
            content.append("")
        
        # 详细攻略
        detailed_guide = getattr(guide, 'detailed_guide', None)
        if detailed_guide:
            content.append("📖 详细攻略")
            content.append("-" * 30)
            content.append(str(detailed_guide))
            content.append("")
        
        # 生成时间
        content.append("=" * 60)
        content.append(f"📅 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        content.append("🎯 由 WanderAI 智能旅游攻略系统生成")
        
    except Exception as e:
        # 如果出现任何错误，返回基本信息
        content = [
            f"🗺️ {getattr(guide, 'destination', '未知目的地')} 旅游攻略",
            "=" * 60,
            "",
            "📋 基本信息",
            "-" * 30,
            f"📍 目的地: {getattr(guide, 'destination', '未知目的地')}",
            f"🎯 旅行风格: {getattr(guide, 'travel_style', '未指定')}",
            f"💰 预算范围: {getattr(guide, 'budget_range', '未指定')}",
            f"⏰ 旅行时长: {getattr(guide, 'travel_duration', '未指定')}",
            "",
            "⚠️ 数据解析出现错误，请重新生成攻略。",
            "",
            "=" * 60,
            f"📅 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
            "🎯 由 WanderAI 智能旅游攻略系统生成"
        ]
    
    return "\n".join(content)








def generate_travel_guide(destination, travel_style, budget_min, budget_max, budget_amount, budget_range, travel_duration, interests):
    """生成旅游攻略内容 - 使用DeepSeek API真实数据"""
    try:
        print(f"🔍 开始为{destination}生成DeepSeek真实旅游攻略...")
        
        # 使用真实数据旅游服务
        try:
            from .services.real_data_travel_service import RealDataTravelService
            real_data_service = RealDataTravelService()
            
            # 获取真实旅游攻略数据
            guide_data = real_data_service.get_real_travel_guide(
                destination=destination,
                travel_style=travel_style,
                budget_min=budget_min,
                budget_max=budget_max,
                budget_amount=budget_amount,
                budget_range=budget_range,
                travel_duration=travel_duration,
                interests=interests or []
            )
            
            print("✅ DeepSeek真实旅游攻略生成完成！")
            return guide_data
            
        except ImportError:
            print("⚠️ 真实数据旅游服务不可用，使用增强版服务...")
            # 回退到增强版服务
            try:
                from .services.enhanced_travel_service import EnhancedTravelService
                enhanced_service = EnhancedTravelService()
                
                guide_data = enhanced_service.get_real_travel_guide(
                    destination=destination,
                    travel_style=travel_style,
                    budget_min=budget_min,
                    budget_max=budget_max,
                    budget_amount=budget_amount,
                    budget_range=budget_range,
                    travel_duration=travel_duration,
                    interests=interests or []
                )
                
                print("✅ 增强版旅游攻略生成完成！")
                return guide_data
                
            except ImportError:
                print("⚠️ 增强版旅游服务不可用，使用原版服务...")
                # 回退到原版服务
                from .services.travel_data_service import TravelDataService
                travel_service = TravelDataService()
                
                base_data = travel_service.get_travel_guide_data(
                    destination=destination,
                    travel_style=travel_style,
                    budget_min=budget_min,
                    budget_max=budget_max,
                    budget_amount=budget_amount,
                    budget_range=budget_range,
                    travel_duration=travel_duration,
                    interests=interests or []
                )
                
                # 尝试使用DeepSeek API生成增强内容
                try:
                    print(f"🤖 尝试使用DeepSeek API为{destination}生成增强内容...")
                    deepseek_content = generate_travel_guide_with_deepseek(
                        destination, travel_style, budget_min, budget_max, budget_amount, budget_range, travel_duration, interests
                    )
                    
                    if deepseek_content:
                        print("✅ DeepSeek API生成成功，解析并合并数据...")
                        parsed_deepseek_data = parse_deepseek_travel_guide(deepseek_content, destination)
                        
                        guide_data = {
                            **base_data,
                            **parsed_deepseek_data,
                            'detailed_guide': deepseek_content,
                        }
                    else:
                        print("⚠️ DeepSeek API生成失败，使用基础数据...")
                        guide_data = base_data
                        
                except Exception as deepseek_error:
                    print(f"⚠️ DeepSeek API不可用，使用基础数据: {deepseek_error}")
                    guide_data = base_data
                
                return guide_data
        
    except Exception as e:
        print(f"❌ 生成旅游攻略失败: {e}")
        raise Exception(f"无法获取{destination}的旅游数据: {str(e)}")


def parse_deepseek_travel_guide(content, destination):
    """解析DeepSeek生成的旅游攻略内容，提取结构化数据"""
    try:
        parsed_data = {
            'destination': destination,
            'must_visit_attractions': [],
            'food_recommendations': [],
            'transportation_guide': {},
            'travel_tips': [],
            'budget_estimate': {},
            'best_time_to_visit': '',
            'daily_schedule': [],
            'cost_breakdown': {}
        }
        
        # 简单的文本解析逻辑
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检测章节标题
            if '景点' in line or '必去' in line:
                current_section = 'attractions'
            elif '美食' in line or '餐厅' in line:
                current_section = 'food'
            elif '交通' in line:
                current_section = 'transport'
            elif '贴士' in line or '注意事项' in line:
                current_section = 'tips'
            elif '预算' in line or '费用' in line:
                current_section = 'budget'
            elif '时间' in line or '季节' in line:
                current_section = 'time'
            elif '行程' in line or '安排' in line:
                current_section = 'schedule'
            elif line.startswith(('•', '-', '1.', '2.', '3.', '4.', '5.')):
                # 提取列表项
                item = line.replace('•', '').replace('-', '').strip()
                if item and len(item) > 3:  # 过滤太短的项目
                    if current_section == 'attractions':
                        parsed_data['must_visit_attractions'].append(item)
                    elif current_section == 'food':
                        parsed_data['food_recommendations'].append(item)
                    elif current_section == 'tips':
                        parsed_data['travel_tips'].append(item)
            elif current_section == 'time' and len(line) > 10:
                parsed_data['best_time_to_visit'] = line
            elif current_section == 'transport' and ':' in line:
                # 提取交通信息
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    parsed_data['transportation_guide'][key] = value
        
        # 确保至少有一些数据
        if not parsed_data['must_visit_attractions']:
            parsed_data['must_visit_attractions'] = [f"{destination}著名景点"]
        if not parsed_data['food_recommendations']:
            parsed_data['food_recommendations'] = [f"{destination}特色美食"]
        if not parsed_data['travel_tips']:
            parsed_data['travel_tips'] = [f"建议提前了解{destination}的天气情况"]
        
        return parsed_data
        
    except Exception as e:
        print(f"解析DeepSeek内容失败: {e}")
        return {}


def generate_travel_guide_with_deepseek(destination, travel_style, budget_min, budget_max, budget_amount, budget_range, travel_duration, interests):
    """使用DeepSeek API生成旅游攻略"""
    try:
        # 构建更详细的提示词
        interests_text = "、".join(interests) if interests else "通用"
        
        # 根据旅行风格调整提示词
        style_prompts = {
            'cultural': '文化探索型，重点关注历史遗迹、博物馆、当地文化体验',
            'adventure': '冒险刺激型，重点关注户外活动、极限运动、自然探索',
            'relaxation': '休闲放松型，重点关注温泉、度假村、慢节奏体验',
            'foodie': '美食探索型，重点关注当地特色餐厅、美食街、烹饪体验',
            'shopping': '购物娱乐型，重点关注购物中心、特色市场、娱乐场所',
            'photography': '摄影记录型，重点关注风景优美的地方、最佳拍摄时间',
            'general': '综合体验型，平衡各种旅游元素'
        }
        
        style_desc = style_prompts.get(travel_style, '综合体验型')
        
        # 根据预算范围调整提示词
        avg_budget = (budget_min + budget_max) // 2
        if avg_budget < 3000:
            budget_desc = f'经济型预算({budget_min}-{budget_max}元)，重点关注性价比高的选择，住宿选择青年旅社或经济型酒店，餐饮以当地小吃和平价餐厅为主'
        elif avg_budget < 8000:
            budget_desc = f'舒适型预算({budget_min}-{budget_max}元)，平衡价格和质量，住宿选择商务酒店或精品民宿，餐饮可以体验一些当地特色餐厅'
        elif avg_budget < 15000:
            budget_desc = f'豪华型预算({budget_min}-{budget_max}元)，追求品质体验，住宿选择豪华酒店或度假村，餐饮可以尝试高级餐厅和米其林推荐'
        else:
            budget_desc = f'奢华型预算({budget_min}-{budget_max}元)，追求顶级体验，住宿选择五星级酒店或奢华度假村，餐饮以米其林星级餐厅为主'
        
        prompt = f"""请为{destination}生成一份详细、真实、实用的旅游攻略。

旅行要求：
- 目的地：{destination}
- 旅行风格：{style_desc}
- 预算范围：{budget_desc}
- 旅行时长：{travel_duration}
- 兴趣偏好：{interests_text}

请严格按照以下格式生成内容：

## 🏛️ 必去景点推荐
1. [景点名称] - [门票价格] - [开放时间] - [交通方式] - [推荐理由]
2. [景点名称] - [门票价格] - [开放时间] - [交通方式] - [推荐理由]
...

## 🍜 美食推荐
1. [餐厅名称] - [特色菜品] - [价格区间] - [地址] - [推荐理由]
2. [餐厅名称] - [特色菜品] - [价格区间] - [地址] - [推荐理由]
...

## 🚗 交通指南
- 机场/火车站到市区：[具体交通方式和费用]
- 市内交通：[地铁、公交、出租车等信息]
- 景点间交通：[具体路线和费用]

## 🏨 住宿推荐
- 经济型：[酒店名称和价格]
- 中档型：[酒店名称和价格]
- 高端型：[酒店名称和价格]

## 📅 每日行程安排
根据{travel_duration}制定详细行程，包含具体时间安排

## 💰 预算明细
- 住宿费用：[具体金额]
- 餐饮费用：[具体金额]
- 交通费用：[具体金额]
- 门票费用：[具体金额]
- 其他费用：[具体金额]
- 总预算：[具体金额]

## 💡 实用贴士
1. [具体贴士内容]
2. [具体贴士内容]
...

## 🏮 文化背景
[当地特色、习俗、语言等文化信息]

请确保所有信息真实可靠，价格信息准确，避免虚假信息。内容要详细实用，便于游客参考。"""

        # 使用现有的DeepSeekClient
        from .utils import DeepSeekClient
        
        try:
            deepseek = DeepSeekClient()
            content = deepseek.generate_content(prompt)
            if content and len(content) > 100:  # 确保内容足够详细
                print(f"✅ DeepSeek API生成成功，内容长度: {len(content)}字符")
                return content
            else:
                print("⚠️ DeepSeek API生成的内容过短")
                return None
        except ValueError as api_key_error:
            if "API密钥未配置" in str(api_key_error):
                print("⚠️ DeepSeek API密钥未配置，跳过AI增强功能")
                return None
            else:
                print(f"❌ DeepSeekClient配置错误: {api_key_error}")
                return None
        except requests.exceptions.HTTPError as http_error:
            if http_error.response.status_code == 401:
                print("⚠️ DeepSeek API认证失败 (401)，请检查API密钥是否正确")
                return None
            elif http_error.response.status_code == 429:
                print("⚠️ DeepSeek API请求频率超限 (429)，请稍后重试")
                return None
            else:
                print(f"❌ DeepSeek API HTTP错误: {http_error.response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print("⚠️ DeepSeek API请求超时，跳过AI增强功能")
            return None
        except requests.exceptions.ConnectionError:
            print("⚠️ DeepSeek API连接失败，跳过AI增强功能")
            return None
        except Exception as deepseek_error:
            print(f"❌ DeepSeekClient调用失败: {deepseek_error}")
            return None
            
    except Exception as e:
        print(f"❌ DeepSeek API调用异常: {e}")
        return None


# ==================== 自动求职机相关视图 - 已隐藏 ====================

# @login_required
# def job_search_machine(request):
#     """自动求职机页面"""
#     return render(request, 'tools/job_search_machine.html')


# @login_required
# def job_search_profile(request):
#     """求职者资料页面"""
#     return render(request, 'tools/job_search_profile.html')


# @login_required
# def job_search_dashboard(request):
#     """求职仪表盘页面"""
#     return render(request, 'tools/job_search_dashboard.html')


# @csrf_exempt
# @require_http_methods(["POST"])
# @login_required
# def create_job_search_request_api(request):
#     """创建求职请求API"""
#     try:
#         data = json.loads(request.body)
#         
#         # 验证必填字段
#         required_fields = ['job_title', 'location', 'min_salary', 'max_salary']
#         for field in required_fields:
#             if not data.get(field):
#                 return JsonResponse({
#                     'success': False,
#                     'message': f'请填写{field}字段'
#                 })
#         
#         # 创建求职请求
#         job_service = JobSearchService()
#         job_request = job_service.create_job_search_request(
#             user=request.user,
#             job_title=data['job_title'],
#             location=data['location'],
#             min_salary=int(data['min_salary']),
#             max_salary=int(data['max_salary']),
#             job_type=data.get('job_type', 'full_time'),
#             experience_level=data.get('experience_level', '1-3'),
#             keywords=data.get('keywords', []),
#             company_size=data.get('company_size', ''),
#             industry=data.get('industry', ''),
#             education_level=data.get('education_level', ''),
#             auto_apply=data.get('auto_apply', True),
#             max_applications=int(data.get('max_applications', 50)),
#             application_interval=int(data.get('application_interval', 30))
#         )
#         
#         return JsonResponse({
#             'success': True,
#             'message': '求职请求创建成功',
#             'request_id': job_request.id
#         })
#         
#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'message': f'创建求职请求失败: {str(e)}'
#         })


# @csrf_exempt
# @require_http_methods(["POST"])
# @login_required
# def start_job_search_api(request):
#     """开始自动求职API"""
#     try:
#         data = json.loads(request.body)
#         request_id = data.get('request_id')
#         
#         if not request_id:
#             return JsonResponse({
#                 'success': False,
#                 'message': '请提供求职请求ID'
#             })
#         
#         # 获取求职请求
#         try:
#             job_request = JobSearchRequest.objects.get(id=request_id, user=request.user)
#         except JobSearchRequest.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'message': '求职请求不存在'
#             })
#         
#         # 开始自动求职
#         job_service = JobSearchService()
#         result = job_service.start_auto_job_search(job_request)
#         
#         return JsonResponse(result)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_job_applications_api(request):
    """获取职位申请记录API"""
    try:
        request_id = request.GET.get('request_id')
        
        if request_id:
            applications = JobApplication.objects.filter(
                job_search_request_id=request_id,
                job_search_request__user=request.user
            ).order_by('-application_time')
        else:
            applications = JobApplication.objects.filter(
                job_search_request__user=request.user
            ).order_by('-application_time')
        
        applications_data = []
        for app in applications:
            applications_data.append({
                'id': app.id,
                'job_title': app.job_title,
                'company_name': app.company_name,
                'company_logo': app.company_logo,
                'location': app.location,
                'salary_range': app.salary_range,
                'status': app.status,
                'status_color': app.get_status_color(),
                'match_score': app.match_score,
                'match_reasons': app.match_reasons,
                'application_time': app.application_time.strftime('%Y-%m-%d %H:%M:%S'),
                'job_url': app.job_url,
                'notes': app.notes
            })
        
        return JsonResponse({
            'success': True,
            'data': applications_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取申请记录失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def save_job_profile_api(request):
    """保存求职者资料API"""
    try:
        data = json.loads(request.body)
        
        # 获取或创建用户资料
        profile, created = JobSearchProfile.objects.get_or_create(user=request.user)
        
        # 更新资料
        profile.name = data.get('name', '')
        profile.phone = data.get('phone', '')
        profile.email = data.get('email', '')
        profile.current_position = data.get('current_position', '')
        profile.years_of_experience = int(data.get('years_of_experience', 0))
        profile.education_level = data.get('education_level', '')
        profile.school = data.get('school', '')
        profile.major = data.get('major', '')
        profile.skills = data.get('skills', [])
        profile.expected_salary_min = int(data.get('expected_salary_min', 0))
        profile.expected_salary_max = int(data.get('expected_salary_max', 0))
        profile.preferred_locations = data.get('preferred_locations', [])
        profile.preferred_industries = data.get('preferred_industries', [])
        profile.resume_text = data.get('resume_text', '')
        profile.boss_account = data.get('boss_account', '')
        profile.auto_apply_enabled = data.get('auto_apply_enabled', True)
        profile.notification_enabled = data.get('notification_enabled', True)
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': '资料保存成功'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'保存资料失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_job_profile_api(request):
    """获取求职者资料API"""
    try:
        try:
            profile = JobSearchProfile.objects.get(user=request.user)
            profile_data = {
                'name': profile.name,
                'phone': profile.phone,
                'email': profile.email,
                'current_position': profile.current_position,
                'years_of_experience': profile.years_of_experience,
                'education_level': profile.education_level,
                'school': profile.school,
                'major': profile.major,
                'skills': profile.skills,
                'expected_salary_min': profile.expected_salary_min,
                'expected_salary_max': profile.expected_salary_max,
                'preferred_locations': profile.preferred_locations,
                'preferred_industries': profile.preferred_industries,
                'resume_text': profile.resume_text,
                'boss_account': profile.boss_account,
                'auto_apply_enabled': profile.auto_apply_enabled,
                'notification_enabled': profile.notification_enabled,
                'total_applications': profile.total_applications,
                'total_interviews': profile.total_interviews,
                'total_offers': profile.total_offers,
                'success_rate': profile.get_success_rate()
            }
        except JobSearchProfile.DoesNotExist:
            profile_data = {}
        
        return JsonResponse({
            'success': True,
            'data': profile_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取资料失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_job_search_statistics_api(request):
    """获取求职统计信息API"""
    try:
        job_service = JobSearchService()
        stats = job_service.get_job_search_statistics(request.user)
        
        return JsonResponse({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_application_status_api(request):
    """更新申请状态API"""
    try:
        data = json.loads(request.body)
        application_id = data.get('application_id')
        new_status = data.get('status')
        
        if not application_id or not new_status:
            return JsonResponse({
                'success': False,
                'message': '请提供申请ID和新状态'
            })
        
        # 更新申请状态
        application = JobApplication.objects.get(
            id=application_id,
            job_search_request__user=request.user
        )
        application.status = new_status
        application.response_time = timezone.now()
        application.save()
        
        # 更新用户统计
        profile = JobSearchProfile.objects.get(user=request.user)
        if new_status in ['contacted', 'interview']:
            profile.total_interviews += 1
        elif new_status == 'accepted':
            profile.total_offers += 1
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': '状态更新成功'
        })
        
    except JobApplication.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '申请记录不存在'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'更新状态失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_application_notes_api(request):
    """添加申请备注API"""
    try:
        data = json.loads(request.body)
        application_id = data.get('application_id')
        notes = data.get('notes', '')
        
        if not application_id:
            return JsonResponse({
                'success': False,
                'message': '请提供申请ID'
            })
        
        # 更新备注
        application = JobApplication.objects.get(
            id=application_id,
            job_search_request__user=request.user
        )
        application.notes = notes
        application.save()
        
        return JsonResponse({
            'success': True,
            'message': '备注添加成功'
        })
        
    except JobApplication.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '申请记录不存在'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'添加备注失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def generate_boss_qr_code_api(request):
    """生成Boss直聘登录二维码API"""
    try:
        # 简单的频率限制：每个用户每分钟最多生成3次二维码
        cache_key = f'boss_qr_rate_limit_{request.user.id}'
        request_count = cache.get(cache_key, 0)
        
        if request_count >= 3:
            return JsonResponse({
                'success': False,
                'message': '请求过于频繁，请稍后再试'
            })
        
        # 增加请求计数
        cache.set(cache_key, request_count + 1, 60)  # 1分钟过期
        
        job_service = JobSearchService()
        result = job_service.generate_qr_code(request.user.id)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'生成二维码失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_boss_login_page_url_api(request):
    """获取Boss直聘登录页面URL API"""
    try:
        # 频率限制检查
        cache_key = f'boss_login_url_rate_limit_{request.user.id}'
        request_count = cache.get(cache_key, 0)
        if request_count >= 5:
            return JsonResponse({
                'success': False,
                'message': '请求过于频繁，请稍后再试'
            })
        cache.set(cache_key, request_count + 1, 60)
        
        job_service = JobSearchService()
        result = job_service.get_login_page_url(request.user.id)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取登录页面URL失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_boss_user_token_api(request):
    """获取Boss直聘用户token API"""
    try:
        # 频率限制检查
        cache_key = f'boss_token_rate_limit_{request.user.id}'
        request_count = cache.get(cache_key, 0)
        if request_count >= 3:
            return JsonResponse({
                'success': False,
                'message': '请求过于频繁，请稍后再试'
            })
        cache.set(cache_key, request_count + 1, 60)
        
        job_service = JobSearchService()
        result = job_service.get_user_token_with_selenium(request.user.id)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取用户token失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def check_boss_login_status_api(request):
    """检查Boss直聘登录状态API"""
    try:
        job_service = JobSearchService()
        result = job_service.check_qr_login_status(request.user.id)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'检查登录状态失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def check_boss_login_status_selenium_api(request):
    """使用Selenium检查Boss直聘登录状态API"""
    try:
        # 简单的频率限制：每个用户每分钟最多检查3次
        cache_key = f'boss_login_check_rate_limit_{request.user.id}'
        request_count = cache.get(cache_key, 0)
        
        if request_count >= 3:
            return JsonResponse({
                'success': False,
                'message': '请求过于频繁，请稍后再试'
            })
        
        # 增加请求计数
        cache.set(cache_key, request_count + 1, 60)  # 1分钟过期
        
        job_service = JobSearchService()
        result = job_service.check_login_status_with_selenium(request.user.id)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'检查登录状态失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_boss_login_status_api(request):
    """获取Boss直聘登录状态API"""
    try:
        job_service = JobSearchService()
        result = job_service.get_login_status(request.user.id)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取登录状态失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def boss_logout_api(request):
    """Boss直聘退出登录API"""
    try:
        job_service = JobSearchService()
        result = job_service.logout(request.user.id)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'退出登录失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def send_contact_request_api(request):
    """发送联系请求API"""
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        
        if not job_id:
            return JsonResponse({
                'success': False,
                'message': '请提供职位ID'
            })
        
        # 检查登录状态
        job_service = JobSearchService()
        login_status = job_service.get_login_status(request.user.id)
        
        if not login_status.get('is_logged_in'):
            return JsonResponse({
                'success': False,
                'message': '请先登录Boss直聘'
            })
        
        # 发送联系请求
        result = job_service.boss_api.send_contact_request(job_id)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'发送联系请求失败: {str(e)}'
        })


# 爬虫管理相关API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def start_crawler_api(request):
    """启动爬虫任务API"""
    try:
        data = json.loads(request.body)
        subscription_id = data.get('subscription_id')  # 可选，指定订阅ID
        
        from apps.tools.services.social_media_crawler import crawler_manager
        
        # 启动爬虫任务
        result = crawler_manager.start_crawler_for_user(request.user, subscription_id)
        
        return JsonResponse(result, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'启动爬虫任务失败: {str(e)}',
            'updates_count': 0
        }, status=500, content_type='application/json')


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_crawler_status_api(request):
    """获取爬虫状态API"""
    try:
        from apps.tools.services.social_media_crawler import crawler_manager
        
        # 获取爬虫状态
        status = crawler_manager.get_user_crawler_status(request.user)
        
        return JsonResponse(status, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({
            'has_subscriptions': False,
            'message': f'获取状态失败: {str(e)}'
        }, status=500, content_type='application/json')

# 健身社区相关视图函数
@login_required
def fitness_community(request):
    """健身社区页面"""
    return render(request, 'tools/fitness_community.html')

@login_required
def fitness_profile(request):
    """健身个人档案页面"""
    return render(request, 'tools/fitness_profile.html')

@login_required
def fitness_tools(request):
    """健身工具页面"""
    return render(request, 'tools/fitness_tools.html')

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_fitness_community_posts_api(request):
    """获取健身社区帖子API"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        post_type = request.GET.get('post_type', '')
        user_id = request.GET.get('user_id', '')
        
        posts = FitnessCommunityPost.objects.filter(
            is_deleted=False,
            is_public=True
        ).select_related('user', 'related_checkin')
        
        # 过滤帖子类型
        if post_type:
            posts = posts.filter(post_type=post_type)
        
        # 过滤用户
        if user_id:
            posts = posts.filter(user_id=user_id)
        
        # 分页
        total_count = posts.count()
        posts = posts[(page - 1) * page_size:page * page_size]
        
        posts_data = []
        for post in posts:
            # 获取用户档案
            try:
                profile = FitnessUserProfile.objects.get(user=post.user)
                user_display_name = profile.get_display_name()
                user_avatar = profile.avatar.url if profile.avatar else None
            except FitnessUserProfile.DoesNotExist:
                user_display_name = post.user.username
                user_avatar = None
            
            # 检查当前用户是否点赞
            is_liked = FitnessCommunityLike.objects.filter(
                user=request.user,
                post=post
            ).exists()
            
            posts_data.append({
                'id': post.id,
                'post_type': post.post_type,
                'title': post.title,
                'content': post.content,
                'tags': post.tags,
                'training_parts': post.training_parts,
                'difficulty_level': post.difficulty_level,
                'likes_count': post.likes_count,
                'comments_count': post.comments_count,
                'shares_count': post.shares_count,
                'views_count': post.views_count,
                'is_liked': is_liked,
                'is_featured': post.is_featured,
                'created_at': post.created_at.isoformat(),
                'user': {
                    'id': post.user.id,
                    'username': post.user.username,
                    'display_name': user_display_name,
                    'avatar': user_avatar
                },
                'related_checkin': {
                    'id': post.related_checkin.id,
                    'date': post.related_checkin.date.isoformat(),
                    'workout_type': post.related_checkin.detail.workout_type if post.related_checkin.detail else None,
                    'duration': post.related_checkin.detail.duration if post.related_checkin.detail else None,
                    'training_parts': post.related_checkin.detail.training_parts if post.related_checkin.detail else [],
                    'feeling_rating': post.related_checkin.detail.feeling_rating if post.related_checkin.detail else None,
                } if post.related_checkin else None
            })
        
        return JsonResponse({
            'success': True,
            'posts': posts_data,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'has_next': page * page_size < total_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_fitness_community_post_api(request):
    """创建健身社区帖子API"""
    try:
        data = json.loads(request.body)
        post_type = data.get('post_type')
        title = data.get('title')
        content = data.get('content')
        tags = data.get('tags', [])
        training_parts = data.get('training_parts', [])
        difficulty_level = data.get('difficulty_level')
        related_checkin_id = data.get('related_checkin_id')
        
        if not post_type or not title or not content:
            return JsonResponse({
                'success': False,
                'error': '帖子类型、标题和内容不能为空'
            }, status=400)
        
        # 创建帖子
        post_data = {
            'user': request.user,
            'post_type': post_type,
            'title': title,
            'content': content,
            'tags': tags,
            'training_parts': training_parts,
            'difficulty_level': difficulty_level
        }
        
        if related_checkin_id:
            try:
                checkin = CheckInCalendar.objects.get(
                    id=related_checkin_id,
                    user=request.user
                )
                post_data['related_checkin'] = checkin
            except CheckInCalendar.DoesNotExist:
                pass
        
        post = FitnessCommunityPost.objects.create(**post_data)
        
        return JsonResponse({
            'success': True,
            'post_id': post.id,
            'message': '帖子发布成功'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def like_fitness_post_api(request):
    """点赞健身帖子API"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        comment_id = data.get('comment_id')
        
        if not post_id and not comment_id:
            return JsonResponse({
                'success': False,
                'error': '帖子ID或评论ID不能为空'
            }, status=400)
        
        if post_id:
            try:
                post = FitnessCommunityPost.objects.get(id=post_id)
                like, created = FitnessCommunityLike.objects.get_or_create(
                    user=request.user,
                    post=post
                )
                
                if created:
                    post.likes_count += 1
                    post.save()
                    action = 'liked'
                else:
                    like.delete()
                    post.likes_count = max(0, post.likes_count - 1)
                    post.save()
                    action = 'unliked'
                
                return JsonResponse({
                    'success': True,
                    'action': action,
                    'likes_count': post.likes_count
                })
                
            except FitnessCommunityPost.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': '帖子不存在'
                }, status=404)
        
        elif comment_id:
            try:
                comment = FitnessCommunityComment.objects.get(id=comment_id)
                like, created = FitnessCommunityLike.objects.get_or_create(
                    user=request.user,
                    comment=comment
                )
                
                if created:
                    comment.likes_count += 1
                    comment.save()
                    action = 'liked'
                else:
                    like.delete()
                    comment.likes_count = max(0, comment.likes_count - 1)
                    comment.save()
                    action = 'unliked'
                
                return JsonResponse({
                    'success': True,
                    'action': action,
                    'likes_count': comment.likes_count
                })
                
            except FitnessCommunityComment.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': '评论不存在'
                }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def comment_fitness_post_api(request):
    """评论健身帖子API"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        content = data.get('content')
        parent_comment_id = data.get('parent_comment_id')
        
        if not post_id or not content:
            return JsonResponse({
                'success': False,
                'error': '帖子ID和评论内容不能为空'
            }, status=400)
        
        try:
            post = FitnessCommunityPost.objects.get(id=post_id)
        except FitnessCommunityPost.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '帖子不存在'
            }, status=404)
        
        comment_data = {
            'post': post,
            'user': request.user,
            'content': content
        }
        
        if parent_comment_id:
            try:
                parent_comment = FitnessCommunityComment.objects.get(id=parent_comment_id)
                comment_data['parent_comment'] = parent_comment
            except FitnessCommunityComment.DoesNotExist:
                pass
        
        comment = FitnessCommunityComment.objects.create(**comment_data)
        
        # 更新帖子评论数
        post.comments_count += 1
        post.save()
        
        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'message': '评论发布成功'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_fitness_user_profile_api(request):
    """获取健身用户档案API"""
    try:
        user_id = request.GET.get('user_id', request.user.id)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '用户不存在'
            }, status=404)
        
        # 获取或创建用户档案
        profile, created = FitnessUserProfile.objects.get_or_create(
            user=user,
            defaults={
                'nickname': user.username,
                'fitness_level': 'beginner',
                'primary_goals': ['增肌', '减脂'],
                'favorite_workouts': ['力量训练']
            }
        )
        
        # 更新统计数据
        profile.update_stats()
        
        # 获取用户成就
        achievements = UserFitnessAchievement.objects.filter(
            user=user
        ).select_related('achievement').order_by('-earned_at')
        
        achievements_data = []
        for user_achievement in achievements:
            achievements_data.append({
                'id': user_achievement.achievement.id,
                'name': user_achievement.achievement.name,
                'description': user_achievement.achievement.description,
                'level': user_achievement.achievement.level,
                'icon': user_achievement.achievement.icon,
                'color': user_achievement.achievement.color,
                'earned_at': user_achievement.earned_at.isoformat(),
                'is_shared': user_achievement.is_shared
            })
        
        # 获取关注关系
        is_following = False
        if user_id != request.user.id:
            is_following = FitnessFollow.objects.filter(
                follower=request.user,
                following=user
            ).exists()
        
        profile_data = {
            'user_id': user.id,
            'username': user.username,
            'nickname': profile.nickname,
            'avatar': profile.avatar.url if profile.avatar else None,
            'bio': profile.bio,
            'fitness_level': profile.fitness_level,
            'primary_goals': profile.primary_goals,
            'favorite_workouts': profile.favorite_workouts,
            'total_workouts': profile.total_workouts,
            'total_duration': profile.total_duration,
            'current_streak': profile.current_streak,
            'longest_streak': profile.longest_streak,
            'is_public_profile': profile.is_public_profile,
            'achievements': achievements_data,
            'is_following': is_following,
            'created_at': profile.created_at.isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'profile': profile_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def follow_fitness_user_api(request):
    """关注健身用户API"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': '用户ID不能为空'
            }, status=400)
        
        if int(user_id) == request.user.id:
            return JsonResponse({
                'success': False,
                'error': '不能关注自己'
            }, status=400)
        
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '用户不存在'
            }, status=404)
        
        follow, created = FitnessFollow.objects.get_or_create(
            follower=request.user,
            following=target_user
        )
        
        if created:
            action = 'followed'
        else:
            follow.delete()
            action = 'unfollowed'
        
        return JsonResponse({
            'success': True,
            'action': action
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_fitness_achievements_api(request):
    """获取健身成就API"""
    try:
        user_id = request.GET.get('user_id', request.user.id)
        
        # 获取所有成就
        achievements = FitnessAchievement.objects.all().order_by('level', 'achievement_type', 'name')
        
        # 获取用户已获得的成就
        user_achievements = UserFitnessAchievement.objects.filter(
            user_id=user_id
        ).values_list('achievement_id', flat=True)
        
        achievements_data = []
        for achievement in achievements:
            is_achieved = achievement.id in user_achievements
            progress = 0
            
            if is_achieved:
                progress = 100
            else:
                # 计算进度（这里需要根据具体条件计算）
                progress = 0  # 暂时设为0，后续可以根据具体条件计算
            
            achievements_data.append({
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'achievement_type': achievement.achievement_type,
                'level': achievement.level,
                'icon': achievement.icon,
                'color': achievement.color,
                'is_achieved': is_achieved,
                'progress': progress,
                'unlock_condition': achievement.unlock_condition
            })
        
        return JsonResponse({
            'success': True,
            'achievements': achievements_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def share_achievement_api(request):
    """分享成就API"""
    try:
        data = json.loads(request.body)
        achievement_id = data.get('achievement_id')
        
        if not achievement_id:
            return JsonResponse({
                'success': False,
                'error': '成就ID不能为空'
            }, status=400)
        
        try:
            user_achievement = UserFitnessAchievement.objects.get(
                user=request.user,
                achievement_id=achievement_id
            )
        except UserFitnessAchievement.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '成就不存在'
            }, status=404)
        
        # 标记为已分享
        user_achievement.is_shared = True
        user_achievement.save()
        
        # 创建社区帖子
        achievement = user_achievement.achievement
        post = FitnessCommunityPost.objects.create(
            user=request.user,
            post_type='achievement',
            title=f'🎉 获得成就：{achievement.name}',
            content=f'我刚刚获得了{achievement.get_level_display()}成就「{achievement.name}」！\n\n{achievement.description}\n\n继续加油！💪',
            tags=['成就分享', achievement.achievement_type, achievement.level],
            difficulty_level='beginner'  # 成就分享默认初级
        )
        
        return JsonResponse({
            'success': True,
            'message': '成就分享成功',
            'post_id': post.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# 中优先级：添加缺失的页面视图函数
@login_required
def tarot_reading_view(request):
    """塔罗牌占卜页面"""
    return render(request, 'tools/tarot_reading.html')

@login_required
def tarot_diary_view(request):
    """塔罗牌日记页面"""
    return render(request, 'tools/tarot_diary.html')

@login_required
def meetsomeone_dashboard_view(request):
    """遇见某人主页面"""
    return render(request, 'tools/meetsomeone_dashboard.html')

@login_required
def meetsomeone_timeline_view(request):
    """遇见某人时间线页面"""
    return render(request, 'tools/meetsomeone_timeline.html')

@login_required
def meetsomeone_graph_view(request):
    """遇见某人图表页面"""
    return render(request, 'tools/meetsomeone_graph.html')

# ===== 功能推荐系统API视图 =====

@csrf_exempt
@require_http_methods(["GET", "POST"])
def feature_recommendations_api(request):
    """功能推荐API - 支持GET获取推荐和POST记录行为"""
    try:
        if request.method == "GET":
            # GET请求：获取功能推荐
            from .services.feature_recommendation_engine import FeatureRecommendationEngine
            
            # 检查用户是否已登录
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': True,
                    'data': [],
                    'algorithm': 'smart',
                    'count': 0
                })
            
            # 获取查询参数
            algorithm = request.GET.get('algorithm', 'smart')
            limit = int(request.GET.get('limit', 6))
            force_show = request.GET.get('force_show', 'false').lower() == 'true'
            
            # 创建推荐引擎实例
            engine = FeatureRecommendationEngine()
            
            # 获取用户上下文信息
            context = {
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
            
            # 获取推荐
            recommendations = engine.get_recommendations_for_user(
                user=request.user,
                limit=limit,
                context=context
            )
            
            # 格式化推荐数据
            formatted_recommendations = []
            for rec in recommendations:
                feature = rec.get('feature')  # 推荐引擎返回的是字典，包含feature键
                if feature:
                    # 获取推荐理由
                    reason = rec.get('reason', '为您推荐一个实用功能')
                    
                    # 获取功能类别显示名称
                    category_display = feature.get_category_display()
                    
                    formatted_recommendations.append({
                        'id': feature.id,
                        'name': feature.name,
                        'description': feature.description,
                        'category': feature.category,
                        'category_display': category_display,
                        'icon_class': feature.icon_class,
                        'icon_color': feature.icon_color,
                        'url_name': feature.url_name,
                        'recommendation_weight': feature.recommendation_weight,
                        'popularity_score': feature.popularity_score,
                        'recommendation_reason': reason,
                    })
            
            return JsonResponse({
                'success': True,
                'data': formatted_recommendations,
                'algorithm': algorithm,
                'count': len(formatted_recommendations)
            })
        
        elif request.method == "POST":
            # POST请求：记录推荐行为
            # 检查用户是否已登录
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': '用户未登录'
                }, status=401)
            
            data = json.loads(request.body)
            feature_id = data.get('feature_id')
            action = data.get('action', 'shown')
            session_id = data.get('session_id', '')
            
            if not feature_id:
                return JsonResponse({
                    'success': False,
                    'error': '缺少功能ID'
                }, status=400)
            
            from .models import Feature, FeatureRecommendation
            
            try:
                feature = Feature.objects.get(id=feature_id)
            except Feature.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': '功能不存在'
                }, status=404)
            
            # 记录推荐行为
            recommendation = FeatureRecommendation.objects.create(
                user=request.user,
                feature=feature,
                session_id=session_id,
                action=action,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                action_time=timezone.now() if action != 'shown' else None
            )
            
            # 如果是点击行为，更新功能使用统计
            if action == 'clicked':
                feature.increment_usage()
                recommendation.action_time = timezone.now()
                recommendation.save(update_fields=['action_time'])
            
            return JsonResponse({
                'success': True,
                'message': '推荐行为记录成功',
                'action': action,
                'feature_id': feature_id
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)





@csrf_exempt
@require_http_methods(["GET"])
@login_required
def feature_list_api(request):
    """获取功能列表API"""
    try:
        from .models import Feature
        
        # 获取查询参数
        category = request.GET.get('category')
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # 构建查询
        queryset = Feature.objects.filter(is_active=True, is_public=True)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(description__icontains=search)
            )
        
        # 分页
        total_count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        features = queryset[start:end]
        
        # 格式化数据
        formatted_features = []
        for feature in features:
            formatted_features.append({
                'id': feature.id,
                'name': feature.name,
                'description': feature.description,
                'category': feature.category,
                'feature_type': feature.feature_type,
                'icon_class': feature.icon_class,
                'icon_color': feature.icon_color,
                'url_name': feature.url_name,
                'recommendation_weight': feature.recommendation_weight,
                'popularity_score': feature.popularity_score,
                'require_login': feature.require_login,
                'require_membership': feature.require_membership,
            })
        
        return JsonResponse({
            'success': True,
            'features': formatted_features,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def recommendation_stats_api(request):
    """获取推荐统计API"""
    try:
        from .models import FeatureRecommendation
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # 获取查询参数
        days = int(request.GET.get('days', 30))
        since_date = timezone.now() - timedelta(days=days)
        
        # 获取统计数据
        stats = FeatureRecommendation.objects.filter(
            user=request.user,
            created_at__gte=since_date
        ).aggregate(
            total_shown=Count('id', filter=Q(action='shown')),
            total_clicked=Count('id', filter=Q(action='clicked')),
            total_dismissed=Count('id', filter=Q(action='dismissed')),
            total_not_interested=Count('id', filter=Q(action='not_interested'))
        )
        
        # 计算点击率
        total_shown = stats['total_shown'] or 0
        total_clicked = stats['total_clicked'] or 0
        click_rate = (total_clicked / total_shown * 100) if total_shown > 0 else 0
        
        return JsonResponse({
            'success': True,
            'stats': {
                'period_days': days,
                'total_shown': total_shown,
                'total_clicked': total_clicked,
                'total_dismissed': stats['total_dismissed'] or 0,
                'total_not_interested': stats['total_not_interested'] or 0,
                'click_rate': round(click_rate, 2)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def resolve_url_api(request):
    """URL解析API - 根据url_name解析到实际URL"""
    try:
        url_name = request.GET.get('url_name')
        if not url_name:
            return JsonResponse({
                'success': False,
                'error': '缺少url_name参数'
            }, status=400)
        
        from .models import Feature
        
        try:
            feature = Feature.objects.filter(url_name=url_name).first()
            if not feature:
                return JsonResponse({
                    'success': False,
                    'error': f'功能不存在: {url_name}'
                }, status=404)
            
            # 构建功能页面URL
            feature_url = f'/tools/{url_name}/'
            
            return JsonResponse({
                'success': True,
                'url': feature_url,
                'feature_name': feature.name,
                'url_name': url_name
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'查询功能时出错: {str(e)}'
            }, status=500)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
def meditation_audio_api(request):
    """冥想音频API"""
    if request.method == 'GET':
        try:
            action = request.GET.get('action', 'random')
            category = request.GET.get('category', '')
            keyword = request.GET.get('keyword', '')
            
            # 导入冥想音频服务
            from .services.meditation_audio_service import meditation_audio_service
            
            if action == 'categories':
                # 获取所有音效类别
                categories = meditation_audio_service.get_all_categories()
                return JsonResponse({
                    'success': True,
                    'data': categories
                }, content_type='application/json')
            
            elif action == 'random':
                # 获取随机音效
                if category:
                    # 获取指定类别的随机音效
                    sound = meditation_audio_service.get_meditation_sound(category)
                else:
                    # 获取完全随机的音效
                    sound = meditation_audio_service.get_random_meditation_sound()
                
                if sound:
                    return JsonResponse({
                        'success': True,
                        'data': sound
                    }, content_type='application/json')
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '获取音效失败'
                    }, content_type='application/json')
            
            elif action == 'search':
                # 搜索音效
                if keyword:
                    sounds = meditation_audio_service.search_meditation_sounds(keyword)
                    return JsonResponse({
                        'success': True,
                        'data': sounds
                    }, content_type='application/json')
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '搜索关键词不能为空'
                    }, content_type='application/json')
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': '不支持的操作'
                }, content_type='application/json')
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'服务器错误: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': '不支持的请求方法'
    }, content_type='application/json')


@login_required
def food_randomizer(request):
    """食物随机选择器页面"""
    return render(request, 'tools/food_randomizer.html')


# 食物随机选择器API函数
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def start_food_randomization_api(request):
    """开始食物随机选择API - 使用真实数据"""
    try:
        data = json.loads(request.body)
        meal_type = data.get('meal_type', '')
        cuisine_preference = data.get('cuisine_preference', '')
        mood = data.get('mood', '')
        price_range = data.get('price_range', '')
        dietary_restrictions = data.get('dietary_restrictions', [])
        animation_duration = data.get('animation_duration', 3000)
        
        # 构建查询条件 - 使用SQLite兼容的查询方式
        available_foods = FoodItem.objects.filter(is_active=True)
        
        # 根据餐种筛选
        if meal_type and meal_type != 'mixed':
            # 使用Python过滤而不是数据库查询
            available_foods = [food for food in available_foods if meal_type in food.meal_types]
        
        # 根据菜系偏好筛选
        if cuisine_preference and cuisine_preference != 'mixed':
            available_foods = [food for food in available_foods if food.cuisine == cuisine_preference]
        
        # 根据心情和价格范围调整筛选条件
        if mood == 'happy':
            # 开心时倾向于选择受欢迎的食物
            available_foods = [food for food in available_foods if food.popularity_score >= 0.5]
        elif mood == 'sad':
            # 难过时倾向于选择安慰食物
            available_foods = [food for food in available_foods if 'comfort' in food.tags]
        elif mood == 'tired':
            # 疲惫时倾向于选择简单易做的食物
            available_foods = [food for food in available_foods if food.difficulty == 'easy']
        
        # 根据价格范围筛选
        if price_range == 'low':
            # 低价位，选择简单易做的食物
            available_foods = [food for food in available_foods if food.difficulty == 'easy']
        elif price_range == 'high':
            # 高价位，选择高级食物
            available_foods = [food for food in available_foods if 'premium' in food.tags]
        
        # 根据饮食禁忌筛选
        if dietary_restrictions:
            for restriction in dietary_restrictions:
                if restriction == 'no_spicy':
                    # 不吃辣
                    available_foods = [food for food in available_foods if 'spicy' not in food.tags]
                elif restriction == 'vegetarian':
                    # 素食
                    available_foods = [food for food in available_foods if 'vegetarian' in food.tags]
                elif restriction == 'no_seafood':
                    # 不吃海鲜
                    available_foods = [food for food in available_foods if 'seafood' not in food.tags]
                elif restriction == 'no_pork':
                    # 不吃猪肉
                    available_foods = [food for food in available_foods if 'pork' not in food.tags]
        
        if not available_foods:
            # 如果没有找到符合条件的食物，放宽条件
            available_foods = list(FoodItem.objects.filter(is_active=True))
        
        if not available_foods:
            return JsonResponse({
                'success': False,
                'error': '没有找到合适的食物'
            })
        
        # 随机选择一个食物
        selected_food = random.choice(available_foods)
        
        # 获取备选食物（同菜系或同餐种的其他食物）
        alternative_foods = []
        all_foods = list(FoodItem.objects.filter(is_active=True).exclude(id=selected_food.id))
        
        if selected_food.cuisine != 'mixed':
            # 同菜系的食物
            alternative_foods = [food for food in all_foods if food.cuisine == selected_food.cuisine]
        else:
            # 同餐种的食物
            alternative_foods = [food for food in all_foods if any(meal_type in food.meal_types for meal_type in selected_food.meal_types)]
        
        # 限制数量
        alternative_foods = alternative_foods[:5]
        
        # 创建随机选择会话记录
        session = FoodRandomizationSession.objects.create(
            user=request.user,
            meal_type=meal_type,
            cuisine_preference=cuisine_preference,
            status='completed',
            animation_duration=animation_duration,
            selected_food=selected_food,
            alternative_foods=[food.id for food in alternative_foods],
            completed_at=timezone.now()
        )
        
        # 创建历史记录
        FoodHistory.objects.create(
            user=request.user,
            food_item=selected_food,
            meal_type=meal_type,
            session=session
        )
        
        # 构建响应数据
        response_data = {
            'success': True,
            'session_id': session.id,
            'selected_food': {
                'id': selected_food.id,
                'name': selected_food.name,
                'description': selected_food.description,
                'image_url': selected_food.image_url,
                'cuisine': selected_food.get_cuisine_display(),
                'difficulty': selected_food.get_difficulty_display(),
                'cooking_time': selected_food.cooking_time,
                'ingredients': selected_food.ingredients,
                'tags': selected_food.tags,
                'meal_types': selected_food.meal_types,
                'recipe_url': selected_food.recipe_url,
                'popularity_score': selected_food.popularity_score
            },
            'alternative_foods': [
                {
                    'id': food.id,
                    'name': food.name,
                    'description': food.description,
                    'image_url': food.image_url,
                    'cuisine': food.get_cuisine_display(),
                    'difficulty': food.get_difficulty_display(),
                    'cooking_time': food.cooking_time
                }
                for food in alternative_foods
            ],
            'message': f'为您推荐了 {selected_food.name}'
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"食物随机选择失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'随机选择失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def pause_food_randomization_api(request):
    """暂停食物随机选择API"""
    try:
        return JsonResponse({
            'success': True,
            'message': '暂停随机选择'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def pure_random_food_api(request):
    """纯随机食物选择API - 使用真实数据"""
    try:
        data = json.loads(request.body)
        animation_duration = data.get('animation_duration', 3000)
        
        # 从所有活跃食物中完全随机选择
        available_foods = FoodItem.objects.filter(is_active=True)
        
        if not available_foods.exists():
            return JsonResponse({
                'success': False,
                'error': '没有可用的食物数据'
            })
        
        # 随机选择一个食物
        selected_food = random.choice(available_foods)
        
        # 获取备选食物（完全随机）
        alternative_foods = list(FoodItem.objects.filter(
            is_active=True
        ).exclude(id=selected_food.id).order_by('?')[:5])
        
        # 创建随机选择会话记录
        session = FoodRandomizationSession.objects.create(
            user=request.user,
            meal_type='mixed',
            cuisine_preference='mixed',
            status='completed',
            animation_duration=animation_duration,
            selected_food=selected_food,
            alternative_foods=[food.id for food in alternative_foods],
            completed_at=timezone.now()
        )
        
        # 创建历史记录
        FoodHistory.objects.create(
            user=request.user,
            food_item=selected_food,
            meal_type='mixed',
            session=session
        )
        
        # 构建响应数据
        response_data = {
            'success': True,
            'session_id': session.id,
            'selected_food': {
                'id': selected_food.id,
                'name': selected_food.name,
                'description': selected_food.description,
                'image_url': selected_food.image_url,
                'cuisine': selected_food.get_cuisine_display(),
                'difficulty': selected_food.get_difficulty_display(),
                'cooking_time': selected_food.cooking_time,
                'ingredients': selected_food.ingredients,
                'tags': selected_food.tags,
                'meal_types': selected_food.meal_types,
                'recipe_url': selected_food.recipe_url,
                'popularity_score': selected_food.popularity_score
            },
            'alternative_foods': [
                {
                    'id': food.id,
                    'name': food.name,
                    'description': food.description,
                    'image_url': food.image_url,
                    'cuisine': food.get_cuisine_display(),
                    'difficulty': food.get_difficulty_display(),
                    'cooking_time': food.cooking_time
                }
                for food in alternative_foods
            ],
            'message': f'纯随机为您选择了 {selected_food.name}'
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"纯随机食物选择失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'纯随机选择失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_food_history_api(request):
    """获取食物历史记录API - 使用真实数据"""
    try:
        # 获取用户的历史记录，按时间倒序排列
        history_records = FoodHistory.objects.filter(
            user=request.user
        ).select_related('food_item').order_by('-created_at')[:20]  # 最近20条记录
        
        history_data = []
        for record in history_records:
            history_data.append({
                'id': record.id,
                'food_name': record.food_item.name,
                'food_description': record.food_item.description,
                'food_image_url': record.food_item.image_url,
                'cuisine': record.food_item.get_cuisine_display(),
                'meal_type': record.get_meal_type_display(),
                'selected_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'rating': record.rating if hasattr(record, 'rating') else None,
                'comment': record.feedback if hasattr(record, 'feedback') else '',
                'is_cooked': record.was_cooked if hasattr(record, 'was_cooked') else False,
                'session_id': record.session.id if record.session else None
            })
        
        return JsonResponse({
            'success': True,
            'history': history_data,
            'total_count': len(history_data)
        })
        
    except Exception as e:
        print(f"获取食物历史记录失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取历史记录失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def rate_food_api(request):
    """评价食物API - 使用真实数据"""
    try:
        data = json.loads(request.body)
        food_id = data.get('food_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        is_cooked = data.get('is_cooked', False)
        session_id = data.get('session_id')
        
        # 验证评分范围
        if rating is not None and (rating < 1 or rating > 5):
            return JsonResponse({
                'success': False,
                'error': '评分必须在1-5之间'
            })
        
        # 查找对应的历史记录
        history_record = None
        if session_id:
            history_record = FoodHistory.objects.filter(
                user=request.user,
                session__id=session_id
            ).first()
        elif food_id:
            history_record = FoodHistory.objects.filter(
                user=request.user,
                food_item_id=food_id
            ).order_by('-created_at').first()
        
        if history_record:
            # 更新历史记录
            if rating is not None:
                history_record.rating = rating
            if comment:
                history_record.feedback = comment
            if is_cooked is not None:
                history_record.was_cooked = is_cooked
            history_record.save()
            
            # 更新食物的受欢迎度评分
            if rating is not None and food_id:
                try:
                    food_item = FoodItem.objects.get(id=food_id)
                    # 计算新的受欢迎度评分（简单平均）
                    all_ratings = FoodHistory.objects.filter(
                        food_item=food_item,
                        rating__isnull=False
                    ).values_list('rating', flat=True)
                    
                    if all_ratings:
                        avg_rating = sum(all_ratings) / len(all_ratings)
                        food_item.popularity_score = avg_rating / 5.0  # 转换为0-1范围
                        food_item.save()
                except FoodItem.DoesNotExist:
                    pass
            
            return JsonResponse({
                'success': True,
                'message': '评价保存成功',
                'updated_record': {
                    'id': history_record.id,
                    'rating': history_record.rating,
                    'comment': history_record.feedback,
                    'is_cooked': history_record.was_cooked
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '未找到对应的历史记录'
            })
        
    except Exception as e:
        print(f"评价食物失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'评价保存失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_checkin_calendar_api(request):
    """获取打卡日历数据"""
    try:
        # 原有的函数体内容
        pass
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

# 用户资料相关API

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_user_profile_api(request, user_id):
    """获取用户资料信息"""
    try:
        user = get_object_or_404(User, id=user_id)
        profile = Profile.objects.filter(user=user).first()
        membership = UserMembership.objects.filter(user=user).first()
        theme = UserTheme.objects.filter(user=user).first()
        
        # 获取用户标签（基于用户行为和偏好）
        tags = []
        
        # 基于会员类型添加标签
        if membership and membership.membership_type != 'free':
            tags.append(f'💎 {membership.get_membership_type_display()}')
        
        # 基于主题模式添加标签
        if theme:
            mode_emojis = {
                'work': '💻',
                'life': '🌱',
                'training': '💪',
                'emo': '🎭'
            }
            tags.append(f"{mode_emojis.get(theme.mode, '🎯')} {theme.get_mode_display()}")
        
        # 基于用户活跃度添加标签
        if user.is_staff:
            tags.append('👑 管理员')
        
        # 基于注册时间添加标签
        days_since_joined = (timezone.now() - user.date_joined).days
        if days_since_joined > 365:
            tags.append('🎂 老用户')
        elif days_since_joined > 30:
            tags.append('🌟 活跃用户')
        else:
            tags.append('🆕 新用户')
        
        data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
            'avatar_url': profile.avatar.url if profile and profile.avatar else None,
            'bio': profile.bio if profile else '',
            'phone': profile.phone if profile else '',
            'membership_type': membership.get_membership_type_display() if membership else '免费用户',
            'theme_mode': theme.get_mode_display() if theme else '默认模式',
            'tags': tags,
            'is_online': False,  # 将在WebSocket中更新
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_chat_room_participants_api(request, room_id):
    """获取聊天室参与者信息"""
    try:
        room = get_object_or_404(ChatRoom, room_id=room_id)
        
        participants = []
        
        # 获取用户1信息
        user1_data = get_user_profile_data(room.user1)
        participants.append(user1_data)
        
        # 获取用户2信息（如果存在）
        if room.user2:
            user2_data = get_user_profile_data(room.user2)
            participants.append(user2_data)
        
        return JsonResponse({
            'success': True,
            'data': {
                'room_id': room_id,
                'participants': participants,
                'status': room.get_status_display(),
                'created_at': room.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def get_user_profile_data(user):
    """获取用户资料数据的辅助函数"""
    profile = Profile.objects.filter(user=user).first()
    membership = UserMembership.objects.filter(user=user).first()
    theme = UserTheme.objects.filter(user=user).first()
    
    # 获取用户标签
    tags = []
    
    if membership and membership.membership_type != 'free':
        tags.append(f'💎 {membership.get_membership_type_display()}')
    
    if theme:
        mode_emojis = {
            'work': '💻',
            'life': '🌱',
            'training': '💪',
            'emo': '🎭'
        }
        tags.append(f"{mode_emojis.get(theme.mode, '🎯')} {theme.get_mode_display()}")
    
    if user.is_staff:
        tags.append('👑 管理员')
    
    days_since_joined = (timezone.now() - user.date_joined).days
    if days_since_joined > 365:
        tags.append('🎂 老用户')
    elif days_since_joined > 30:
        tags.append('🌟 活跃用户')
    else:
        tags.append('🆕 新用户')
    
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'display_name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'avatar_url': profile.avatar.url if profile and profile.avatar else None,
        'bio': profile.bio if profile else '',
        'membership_type': membership.get_membership_type_display() if membership else '免费用户',
        'theme_mode': theme.get_mode_display() if theme else '默认模式',
        'tags': tags,
        'is_online': False,  # 将在WebSocket中更新
    }

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_checkin_calendar_api(request):
    """获取打卡日历数据"""
    try:
        from .models import CheckInCalendar
        
        checkin_type = request.GET.get('type', 'diary')
        year = int(request.GET.get('year', datetime.now().year))
        month = int(request.GET.get('month', datetime.now().month))
        
        # 获取指定月份的数据
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # 从数据库获取打卡数据
        checkins = CheckInCalendar.objects.filter(
            user=request.user,
            calendar_type=checkin_type,
            date__range=[start_date.date(), end_date.date()]
        ).select_related('detail')
        
        # 构建日历数据
        calendar_data = {}
        for checkin in checkins:
            date_str = checkin.date.strftime('%Y-%m-%d')
            calendar_data[date_str] = {
                'id': checkin.id,
                'status': checkin.status,
                'mood': getattr(checkin.detail, 'mood', None) if hasattr(checkin, 'detail') else None,
                'note': getattr(checkin.detail, 'note', '') if hasattr(checkin, 'detail') else ''
            }
        
        # 计算连续打卡
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        # 获取所有打卡记录，按日期排序
        all_checkins = CheckInCalendar.objects.filter(
            user=request.user,
            calendar_type=checkin_type
        ).order_by('date')
        
        if all_checkins.exists():
            last_checkin_date = None
            for checkin in all_checkins:
                if last_checkin_date is None:
                    temp_streak = 1
                elif (checkin.date - last_checkin_date).days == 1:
                    temp_streak += 1
                else:
                    temp_streak = 1
                
                longest_streak = max(longest_streak, temp_streak)
                last_checkin_date = checkin.date
            
            # 计算当前连续打卡
            today = datetime.now().date()
            if last_checkin_date == today:
                current_streak = temp_streak
            elif (today - last_checkin_date).days == 1:
                current_streak = temp_streak
            else:
                current_streak = 0
        
        # 月度统计
        monthly_stats = {
            'total_days': len(calendar_data),
            'completed_days': len([c for c in calendar_data.values() if c['status'] == 'completed']),
            'rest_days': len([c for c in calendar_data.values() if c['status'] == 'rest']),
            'missed_days': (end_date.date() - start_date.date()).days + 1 - len(calendar_data)
        }
        
        return JsonResponse({
            'success': True,
            'calendar_data': calendar_data,
            'streak': {
                'current': current_streak,
                'longest': longest_streak
            },
            'monthly_stats': monthly_stats
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取打卡日历失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def number_match_api(request):
    """数字匹配API - 用户输入四个数字匹配相同数字的人"""
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    try:
        data = json.loads(request.body)
        input_number = data.get('number', '').strip()
        
        # 验证输入
        if not input_number or len(input_number) != 4 or not input_number.isdigit():
            return JsonResponse({
                'success': False,
                'error': '请输入4位数字'
            }, status=400, content_type='application/json', headers=response_headers)
        
        # 检查用户是否已经在匹配中
        existing_match = UserOnlineStatus.objects.filter(
            user=request.user,
            is_online=True,
            match_number__isnull=False
        ).first()
        
        if existing_match:
            return JsonResponse({
                'success': False,
                'error': '您已经在匹配中，请先取消当前匹配'
            }, status=400, content_type='application/json', headers=response_headers)
        
        # 查找是否有其他用户输入了相同的数字
        matching_user = UserOnlineStatus.objects.filter(
            match_number=input_number,
            is_online=True,
            user__is_active=True
        ).exclude(user=request.user).first()
        
        if matching_user:
            # 找到匹配，创建聊天室
            chat_room = ChatRoom.objects.create(
                room_id=f"match-{uuid.uuid4()}",
                user1=request.user,
                user2=matching_user.user,
                created_at=timezone.now()
            )
            
            # 清除匹配状态
            UserOnlineStatus.objects.filter(
                user__in=[request.user, matching_user.user]
            ).update(match_number=None)
            
            return JsonResponse({
                'success': True,
                'matched': True,
                'room_id': chat_room.room_id,
                'matched_user': {
                    'username': matching_user.user.username,
                    'display_name': get_user_profile_data(matching_user.user)['display_name']
                },
                'message': f'匹配成功！您与 {matching_user.user.username} 开始聊天'
            }, content_type='application/json', headers=response_headers)
        else:
            # 没有找到匹配，记录当前用户的匹配数字
            UserOnlineStatus.objects.update_or_create(
                user=request.user,
                defaults={
                    'is_online': True,
                    'match_number': input_number,
                    'last_seen': timezone.now()
                }
            )
            
            return JsonResponse({
                'success': True,
                'matched': False,
                'message': f'正在等待输入 {input_number} 的用户...'
            }, content_type='application/json', headers=response_headers)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400, content_type='application/json', headers=response_headers)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'匹配失败: {str(e)}'
        }, status=500, content_type='application/json', headers=response_headers)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def cancel_number_match_api(request):
    """取消数字匹配API"""
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '请先登录',
            'redirect_url': '/users/login/'
        }, status=401, content_type='application/json', headers=response_headers)
    
    try:
        # 清除用户的匹配状态
        UserOnlineStatus.objects.filter(
            user=request.user
        ).update(match_number=None)
        
        return JsonResponse({
            'success': True,
            'message': '已取消匹配'
        }, content_type='application/json', headers=response_headers)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'取消匹配失败: {str(e)}'
        }, status=500, content_type='application/json', headers=response_headers)