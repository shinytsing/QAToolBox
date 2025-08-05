from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import requests
from django.utils import timezone
from datetime import datetime
from django.db import models
import uuid
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import time

from .models import LifeDiaryEntry, LifeStatistics, LifeGoal, LifeGoalProgress
from .models import ChatRoom, HeartLinkRequest, UserOnlineStatus, ChatMessage

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

# 自动求职机相关模型导入
from .models import JobSearchRequest, JobApplication, JobSearchProfile, JobSearchStatistics
from .services.job_search_service import JobSearchService

@login_required
def test_case_generator(request):
    """测试用例生成器页面"""
    return render(request, 'tools/test_case_generator.html')

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
    """健身中心页面"""
    return render(request, 'tools/fitness_center.html')

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
        if request.user not in chat_room.participants:
            return redirect('heart_link')
    except ChatRoom.DoesNotExist:
        return redirect('heart_link')
    
    context = {
        'chat_room': chat_room,
        'other_user': chat_room.user2 if request.user == chat_room.user1 else chat_room.user1
    }
    return render(request, 'tools/heart_link_chat.html', context)

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
        
        # 创建新的日记记录
        today = timezone.now().date()
        diary_entry = LifeDiaryEntry.objects.create(
            user=request.user,
            date=today,
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
    """健身中心API"""
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
        # 检查房间中的用户是否都活跃（更宽松的条件）
        # 只有在两个用户都超过20分钟不活跃时才结束聊天室
        user1_inactive = False
        user2_inactive = False
        
        # 检查用户1是否超过20分钟不活跃
        try:
            online_status1 = UserOnlineStatus.objects.filter(user=room.user1).first()
            if online_status1 and online_status1.last_seen:
                user1_inactive = timezone.now() - online_status1.last_seen > timedelta(minutes=20)
            elif room.user1.last_login:
                user1_inactive = timezone.now() - room.user1.last_login > timedelta(minutes=30)
        except:
            pass
        
        # 检查用户2是否超过20分钟不活跃
        if room.user2:
            try:
                online_status2 = UserOnlineStatus.objects.filter(user=room.user2).first()
                if online_status2 and online_status2.last_seen:
                    user2_inactive = timezone.now() - online_status2.last_seen > timedelta(minutes=20)
                elif room.user2.last_login:
                    user2_inactive = timezone.now() - room.user2.last_login > timedelta(minutes=30)
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
            # 清理过期的请求
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
            
            # 清理过期请求
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
            heart_link_request = HeartLinkRequest.objects.get(
                requester=request.user,
                status='pending'
            )
            heart_link_request.status = 'cancelled'
            heart_link_request.save()
            return JsonResponse({
                'success': True,
                'message': '已取消匹配请求'
            }, content_type='application/json', headers=response_headers)
        except HeartLinkRequest.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '没有找到待处理的请求'
            }, status=404, content_type='application/json', headers=response_headers)
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
        # 只在必要时清理过期请求，避免过度清理
        # 清理超过10分钟的pending请求（只清理真正过期的）
        from datetime import timedelta
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
            # 只有在请求确实超过10分钟时才标记为过期
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
                    if request.user not in [chat_room.user1, chat_room.user2]:
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
        if request.user not in [chat_room.user1, chat_room.user2]:
            return JsonResponse({
                'success': False,
                'error': '您没有权限访问此聊天室'
            }, status=403, content_type='application/json', headers=response_headers)
        
        # 获取消息
        messages = ChatMessage.objects.filter(room=chat_room).order_by('created_at')
        
        # 格式化消息
        message_list = []
        for message in messages:
            message_list.append({
                'id': message.id,
                'sender': message.sender.username,
                'content': message.content,
                'message_type': message.message_type,
                'file_url': message.file_url,
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
            if request.user not in [chat_room.user1, chat_room.user2]:
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
            UserOnlineStatus.objects.update_or_create(
                user=request.user,
                defaults={
                    'last_seen': timezone.now(),
                    'status': status
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': '在线状态已更新'
            }, content_type='application/json', headers=response_headers)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'更新在线状态失败: {str(e)}'
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
        if request.user not in [chat_room.user1, chat_room.user2]:
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
        
        # 验证URL格式
        if 'douyin.com' not in up主_url:
            return JsonResponse({
                'success': False,
                'error': '请输入有效的抖音UP主主页URL'
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
@require_http_methods(["GET"])
def test_heart_link_api(request):
    """测试心动链接功能API"""
    try:
        # 检查用户认证
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': '请先登录'
            }, status=401, content_type='application/json')
        
        # 获取统计数据
        total_requests = HeartLinkRequest.objects.count()
        pending_requests = HeartLinkRequest.objects.filter(status='pending').count()
        matched_requests = HeartLinkRequest.objects.filter(status='matched').count()
        expired_requests = HeartLinkRequest.objects.filter(status='expired').count()
        
        # 获取用户自己的请求
        user_requests = HeartLinkRequest.objects.filter(requester=request.user).order_by('-created_at')
        user_request_count = user_requests.count()
        latest_request = user_requests.first()
        
        # 检查是否有其他等待中的用户
        other_pending_users = HeartLinkRequest.objects.filter(
            status='pending'
        ).exclude(requester=request.user).count()
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_requests': total_requests,
                'pending_requests': pending_requests,
                'matched_requests': matched_requests,
                'expired_requests': expired_requests,
                'user_request_count': user_request_count,
                'other_pending_users': other_pending_users,
                'latest_request': {
                    'id': latest_request.id if latest_request else None,
                    'status': latest_request.status if latest_request else None,
                    'created_at': latest_request.created_at.strftime('%Y-%m-%d %H:%M:%S') if latest_request else None,
                    'is_expired': latest_request.is_expired if latest_request else None
                } if latest_request else None
            }
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'测试失败: {str(e)}'
        }, status=500, content_type='application/json')

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

