from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
import json
import math
import random
import logging
from functools import wraps

from .models import TimeCapsule, CapsuleUnlock, MemoryFragment, Achievement, ParallelMatch, User

# 设置日志
logger = logging.getLogger(__name__)

def handle_api_errors(func):
    """API错误处理装饰器"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"API错误 in {func.__name__}: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '服务器暂时不可用，请稍后重试',
                'error_code': 'INTERNAL_ERROR'
            }, status=500)
    return wrapper

def cache_response(timeout=300):
    """缓存响应装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # 只为GET请求缓存
            if request.method != 'GET':
                return func(request, *args, **kwargs)
            
            # 生成缓存键
            cache_key = f"time_capsule_{func.__name__}_{request.user.id if request.user.is_authenticated else 'anonymous'}"
            
            # 尝试从缓存获取
            cached_response = cache.get(cache_key)
            if cached_response:
                return JsonResponse(cached_response)
            
            # 执行原函数
            response = func(request, *args, **kwargs)
            
            # 缓存响应
            if response.status_code == 200:
                try:
                    response_data = json.loads(response.content)
                    cache.set(cache_key, response_data, timeout)
                except:
                    pass
            
            return response
        return wrapper
    return decorator


def time_capsule_diary(request):
    """时光胶囊日记主页面"""
    # 添加WebSocket连接状态检查
    websocket_available = hasattr(settings, 'CHANNEL_LAYERS')
    
    context = {
        'websocket_available': websocket_available,
        'api_timeout': 10000,  # 10秒超时
        'retry_attempts': 3,
    }
    
    return render(request, 'tools/time_capsule_diary.html', context)


