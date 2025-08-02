from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import requests

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
    """生活日记页面"""
    return render(request, 'tools/life_diary.html')

@login_required
def emo_diary(request):
    """Emo情感日记页面"""
    return render(request, 'tools/emo_diary.html')

@login_required
def creative_writer(request):
    """创意文案生成器页面"""
    return render(request, 'tools/creative_writer.html')

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
            return JsonResponse({'error': 'API密钥未配置'}, status=500)
        
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
            })
        else:
            return JsonResponse({
                'error': f'API调用失败: {response.status_code}'
            }, status=500)
            
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
            return JsonResponse({'error': 'API密钥未配置'}, status=500)
        
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
            })
        else:
            return JsonResponse({
                'error': f'API调用失败: {response.status_code}'
            }, status=500)
            
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
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '获取歌曲失败'
                    })
            
            elif action == 'playlist':
                # 获取模式所有歌曲
                tracks = free_music_api.get_music_by_mode(mode)
                return JsonResponse({
                    'success': True,
                    'data': tracks
                })
            
            elif action == 'search':
                # 搜索歌曲
                keyword = request.GET.get('keyword', '')
                if keyword:
                    songs = free_music_api.search_song(keyword, mode)
                    return JsonResponse({
                        'success': True,
                        'data': songs
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': '搜索关键词不能为空'
                    })
            
            elif action == 'modes':
                # 获取所有可用模式
                modes = free_music_api.get_available_modes()
                mode_info = []
                for mode_name in modes:
                    mode_info.append(free_music_api.get_mode_info(mode_name))
                return JsonResponse({
                    'success': True,
                    'data': mode_info
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': '不支持的操作'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'服务器错误: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': '不支持的请求方法'
    })

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
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '获取下一首歌曲失败'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


# 社交媒体订阅相关API
@csrf_exempt
@require_http_methods(["POST"])
def add_social_subscription_api(request):
    """添加社交媒体订阅API"""
    try:
        data = json.loads(request.body)
        platform = data.get('platform')
        user_id = data.get('user_id')
        user_name = data.get('user_name', f'用户{user_id}')
        subscription_types = data.get('subscription_types', [])
        check_frequency = data.get('check_frequency', 15)
        
        if not platform or not user_id:
            return JsonResponse({
                'success': False,
                'error': '平台和用户ID不能为空'
            }, status=400)
        
        # 检查是否已存在相同订阅
        from apps.tools.models import SocialMediaSubscription
        existing = SocialMediaSubscription.objects.filter(
            user=request.user,
            platform=platform,
            target_user_id=user_id
        ).first()
        
        if existing:
            return JsonResponse({
                'success': False,
                'error': '该用户已订阅'
            }, status=400)
        
        # 创建新订阅
        subscription = SocialMediaSubscription.objects.create(
            user=request.user,
            platform=platform,
            target_user_id=user_id,
            target_user_name=user_name,
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
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_subscription_api(request):
    """更新订阅状态API"""
    try:
        data = json.loads(request.body)
        subscription_id = data.get('subscription_id')
        action = data.get('action')  # 'toggle', 'delete'
        
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
            }, status=404)
        
        if action == 'toggle':
            subscription.status = 'paused' if subscription.status == 'active' else 'active'
            subscription.save()
            
            return JsonResponse({
                'success': True,
                'status': subscription.status
            })
            
        elif action == 'delete':
            subscription.delete()
            
            return JsonResponse({
                'success': True,
                'message': '订阅已删除'
            })
        
        else:
            return JsonResponse({
                'success': False,
                'error': '无效的操作'
            }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_notifications_api(request):
    """获取通知列表API"""
    try:
        from apps.tools.models import SocialMediaNotification
        from django.db.models import Q
        
        # 获取过滤参数
        notification_type = request.GET.get('type', 'all')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # 构建查询
        notifications = SocialMediaNotification.objects.filter(
            subscription__user=request.user
        )
        
        if notification_type != 'all':
            notifications = notifications.filter(notification_type=notification_type)
        
        # 分页
        total_count = notifications.count()
        notifications = notifications[(page - 1) * page_size:page * page_size]
        
        notification_list = []
        for notif in notifications:
            notification_list.append({
                'id': notif.id,
                'subscription_id': notif.subscription.id,
                'type': notif.notification_type,
                'title': notif.title,
                'content': notif.content,
                'is_read': notif.is_read,
                'created_at': notif.created_at.isoformat(),
                'platform': notif.subscription.platform,
                'target_user_name': notif.subscription.target_user_name
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notification_list,
            'total_count': total_count,
            'page': page,
            'page_size': page_size
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def mark_notification_read_api(request):
    """标记通知为已读API"""
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        from apps.tools.models import SocialMediaNotification
        
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
            })
            
        except SocialMediaNotification.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '通知不存在'
            }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
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
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)