@login_required
def vanity_os_dashboard(request):
    """VanityOS 主仪表盘页面"""
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


@login_required
def test_desire_todo_enhanced_view(request):
    """欲望代办和反程序员形象测试页面"""
    return render(request, 'test_desire_todo_enhanced.html')


def test_desire_todo_public_view(request):
    """欲望代办和反程序员形象测试页面（公开）"""
    return render(request, 'test_desire_todo_enhanced.html')


def test_api_public_view(request):
    """API测试页面（公开）"""
    return render(request, 'test_api_public.html')


# VanityOS API 视图

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_vanity_wealth_api(request):
    """获取虚拟财富API"""
    try:
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
@login_required
def add_sin_points_api(request):
    """添加罪恶积分API"""
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
        
        # 检查消息时间（只能删除2分钟内的消息）
        time_diff = timezone.now() - message.created_at
        if time_diff.total_seconds() > 120:  # 2分钟
            return JsonResponse({
                'success': False,
                'error': '只能删除2分钟内的消息'
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
@require_http_methods(["POST"])
@login_required
def travel_guide_api(request):
    """旅游攻略API"""
    try:
        data = json.loads(request.body)
        destination = data.get('destination', '').strip()
        travel_style = data.get('travel_style', 'general')
        budget_range = data.get('budget_range', 'medium')
        travel_duration = data.get('travel_duration', '3-5天')
        interests = data.get('interests', [])
        
        if not destination:
            return JsonResponse({'error': '请输入目的地'}, status=400)
        
        # 生成旅游攻略内容
        guide_content = generate_travel_guide(
            destination, travel_style, budget_range, 
            travel_duration, interests
        )
        
        # 过滤掉TravelGuide模型中不存在的字段
        valid_fields = {
            'must_visit_attractions', 'food_recommendations', 'transportation_guide',
            'hidden_gems', 'weather_info', 'best_time_to_visit', 'budget_estimate', 'travel_tips',
            'detailed_guide', 'daily_schedule', 'activity_timeline', 'cost_breakdown'
        }
        filtered_content = {k: v for k, v in guide_content.items() if k in valid_fields}
        
        # 保存到数据库
        travel_guide = TravelGuide.objects.create(
            user=request.user,
            destination=destination,
            travel_style=travel_style,
            budget_range=budget_range,
            travel_duration=travel_duration,
            interests=interests,
            **filtered_content
        )
        
        return JsonResponse({
            'success': True,
            'guide_id': travel_guide.id,
            'guide': {
                'destination': travel_guide.destination,
                'must_visit_attractions': travel_guide.must_visit_attractions,
                'food_recommendations': travel_guide.food_recommendations,
                'transportation_guide': travel_guide.transportation_guide,
                'hidden_gems': travel_guide.hidden_gems,
                'weather_info': travel_guide.weather_info,
                'best_time_to_visit': travel_guide.best_time_to_visit,
                'budget_estimate': travel_guide.budget_estimate,
                'travel_tips': travel_guide.travel_tips,
                'detailed_guide': travel_guide.detailed_guide,
                'daily_schedule': travel_guide.daily_schedule,
                'activity_timeline': travel_guide.activity_timeline,
                'cost_breakdown': travel_guide.cost_breakdown,
                'created_at': travel_guide.created_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
        
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
            guides_data.append({
                'id': guide.id,
                'destination': guide.destination,
                'travel_style': guide.travel_style,
                'budget_range': guide.budget_range,
                'travel_duration': guide.travel_duration,
                'attractions_count': guide.get_attractions_count(),
                'food_count': guide.get_food_count(),
                'hidden_gems_count': guide.get_hidden_gems_count(),
                'is_favorite': guide.is_favorite,
                'created_at': guide.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        
        return JsonResponse({
            'success': True,
            'guides': guides_data
        })
        
    except Exception as e:
        print(f"获取旅游攻略列表失败: {str(e)}")
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
        
        # 生成格式化的攻略内容
        formatted_content = format_travel_guide_for_export(guide)
        
        # 生成PDF文件
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import os
            import tempfile
            
            # 创建临时PDF文件
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                pdf_path = tmp_file.name
            
            # 创建PDF文档
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            story = []
            
            # 获取样式
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1,  # 居中
                textColor=colors.darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.darkgreen
            )
            
            normal_style = styles['Normal']
            
            # 添加标题
            story.append(Paragraph(f"🗺️ {guide.destination}旅游攻略", title_style))
            story.append(Spacer(1, 20))
            
            # 添加基本信息
            story.append(Paragraph("📍 基本信息", heading_style))
            info_data = [
                ['目的地', guide.destination],
                ['旅行风格', guide.travel_style],
                ['预算范围', guide.budget_range],
                ['旅行时长', guide.travel_duration],
                ['兴趣偏好', ', '.join(guide.interests) if guide.interests else '无']
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # 添加每日行程
            if guide.daily_schedule:
                story.append(Paragraph("🗓️ 每日行程安排", heading_style))
                for day_schedule in guide.daily_schedule:
                    day_title = f"第{day_schedule.get('day', '')}天"
                    story.append(Paragraph(day_title, heading_style))
                    
                    # 收集当天所有活动
                    all_activities = []
                    for time_slot in ['morning', 'afternoon', 'evening', 'night']:
                        for activity in day_schedule.get(time_slot, []):
                            all_activities.append([
                                activity.get('time', ''),
                                activity.get('activity', ''),
                                activity.get('location', ''),
                                activity.get('cost', '')
                            ])
                    
                    if all_activities:
                        activity_table = Table(all_activities, colWidths=[1*inch, 2.5*inch, 1.5*inch, 1*inch])
                        activity_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                        ]))
                        story.append(activity_table)
                    
                    if day_schedule.get('accommodation'):
                        story.append(Paragraph(f"🏨 住宿: {day_schedule['accommodation']}", normal_style))
                    
                    story.append(Spacer(1, 10))
            
            # 添加其他信息
            if guide.must_visit_attractions:
                story.append(Paragraph("🎯 必去景点", heading_style))
                for i, attraction in enumerate(guide.must_visit_attractions, 1):
                    if isinstance(attraction, dict):
                        story.append(Paragraph(f"{i}. {attraction.get('name', '')} - {attraction.get('description', '')}", normal_style))
                    else:
                        story.append(Paragraph(f"{i}. {attraction}", normal_style))
                story.append(Spacer(1, 15))
            
            if guide.food_recommendations:
                story.append(Paragraph("🍜 美食推荐", heading_style))
                for i, food in enumerate(guide.food_recommendations, 1):
                    if isinstance(food, dict):
                        story.append(Paragraph(f"{i}. {food.get('name', '')} - {food.get('specialty', '')}", normal_style))
                    else:
                        story.append(Paragraph(f"{i}. {food}", normal_style))
                story.append(Spacer(1, 15))
            
            if guide.travel_tips:
                story.append(Paragraph("💡 旅行贴士", heading_style))
                for i, tip in enumerate(guide.travel_tips, 1):
                    story.append(Paragraph(f"{i}. {tip}", normal_style))
                story.append(Spacer(1, 15))
            
            # 生成PDF
            doc.build(story)
            
            # 读取生成的PDF文件
            with open(pdf_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
            
            # 删除临时文件
            os.unlink(pdf_path)
            
            # 创建HTTP响应
            from django.http import HttpResponse
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{guide.destination}_旅游攻略.pdf"'
            
            # 标记为已导出
            guide.is_exported = True
            guide.save()
            
            return response
            
        except ImportError:
            # 如果没有安装reportlab，返回文本格式
            return JsonResponse({
                'success': True,
                'message': '攻略导出成功（文本格式）',
                'guide_id': guide_id,
                'formatted_content': formatted_content
            })
        
    except Exception as e:
        print(f"导出攻略失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'导出失败: {str(e)}'
        }, status=500)


def format_travel_guide_for_export(guide):
    """格式化旅游攻略用于导出"""
    content = []
    
    # 标题
    content.append(f"🗺️{guide.destination}旅游攻略")
    content.append("=" * 50)
    
    # 基本信息
    content.append(f"📍目的地: {guide.destination}")
    content.append(f"🎯旅行风格: {guide.travel_style}")
    content.append(f"💰预算范围: {guide.budget_range}")
    content.append(f"⏰旅行时长: {guide.travel_duration}")
    content.append(f"🎨兴趣偏好: {', '.join(guide.interests) if guide.interests else '无'}")
    content.append("")
    
    # 路线规划
    if guide.daily_schedule:
        content.append("🚥路线规划")
        for day_schedule in guide.daily_schedule:
            day_activities = []
            if day_schedule.get('morning'):
                day_activities.extend([activity.get('activity', '') for activity in day_schedule['morning']])
            if day_schedule.get('afternoon'):
                day_activities.extend([activity.get('activity', '') for activity in day_schedule['afternoon']])
            if day_schedule.get('evening'):
                day_activities.extend([activity.get('activity', '') for activity in day_schedule['evening']])
            
            if day_activities:
                content.append(f"🚥Day{day_schedule.get('day', '')}: {'—'.join(day_activities)}")
        content.append("")
    
    # 住宿推荐
    if hasattr(guide, 'accommodation_data') and guide.accommodation_data:
        content.append("🏠住宿推荐")
        for hotel in guide.accommodation_data.get('hotels', []):
            content.append(f"📍{hotel.get('name', '')}")
            content.append(f"推荐理由: {hotel.get('recommendation', '')}")
            content.append("")
    
    # 必去景点
    if guide.must_visit_attractions:
        content.append("🎯必去景点")
        for i, attraction in enumerate(guide.must_visit_attractions, 1):
            if isinstance(attraction, dict):
                content.append(f"{i}. {attraction.get('name', '')} - {attraction.get('description', '')}")
            else:
                content.append(f"{i}. {attraction}")
        content.append("")
    
    # 美食推荐
    if guide.food_recommendations:
        content.append("🍜美食推荐")
        for i, food in enumerate(guide.food_recommendations, 1):
            if isinstance(food, dict):
                content.append(f"{i}. {food.get('name', '')} - {food.get('specialty', '')}")
            else:
                content.append(f"{i}. {food}")
        content.append("")
    
    # 交通指南
    if guide.transportation_guide:
        content.append("🚗交通指南")
        if isinstance(guide.transportation_guide, dict):
            for key, value in guide.transportation_guide.items():
                content.append(f"• {key}: {value}")
        content.append("")
    
    # 预算估算
    if guide.budget_estimate:
        content.append("💰预算估算")
        if isinstance(guide.budget_estimate, dict):
            for budget_type, amount in guide.budget_estimate.items():
                content.append(f"• {budget_type}: {amount}")
        content.append("")
    
    # 旅行贴士
    if guide.travel_tips:
        content.append("💡旅行贴士")
        for i, tip in enumerate(guide.travel_tips, 1):
            content.append(f"{i}. {tip}")
        content.append("")
    
    # 最佳旅行时间
    if guide.best_time_to_visit:
        content.append("📅最佳旅行时间")
        content.append(guide.best_time_to_visit)
        content.append("")
    
    # 费用明细
    if guide.cost_breakdown:
        content.append("💸费用明细")
        cost_data = guide.cost_breakdown
        if isinstance(cost_data, dict):
            total_cost = cost_data.get('total_cost', 0)
            content.append(f"总费用: {total_cost}元")
            
            for category, details in cost_data.items():
                if category != 'total_cost' and isinstance(details, dict):
                    content.append(f"• {details.get('description', category)}: {details.get('total_cost', 0)}元")
        content.append("")
    
    return "\n".join(content)


def generate_travel_guide(destination, travel_style, budget_range, travel_duration, interests):
    """生成旅游攻略内容"""
    try:
        # 导入旅游数据服务
        from .services.travel_data_service import TravelDataService
        
        # 创建数据服务实例
        travel_service = TravelDataService()
        
        # 获取真实旅游数据
        guide_data = travel_service.get_travel_guide_data(
            destination=destination,
            travel_style=travel_style,
            budget_range=budget_range,
            travel_duration=travel_duration,
            interests=interests or []
        )
        
        return guide_data
        
    except Exception as e:
        print(f"获取旅游数据失败: {e}")
        
        # 如果获取真实数据失败，返回基础模拟数据
        return {
            'must_visit_attractions': [
                f"{destination}著名景点1",
                f"{destination}著名景点2", 
                f"{destination}著名景点3",
                f"{destination}著名景点4",
                f"{destination}著名景点5"
            ],
            'food_recommendations': [
                f"{destination}特色美食1",
                f"{destination}特色美食2",
                f"{destination}特色美食3",
                f"{destination}特色美食4"
            ],
            'transportation_guide': {
                "飞机": f"从主要城市可直飞{destination}",
                "火车": f"可乘坐高铁或普通列车到达{destination}",
                "汽车": f"可乘坐长途汽车到达{destination}",
                "市内交通": "地铁、公交、出租车都很方便"
            },
            'hidden_gems': [
                f"{destination}小众景点1",
                f"{destination}小众景点2",
                f"{destination}小众景点3"
            ],
            'weather_info': {
                "春季": "温度适宜，适合户外活动",
                "夏季": "天气炎热，注意防晒",
                "秋季": "天高气爽，是旅游的好时节",
                "冬季": "天气寒冷，注意保暖"
            },
            'best_time_to_visit': f"建议在春秋季节前往{destination}，天气适宜，景色优美。",
            'budget_estimate': {
                "经济型": "人均2000-3000元",
                "舒适型": "人均4000-6000元", 
                "豪华型": "人均8000-12000元"
            },
            'travel_tips': [
                "建议提前预订酒店和机票",
                "准备防晒和雨具",
                "注意当地风俗习惯",
                "保管好随身物品",
                "建议购买旅游保险"
            ]
        }


# ==================== 自动求职机相关视图 ====================

@login_required
def job_search_machine(request):
    """自动求职机页面"""
    return render(request, 'tools/job_search_machine.html')


@login_required
def job_search_profile(request):
    """求职者资料页面"""
    return render(request, 'tools/job_search_profile.html')


@login_required
def job_search_dashboard(request):
    """求职仪表盘页面"""
    return render(request, 'tools/job_search_dashboard.html')


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_job_search_request_api(request):
    """创建求职请求API"""
    try:
        data = json.loads(request.body)
        
        # 验证必填字段
        required_fields = ['job_title', 'location', 'min_salary', 'max_salary']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'请填写{field}字段'
                })
        
        # 创建求职请求
        job_service = JobSearchService()
        job_request = job_service.create_job_search_request(
            user=request.user,
            job_title=data['job_title'],
            location=data['location'],
            min_salary=int(data['min_salary']),
            max_salary=int(data['max_salary']),
            job_type=data.get('job_type', 'full_time'),
            experience_level=data.get('experience_level', '1-3'),
            keywords=data.get('keywords', []),
            company_size=data.get('company_size', ''),
            industry=data.get('industry', ''),
            education_level=data.get('education_level', ''),
            auto_apply=data.get('auto_apply', True),
            max_applications=int(data.get('max_applications', 50)),
            application_interval=int(data.get('application_interval', 30))
        )
        
        return JsonResponse({
            'success': True,
            'message': '求职请求创建成功',
            'request_id': job_request.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'创建求职请求失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def start_job_search_api(request):
    """开始自动求职API"""
    try:
        data = json.loads(request.body)
        request_id = data.get('request_id')
        
        if not request_id:
            return JsonResponse({
                'success': False,
                'message': '请提供求职请求ID'
            })
        
        # 获取求职请求
        try:
            job_request = JobSearchRequest.objects.get(id=request_id, user=request.user)
        except JobSearchRequest.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '求职请求不存在'
            })
        
        # 开始自动求职
        job_service = JobSearchService()
        result = job_service.start_auto_job_search(job_request)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'开始自动求职失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_job_search_requests_api(request):
    """获取求职请求列表API"""
    try:
        requests = JobSearchRequest.objects.filter(user=request.user).order_by('-created_at')
        
        requests_data = []
        for req in requests:
            requests_data.append({
                'id': req.id,
                'job_title': req.job_title,
                'location': req.location,
                'salary_range': req.get_salary_range(),
                'status': req.status,
                'total_jobs_found': req.total_jobs_found,
                'total_applications_sent': req.total_applications_sent,
                'success_rate': req.success_rate,
                'progress_percentage': req.get_progress_percentage(),
                'created_at': req.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'completed_at': req.completed_at.strftime('%Y-%m-%d %H:%M:%S') if req.completed_at else None
            })
        
        return JsonResponse({
            'success': True,
            'data': requests_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取求职请求失败: {str(e)}'
        })


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


def generate_travel_guide(destination, travel_style, budget_range, travel_duration, interests):
    """生成旅游攻略内容"""
    try:
        # 导入旅游数据服务
        from .services.travel_data_service import TravelDataService
        
        # 创建数据服务实例
        travel_service = TravelDataService()
        
        # 获取真实旅游数据
        guide_data = travel_service.get_travel_guide_data(
            destination=destination,
            travel_style=travel_style,
            budget_range=budget_range,
            travel_duration=travel_duration,
            interests=interests or []
        )
        
        return guide_data
        
    except Exception as e:
        print(f"获取旅游数据失败: {e}")
        
        # 如果获取真实数据失败，返回基础模拟数据
        return {
            'must_visit_attractions': [
                f"{destination}著名景点1",
                f"{destination}著名景点2", 
                f"{destination}著名景点3",
                f"{destination}著名景点4",
                f"{destination}著名景点5"
            ],
            'food_recommendations': [
                f"{destination}特色美食1",
                f"{destination}特色美食2",
                f"{destination}特色美食3",
                f"{destination}特色美食4"
            ],
            'transportation_guide': {
                "飞机": f"从主要城市可直飞{destination}",
                "火车": f"可乘坐高铁或普通列车到达{destination}",
                "汽车": f"可乘坐长途汽车到达{destination}",
                "市内交通": "地铁、公交、出租车都很方便"
            },
            'hidden_gems': [
                f"{destination}小众景点1",
                f"{destination}小众景点2",
                f"{destination}小众景点3"
            ],
            'weather_info': {
                "春季": "温度适宜，适合户外活动",
                "夏季": "天气炎热，注意防晒",
                "秋季": "天高气爽，是旅游的好时节",
                "冬季": "天气寒冷，注意保暖"
            },
            'best_time_to_visit': f"建议在春秋季节前往{destination}，天气适宜，景色优美。",
            'budget_estimate': {
                "经济型": "人均2000-3000元",
                "舒适型": "人均4000-6000元", 
                "豪华型": "人均8000-12000元"
            },
            'travel_tips': [
                "建议提前预订酒店和机票",
                "准备防晒和雨具",
                "注意当地风俗习惯",
                "保管好随身物品",
                "建议购买旅游保险"
            ]
        }