@login_required
@csrf_exempt
@handle_api_errors
def create_time_capsule(request):
    """创建时光胶囊"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 数据验证
            if not data.get('content', '').strip():
                return JsonResponse({
                    'success': False,
                    'message': '内容不能为空'
                }, status=400)
            
            # 限制内容长度
            if len(data.get('content', '')) > 5000:
                return JsonResponse({
                    'success': False,
                    'message': '内容长度不能超过5000字符'
                }, status=400)
            
            # 创建胶囊
            capsule = TimeCapsule.objects.create(
                user=request.user,
                title=data.get('title', ''),
                content=data.get('content'),
                emotions=data.get('emotions', []),
                location=data.get('location'),
                weather=data.get('weather'),
                keywords=data.get('keywords', []),
                capsule_type=data.get('capsule_type', 'memory'),
                unlock_condition=data.get('unlock_condition', 'time'),
                unlock_time=datetime.fromisoformat(data.get('unlock_time')) if data.get('unlock_time') else None,
                unlock_location=data.get('unlock_location'),
                unlock_event=data.get('unlock_event', ''),
                visibility=data.get('visibility', 'private'),
                is_anonymous=data.get('is_anonymous', False),
                images=data.get('images', []),
                audio=data.get('audio', '')
            )
            
            # 清除相关缓存
            cache.delete(f"time_capsule_get_user_capsules_{request.user.id}")
            
            # 检查成就
            check_achievements(request.user)
            
            # 返回成就更新信息
            achievements = Achievement.objects.filter(user=request.user)
            achievement_list = []
            for achievement in achievements:
                achievement_list.append({
                    'type': achievement.achievement_type,
                    'name': achievement.get_achievement_type_display(),
                    'unlocked_at': achievement.unlocked_at.strftime('%Y-%m-%d'),
                    'progress': achievement.progress,
                    'unlocked': True
                })
            
            return JsonResponse({
                'success': True,
                'message': '时光胶囊创建成功！',
                'capsule_id': capsule.id,
                'achievements': achievement_list,
                'websocket_available': hasattr(settings, 'CHANNEL_LAYERS')
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '数据格式错误'
            }, status=400)
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': f'时间格式错误: {str(e)}'
            }, status=400)
        except Exception as e:
            logger.error(f"创建时光胶囊失败: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'创建失败: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': '请求方法不支持'}, status=405)


@login_required
@cache_response(timeout=60)  # 缓存1分钟
def get_user_capsules(request):
    """获取用户的胶囊列表"""
    try:
        # 使用select_related优化查询
        capsules = TimeCapsule.objects.filter(user=request.user).select_related('user').order_by('-created_at')
        
        capsule_list = []
        for capsule in capsules:
            # 检查解锁状态
            is_unlocked_by_user = CapsuleUnlock.objects.filter(
                capsule=capsule, 
                user=request.user
            ).exists()
            
            capsule_list.append({
                'id': capsule.id,
                'title': capsule.title,
                'content': capsule.content[:100] + '...' if len(capsule.content) > 100 else capsule.content,
                'emotions': capsule.emotions,
                'capsule_type': capsule.get_capsule_type_display(),
                'visibility': capsule.get_visibility_display(),
                'is_locked': capsule.is_locked,
                'is_unlocked': capsule.is_unlocked,
                'is_unlocked_by_user': is_unlocked_by_user,
                'unlock_count': capsule.unlock_count,
                'created_at': capsule.created_at.strftime('%Y-%m-%d %H:%M'),
                'unlock_time': capsule.unlock_time.strftime('%Y-%m-%d %H:%M') if capsule.unlock_time else None,
                'has_images': len(capsule.images) > 0,
                'has_audio': bool(capsule.audio)
            })
        
        return JsonResponse({
            'success': True,
            'capsules': capsule_list,
            'total_count': len(capsule_list),
            'websocket_available': hasattr(settings, 'CHANNEL_LAYERS')
        })
        
    except Exception as e:
        logger.error(f"获取用户胶囊列表失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '获取胶囊列表失败'
        }, status=500)


@login_required
@csrf_exempt
@handle_api_errors
def get_nearby_capsules(request):
    """获取附近的时光胶囊"""
    try:
        lat = float(request.GET.get('lat', 0))
        lng = float(request.GET.get('lng', 0))
        radius = float(request.GET.get('radius', 5000))  # 默认5公里
        
        # 获取附近的胶囊
        capsules = TimeCapsule.objects.filter(
            visibility__in=['public', 'anonymous'],
            unlock_condition='location'
        ).exclude(user=request.user)
        
        nearby_capsules = []
        for capsule in capsules:
            # 从location字段获取坐标信息
            capsule_lat = 0
            capsule_lng = 0
            
            if capsule.location and isinstance(capsule.location, dict):
                capsule_lat = capsule.location.get('lat', 0)
                capsule_lng = capsule.location.get('lng', 0)
            
            # 计算距离
            distance = calculate_distance(lat, lng, capsule_lat, capsule_lng)
            if distance <= radius:
                nearby_capsules.append({
                    'id': capsule.id,
                    'title': capsule.title,
                    'content': capsule.content[:100] + '...' if len(capsule.content) > 100 else capsule.content,
                    'distance': round(distance, 2),
                    'created_at': capsule.created_at.strftime('%Y-%m-%d %H:%M'),
                    'capsule_type': capsule.capsule_type,
                    'is_anonymous': capsule.is_anonymous,
                    'lat': capsule_lat,
                    'lng': capsule_lng,
                    'can_unlock': distance <= 200  # 200米内可解锁
                })
        
        # 按距离排序
        nearby_capsules.sort(key=lambda x: x['distance'])
        
        return JsonResponse({
            'success': True,
            'capsules': nearby_capsules,
            'total': len(nearby_capsules),
            'websocket_available': hasattr(settings, 'CHANNEL_LAYERS')
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': f'参数错误: {str(e)}'
        }, status=400)
    except Exception as e:
        logger.error(f"获取附近胶囊失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '获取附近胶囊失败'
        }, status=500)


def calculate_distance(lat1, lng1, lat2, lng2):
    """计算两点间距离（米）"""
    import math
    
    # 地球半径（米）
    R = 6371000
    
    # 转换为弧度
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # 计算差值
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    # Haversine公式
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


@login_required
@csrf_exempt
@handle_api_errors
def unlock_capsule(request, capsule_id):
    """解锁胶囊"""
    try:
        capsule = TimeCapsule.objects.get(id=capsule_id)
        
        # 检查是否已经解锁过
        if CapsuleUnlock.objects.filter(capsule=capsule, user=request.user).exists():
            return JsonResponse({
                'success': False,
                'message': '您已经解锁过这个胶囊了'
            })
        
        # 检查解锁条件
        if not capsule.can_be_unlocked_by(request.user):
            return JsonResponse({
                'success': False,
                'message': '胶囊还未到解锁时间或条件不满足'
            })
        
        # 获取解锁位置
        unlock_location = None
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                unlock_location = data.get('location')
            except:
                pass
        
        # 创建解锁记录
        unlock_record = CapsuleUnlock.objects.create(
            capsule=capsule,
            user=request.user,
            location=unlock_location
        )
        
        # 更新胶囊状态
        capsule.unlock_count += 1
        capsule.save()
        
        # 创建记忆碎片
        fragment = MemoryFragment.objects.create(
            user=request.user,
            capsule=capsule,
            fragment_type='text',
            content=capsule.content[:100],
            metadata={
                'emotions': capsule.emotions,
                'weather': capsule.weather,
                'location': capsule.location,
                'unlocked_at': timezone.now().isoformat()
            }
        )
        
        # 清除相关缓存
        cache.delete(f"time_capsule_get_user_capsules_{request.user.id}")
        cache.delete(f"time_capsule_get_user_achievements_{request.user.id}")
        
        # 检查成就
        check_achievements(request.user)
        
        return JsonResponse({
            'success': True,
            'message': '胶囊解锁成功！获得记忆碎片',
            'fragment_id': fragment.id,
            'fragment_content': fragment.content,
            'websocket_available': hasattr(settings, 'CHANNEL_LAYERS')
        })
        
    except TimeCapsule.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '胶囊不存在'
        }, status=404)
    except Exception as e:
        logger.error(f"解锁胶囊失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'解锁失败: {str(e)}'
        }, status=400)


@login_required
@cache_response(timeout=300)  # 缓存5分钟
def get_user_achievements(request):
    """获取用户成就"""
    try:
        achievements = Achievement.objects.filter(user=request.user)
        
        # 获取用户统计数据
        today = timezone.now().date()
        
        # 时光旅人：连续记录天数
        consecutive_days = 0
        for i in range(30):  # 检查最近30天
            check_date = today - timedelta(days=i)
            if TimeCapsule.objects.filter(user=request.user, created_at__date=check_date).exists():
                consecutive_days += 1
            else:
                break
        
        # 城市探险家：解锁他人胶囊数量
        unlock_count = CapsuleUnlock.objects.filter(user=request.user).count()
        
        # 记忆收藏家：记忆碎片数量
        fragment_count = MemoryFragment.objects.filter(user=request.user).count()
        
        # 预言家：预测事件成真次数（暂时设为0）
        prophecy_count = 0
        
        achievement_list = []
        for achievement in achievements:
            achievement_list.append({
                'type': achievement.achievement_type,
                'name': achievement.get_achievement_type_display(),
                'unlocked_at': achievement.unlocked_at.strftime('%Y-%m-%d'),
                'progress': achievement.progress,
                'unlocked': True
            })
        
        # 添加未解锁的成就
        achievement_types = ['traveler', 'explorer', 'prophet', 'collector']
        unlocked_types = [a['type'] for a in achievement_list]
        
        for achievement_type in achievement_types:
            if achievement_type not in unlocked_types:
                progress = 0
                if achievement_type == 'traveler':
                    progress = consecutive_days
                elif achievement_type == 'explorer':
                    progress = unlock_count
                elif achievement_type == 'prophet':
                    progress = prophecy_count
                elif achievement_type == 'collector':
                    progress = fragment_count
                
                achievement_list.append({
                    'type': achievement_type,
                    'name': dict(Achievement.ACHIEVEMENT_TYPES)[achievement_type],
                    'unlocked_at': None,
                    'progress': progress,
                    'unlocked': False
                })
        
        return JsonResponse({
            'success': True,
            'achievements': achievement_list,
            'stats': {
                'consecutive_days': consecutive_days,
                'unlock_count': unlock_count,
                'fragment_count': fragment_count,
                'prophecy_count': prophecy_count
            },
            'websocket_available': hasattr(settings, 'CHANNEL_LAYERS')
        })
        
    except Exception as e:
        logger.error(f"获取用户成就失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '获取成就信息失败'
        }, status=500)


@login_required
@cache_response(timeout=120)  # 缓存2分钟
def get_memory_fragments(request):
    """获取记忆碎片"""
    try:
        fragments = MemoryFragment.objects.filter(user=request.user).select_related('capsule')
        
        fragment_list = []
        for fragment in fragments:
            fragment_list.append({
                'id': fragment.id,
                'type': fragment.get_fragment_type_display(),
                'content': fragment.content,
                'created_at': fragment.created_at.strftime('%Y-%m-%d'),
                'capsule_title': fragment.capsule.title or '无标题',
                'metadata': fragment.metadata
            })
        
        return JsonResponse({
            'success': True,
            'fragments': fragment_list,
            'total_fragments': len(fragment_list),
            'websocket_available': hasattr(settings, 'CHANNEL_LAYERS')
        })
        
    except Exception as e:
        logger.error(f"获取记忆碎片失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '获取记忆碎片失败'
        }, status=500)


@login_required
@handle_api_errors
def get_parallel_match(request):
    """获取平行宇宙匹配"""
    try:
        today = timezone.now().date()
        
        # 查找今天的匹配
        match = ParallelMatch.objects.filter(
            (Q(user1=request.user) | Q(user2=request.user)) &
            Q(match_date=today) &
            Q(is_active=True)
        ).select_related('user1', 'user2').first()
        
        if match:
            other_user = match.user2 if match.user1 == request.user else match.user1
            return JsonResponse({
                'success': True,
                'match': {
                    'user_id': other_user.id,
                    'username': other_user.username,
                    'keywords': match.keywords,
                    'match_date': match.match_date.strftime('%Y-%m-%d')
                },
                'websocket_available': hasattr(settings, 'CHANNEL_LAYERS')
            })
        
        # 如果没有匹配，尝试创建新的匹配
        try:
            new_match = create_parallel_match(request.user)
            if new_match:
                other_user = new_match.user2 if new_match.user1 == request.user else new_match.user1
                return JsonResponse({
                    'success': True,
                    'match': {
                        'user_id': other_user.id,
                        'username': other_user.username,
                        'keywords': new_match.keywords,
                        'match_date': new_match.match_date.strftime('%Y-%m-%d')
                    },
                    'websocket_available': hasattr(settings, 'CHANNEL_LAYERS')
                })
        except Exception as e:
            logger.warning(f"创建平行匹配失败: {str(e)}")
        
        return JsonResponse({
            'success': False,
            'message': '暂无匹配',
            'websocket_available': hasattr(settings, 'CHANNEL_LAYERS')
        })
        
    except Exception as e:
        logger.error(f"获取平行匹配失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '获取匹配信息失败'
        }, status=500)


@login_required
def get_time_capsule_stats(request):
    """获取时光胶囊统计信息"""
    try:
        # 用户统计
        user_stats = {
            'total_capsules': TimeCapsule.objects.filter(user=request.user).count(),
            'public_capsules': TimeCapsule.objects.filter(user=request.user, visibility='public').count(),
            'unlocked_by_others': CapsuleUnlock.objects.filter(capsule__user=request.user).count(),
            'total_fragments': MemoryFragment.objects.filter(user=request.user).count(),
            'achievements_count': Achievement.objects.filter(user=request.user).count(),
        }
        
        # 全局统计
        global_stats = cache.get('time_capsule_global_stats')
        if not global_stats:
            global_stats = {
                'total_capsules': TimeCapsule.objects.count(),
                'total_unlocks': CapsuleUnlock.objects.count(),
                'total_fragments': MemoryFragment.objects.count(),
                'active_users_today': User.objects.filter(
                    time_capsules__created_at__date=timezone.now().date()
                ).distinct().count(),
            }
            cache.set('time_capsule_global_stats', global_stats, 3600)  # 缓存1小时
        
        return JsonResponse({
            'success': True,
            'user_stats': user_stats,
            'global_stats': global_stats,
            'websocket_available': hasattr(settings, 'CHANNEL_LAYERS')
        })
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '获取统计信息失败'
        }, status=500)


def get_emotion_icon(emotions):
    """根据情绪返回对应的图标"""
    emotion_icons = {
        'excited': '💡',
        'happy': '😊',
        'calm': '😌',
        'sad': '😢',
        'angry': '😠',
        'surprised': '😲',
        'anxious': '😰',
        'grateful': '🙏',
        'inspired': '✨'
    }
    
    if emotions and len(emotions) > 0:
        return emotion_icons.get(emotions[0], '📝')
    return '📝'


def check_achievements(user):
    """检查并更新用户成就"""
    try:
        # 时光旅人：连续记录7天
        check_traveler_achievement(user)
        
        # 城市探险家：解锁5个他人胶囊
        check_explorer_achievement(user)
        
        # 记忆收藏家：收集10个记忆碎片
        check_collector_achievement(user)
        
        # 清除成就缓存
        cache.delete(f"time_capsule_get_user_achievements_{user.id}")
        
    except Exception as e:
        logger.error(f"检查成就失败: {str(e)}")


def check_traveler_achievement(user):
    """检查时光旅人成就"""
    try:
        # 检查连续记录天数
        today = timezone.now().date()
        consecutive_days = 0
        
        # 从今天开始往前检查，直到找到没有记录的天
        for i in range(30):  # 最多检查30天
            check_date = today - timedelta(days=i)
            if TimeCapsule.objects.filter(user=user, created_at__date=check_date).exists():
                consecutive_days += 1
            else:
                break
        
        # 如果连续记录天数达到7天或以上，解锁成就
        if consecutive_days >= 7:
            achievement, created = Achievement.objects.get_or_create(
                user=user,
                achievement_type='traveler',
                defaults={'progress': consecutive_days}
            )
            if not created:
                achievement.progress = consecutive_days
                achievement.save()
                
    except Exception as e:
        logger.error(f"检查时光旅人成就失败: {str(e)}")


def check_explorer_achievement(user):
    """检查城市探险家成就"""
    try:
        unlock_count = CapsuleUnlock.objects.filter(user=user).count()
        
        if unlock_count >= 5:
            achievement, created = Achievement.objects.get_or_create(
                user=user,
                achievement_type='explorer',
                defaults={'progress': unlock_count}
            )
            if not created:
                achievement.progress = unlock_count
                achievement.save()
                
    except Exception as e:
        logger.error(f"检查城市探险家成就失败: {str(e)}")


def check_collector_achievement(user):
    """检查记忆收藏家成就"""
    try:
        fragment_count = MemoryFragment.objects.filter(user=user).count()
        
        if fragment_count >= 10:
            achievement, created = Achievement.objects.get_or_create(
                user=user,
                achievement_type='collector',
                defaults={'progress': fragment_count}
            )
            if not created:
                achievement.progress = fragment_count
                achievement.save()
                
    except Exception as e:
        logger.error(f"检查记忆收藏家成就失败: {str(e)}")


def create_parallel_match(user):
    """创建平行宇宙匹配"""
    try:
        # 获取用户最近的关键词
        recent_capsules = TimeCapsule.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=7)
        )
        
        if not recent_capsules.exists():
            return None
        
        # 提取关键词
        all_keywords = []
        for capsule in recent_capsules:
            all_keywords.extend(capsule.keywords)
        
        if not all_keywords:
            return None
        
        # 查找有相似关键词的其他用户
        similar_users = User.objects.filter(
            time_capsules__keywords__overlap=all_keywords,
            time_capsules__created_at__gte=timezone.now() - timedelta(days=7)
        ).exclude(id=user.id).distinct()
        
        if not similar_users.exists():
            return None
        
        # 随机选择一个用户进行匹配
        matched_user = random.choice(similar_users)
        
        # 创建匹配记录
        match = ParallelMatch.objects.create(
            user1=user,
            user2=matched_user,
            keywords=all_keywords[:5]  # 取前5个关键词
        )
        
        return match
        
    except Exception as e:
        logger.error(f"创建平行匹配失败: {str(e)}")
        return None


# 从guitar_training_views.py移动过来的API
@login_required
@csrf_exempt
def save_time_capsule_api(request):
    """保存时光胶囊API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            emotions = data.get('emotions', [])
            unlock_time = data.get('unlock_time')
            unlock_condition = data.get('unlock_condition', 'time')
            visibility = data.get('visibility', 'private')
            
            # 处理媒体文件
            images = data.get('images', [])
            audio = data.get('audio', '')
            location = data.get('location', {})
            weather = data.get('weather', {})
            
            if not content:
                return JsonResponse({'success': False, 'message': '请先写下内容'})
            
            if not emotions:
                return JsonResponse({'success': False, 'message': '请选择至少一种情绪'})
            
            # 创建时光胶囊
            from django.core.exceptions import ValidationError
            
            try:
                # 先创建模型实例进行验证
                capsule = TimeCapsule(
                    user=request.user,
                    content=content,
                    emotions=emotions,
                    unlock_condition=unlock_condition,
                    visibility=visibility,
                    unlock_time=unlock_time if unlock_time else None,
                    keywords=[],  # 明确设置默认值
                    images=images,  # 设置图片列表
                    audio=audio,    # 设置音频URL
                    location=location,  # 设置位置信息
                    weather=weather     # 设置天气信息
                )
                
                # 验证模型
                capsule.full_clean()
                
                # 保存到数据库
                capsule.save()
                
            except ValidationError as e:
                # 处理验证错误
                error_messages = []
                for field, errors in e.message_dict.items():
                    for error in errors:
                        if '请输入合法的URL' in error:
                            error_messages.append('音频URL格式不正确')
                        elif '此字段不能为空' in error:
                            error_messages.append(f'{field}字段不能为空')
                        else:
                            error_messages.append(error)
                
                return JsonResponse({
                    'success': False, 
                    'message': '; '.join(error_messages)
                })
            
            # 检查并授予成就
            check_achievements(request.user)
            
            return JsonResponse({
                'success': True,
                'message': '时光胶囊保存成功！',
                'capsule_id': capsule.id
            })
            
        except Exception as e:
            error_message = str(e)
            
            # 处理URL验证错误
            if '请输入合法的URL' in error_message or 'pattern' in error_message.lower():
                return JsonResponse({
                    'success': False, 
                    'message': '音频URL格式不正确，请检查URL格式'
                })
            
            # 处理其他验证错误
            if '此字段不能为空' in error_message:
                return JsonResponse({
                    'success': False, 
                    'message': '请填写所有必需字段'
                })
            
            return JsonResponse({'success': False, 'message': f'保存失败: {error_message}'})
    
    return JsonResponse({'success': False, 'message': '无效请求'})


@login_required
def get_time_capsules_api(request):
    """获取用户的时光胶囊列表API"""
    try:
        # 获取用户的所有胶囊
        capsules = TimeCapsule.objects.filter(user=request.user).order_by('-created_at')
        
        capsule_list = []
        for capsule in capsules:
            capsule_data = {
                'id': capsule.id,
                'content': capsule.content,
                'emotions': capsule.emotions,
                'created_at': capsule.created_at.strftime('%Y-%m-%d %H:%M'),
                'unlock_time': capsule.unlock_time.strftime('%Y-%m-%d %H:%M') if capsule.unlock_time else None,
                'unlock_condition': capsule.unlock_condition,
                'visibility': capsule.visibility,
                'is_unlocked': capsule.is_unlocked,
                'images': capsule.images,
                'audio': capsule.audio,
                'location': capsule.location,
                'weather': capsule.weather
            }
            capsule_list.append(capsule_data)
        
        return JsonResponse({
            'success': True,
            'capsules': capsule_list
        })
        
    except Exception as e:
        logger.error(f"获取时光胶囊列表失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'获取失败: {str(e)}'
        }, status=500)


@login_required
def get_time_capsule_detail_api(request, capsule_id):
    """获取时光胶囊详情API"""
    try:
        capsule = TimeCapsule.objects.get(id=capsule_id, user=request.user)
        
        capsule_data = {
            'id': capsule.id,
            'content': capsule.content,
            'emotions': capsule.emotions,
            'created_at': capsule.created_at.strftime('%Y-%m-%d %H:%M'),
            'unlock_time': capsule.unlock_time.strftime('%Y-%m-%d %H:%M') if capsule.unlock_time else None,
            'unlock_condition': capsule.unlock_condition,
            'visibility': capsule.visibility,
            'is_unlocked': capsule.is_unlocked,
            'images': capsule.images,
            'audio': capsule.audio,
            'location': capsule.location,
            'weather': capsule.weather,
            'keywords': capsule.keywords
        }
        
        return JsonResponse({
            'success': True,
            'capsule': capsule_data
        })
        
    except TimeCapsule.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '胶囊不存在'
        }, status=404)
    except Exception as e:
        logger.error(f"获取时光胶囊详情失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'获取失败: {str(e)}'
        }, status=500)


@login_required
def unlock_time_capsule_api(request, capsule_id):
    """解锁时光胶囊API"""
    try:
        capsule = TimeCapsule.objects.get(id=capsule_id, user=request.user)
        
        # 检查是否可以解锁
        if capsule.is_unlocked:
            return JsonResponse({
                'success': False,
                'message': '胶囊已经解锁'
            })
        
        # 检查解锁条件
        can_unlock = False
        unlock_reason = ""
        
        if capsule.unlock_condition == 'time':
            if capsule.unlock_time and timezone.now() >= capsule.unlock_time:
                can_unlock = True
                unlock_reason = "时间条件满足"
            else:
                unlock_reason = "时间条件未满足"
        
        elif capsule.unlock_condition == 'location':
            # 这里可以添加位置解锁逻辑
            can_unlock = True
            unlock_reason = "位置条件满足"
        
        elif capsule.unlock_condition == 'event':
            # 这里可以添加事件解锁逻辑
            can_unlock = True
            unlock_reason = "事件条件满足"
        
        if can_unlock:
            # 解锁胶囊
            capsule.is_unlocked = True
            capsule.save()
            
            # 创建解锁记录
            CapsuleUnlock.objects.create(
                user=request.user,
                capsule=capsule,
                unlock_time=timezone.now()
            )
            
            # 检查成就
            check_achievements(request.user)
            
            return JsonResponse({
                'success': True,
                'message': f'胶囊解锁成功！{unlock_reason}',
                'capsule': {
                    'id': capsule.id,
                    'content': capsule.content,
                    'emotions': capsule.emotions,
                    'images': capsule.images,
                    'audio': capsule.audio,
                    'location': capsule.location,
                    'weather': capsule.weather
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': unlock_reason
            })
        
    except TimeCapsule.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '胶囊不存在'
        }, status=404)
    except Exception as e:
        logger.error(f"解锁时光胶囊失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'解锁失败: {str(e)}'
        }, status=500)


@login_required
def get_achievements_api(request):
    """获取用户成就API"""
    try:
        import logging
        from django.conf import settings
        logger = logging.getLogger(__name__)
        
        # 获取用户的所有成就
        achievements = Achievement.objects.filter(user=request.user)
        achievement_list = []
        
        for achievement in achievements:
            achievement_data = {
                'type': achievement.achievement_type,
                'name': achievement.get_achievement_type_display(),
                'description': achievement.get_description(),
                'unlocked_at': achievement.unlocked_at.strftime('%Y-%m-%d') if achievement.unlocked_at else None,
                'progress': achievement.progress,
                'unlocked': True
            }
            achievement_list.append(achievement_data)
        
        # 计算统计数据
        stats = {
            'consecutive_days': 0,
            'unlock_count': 0,
            'fragment_count': 0,
            'prophecy_count': 0,
            'total_points': 0
        }
        
        try:
            # 计算连续记录天数
            capsules = TimeCapsule.objects.filter(user=request.user).order_by('-created_at')
            if capsules.exists():
                current_date = timezone.now().date()
                consecutive_days = 0
                check_date = current_date
                
                while True:
                    if capsules.filter(created_at__date=check_date).exists():
                        consecutive_days += 1
                        check_date -= timedelta(days=1)
                    else:
                        break
                
                stats['consecutive_days'] = consecutive_days
            
            # 计算解锁次数
            stats['unlock_count'] = CapsuleUnlock.objects.filter(user=request.user).count()
            
            # 计算记忆碎片数量
            stats['fragment_count'] = MemoryFragment.objects.filter(user=request.user).count()
            
            # 计算预言数量（这里可以根据实际需求调整）
            stats['prophecy_count'] = TimeCapsule.objects.filter(
                user=request.user, 
                unlock_condition='time'
            ).count()
            
            # 计算总积分
            stats['total_points'] = sum(achievement.progress for achievement in achievements)
            
        except Exception as e:
            logger.error(f"计算统计数据失败: {str(e)}")
            # 使用默认值
        
        return JsonResponse({
            'success': True,
            'achievements': achievement_list,
            'stats': stats,
            'websocket_available': hasattr(settings, 'CHANNEL_LAYERS')
        })
        
    except Exception as e:
        logger.error(f"获取用户成就失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'获取失败: {str(e)}',
            'achievements': [],
            'stats': {
                'consecutive_days': 0, 'unlock_count': 0, 'fragment_count': 0,
                'prophecy_count': 0, 'total_points': 0
            }
        }, status=500)


def time_capsule_diary_view(request):
    """时光胶囊日记主页面"""
    # 添加WebSocket连接状态检查
    websocket_available = hasattr(settings, 'CHANNEL_LAYERS')
    
    context = {
        'websocket_available': websocket_available,
        'api_timeout': 10000,  # 10秒超时
        'retry_attempts': 3,
    }
    
    return render(request, 'tools/time_capsule_diary.html', context)


def time_capsule_history_view(request):
    """时光胶囊历史页面"""
    context = {
        'websocket_available': hasattr(settings, 'CHANNEL_LAYERS'),
    }
    
    return render(request, 'tools/time_capsule_history.html', context)
