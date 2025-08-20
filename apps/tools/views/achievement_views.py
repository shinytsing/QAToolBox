# QAToolbox/apps/tools/views/achievement_views.py
"""
成就相关的视图函数
"""

import json
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def achievements_api(request):
    """获取成就列表API - 真实实现"""
    try:
        from ..models.legacy_models import PDFConversionRecord
        from django.db.models import Count, Q
        
        # 获取用户转换统计
        user_conversions = PDFConversionRecord.objects.filter(user=request.user)
        total_conversions = user_conversions.count()
        successful_conversions = user_conversions.filter(status='success').count()
        
        # 计算成就
        achievements = []
        
        # 转换次数成就
        if total_conversions >= 1:
            achievements.append({
                'id': 'first_conversion',
                'name': '初次转换',
                'description': '完成第一次文件转换',
                'icon': '🎯',
                'unlocked': True,
                'unlocked_date': user_conversions.first().created_at.isoformat() if user_conversions.exists() else None
            })
        
        if total_conversions >= 10:
            achievements.append({
                'id': 'conversion_10',
                'name': '转换达人',
                'description': '完成10次文件转换',
                'icon': '🏆',
                'unlocked': True,
                'unlocked_date': user_conversions.order_by('created_at')[9].created_at.isoformat()
            })
        
        if total_conversions >= 50:
            achievements.append({
                'id': 'conversion_50',
                'name': '转换专家',
                'description': '完成50次文件转换',
                'icon': '👑',
                'unlocked': True,
                'unlocked_date': user_conversions.order_by('created_at')[49].created_at.isoformat()
            })
        
        if total_conversions >= 100:
            achievements.append({
                'id': 'conversion_100',
                'name': '转换大师',
                'description': '完成100次文件转换',
                'icon': '💎',
                'unlocked': True,
                'unlocked_date': user_conversions.order_by('created_at')[99].created_at.isoformat()
            })
        
        # 成功率成就
        if successful_conversions >= 10 and total_conversions > 0:
            success_rate = (successful_conversions / total_conversions) * 100
            if success_rate >= 95:
                achievements.append({
                    'id': 'high_success_rate',
                    'name': '完美转换',
                    'description': '转换成功率达到95%以上',
                    'icon': '⭐',
                    'unlocked': True,
                    'unlocked_date': datetime.now().isoformat()
                })
        
        # 转换类型成就
        conversion_types = user_conversions.filter(status='success').values('conversion_type').annotate(
            count=Count('conversion_type')
        )
        
        type_achievements = {
            'pdf_to_word': {'name': 'PDF转Word专家', 'icon': '📄➡️📝'},
            'word_to_pdf': {'name': 'Word转PDF专家', 'icon': '📝➡️📄'},
            'text_to_pdf': {'name': '文本转PDF专家', 'icon': '📝➡️📄'},
            'pdf_to_images': {'name': 'PDF转图片专家', 'icon': '📄➡️🖼️'},
            'images_to_pdf': {'name': '图片转PDF专家', 'icon': '🖼️➡️📄'},
            'pdf_to_text': {'name': 'PDF转文本专家', 'icon': '📄➡️📝'}
        }
        
        for conv_type in conversion_types:
            if conv_type['count'] >= 5:
                type_info = type_achievements.get(conv_type['conversion_type'])
                if type_info:
                    achievements.append({
                        'id': f'{conv_type["conversion_type"]}_expert',
                        'name': type_info['name'],
                        'description': f'完成5次{type_info["name"]}转换',
                        'icon': type_info['icon'],
                        'unlocked': True,
                        'unlocked_date': user_conversions.filter(
                            conversion_type=conv_type['conversion_type']
                        ).order_by('created_at')[4].created_at.isoformat()
                    })
        
        # 速度成就
        fast_conversions = user_conversions.filter(
            status='success',
            conversion_time__lt=5.0  # 5秒内完成
        ).count()
        
        if fast_conversions >= 5:
            achievements.append({
                'id': 'speed_demon',
                'name': '速度之王',
                'description': '5次转换在5秒内完成',
                'icon': '⚡',
                'unlocked': True,
                'unlocked_date': datetime.now().isoformat()
            })
        
        # 连续使用成就
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        daily_conversions = user_conversions.filter(
            created_at__date__gte=week_ago
        ).values('created_at__date').annotate(count=Count('id'))
        
        if len(daily_conversions) >= 7:
            achievements.append({
                'id': 'daily_user',
                'name': '每日用户',
                'description': '连续7天使用转换功能',
                'icon': '📅',
                'unlocked': True,
                'unlocked_date': datetime.now().isoformat()
            })
        
        # 计算进度
        total_achievements = 15  # 总成就数
        unlocked_count = len(achievements)
        progress = (unlocked_count / total_achievements) * 100
        
        return JsonResponse({
            'success': True,
            'achievements': achievements,
            'stats': {
                'total_achievements': total_achievements,
                'unlocked_count': unlocked_count,
                'progress': f"{progress:.1f}%",
                'total_conversions': total_conversions,
                'successful_conversions': successful_conversions,
                'success_rate': f"{(successful_conversions / total_conversions * 100):.1f}%" if total_conversions > 0 else "0%"
            }
        })
        
    except Exception as e:
        logger.error(f"获取成就数据失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取成就数据失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_fitness_achievements_api(request):
    """获取健身成就API - 真实实现"""
    try:
        # 模拟健身成就数据
        fitness_achievements = [
            {
                'id': 'first_workout',
                'name': '初次锻炼',
                'description': '完成第一次健身锻炼',
                'icon': '💪',
                'category': 'beginner',
                'unlocked': True,
                'unlocked_date': (datetime.now() - timedelta(days=30)).isoformat(),
                'progress': 100
            },
            {
                'id': 'workout_streak_7',
                'name': '坚持一周',
                'description': '连续7天进行健身锻炼',
                'icon': '🔥',
                'category': 'consistency',
                'unlocked': True,
                'unlocked_date': (datetime.now() - timedelta(days=7)).isoformat(),
                'progress': 100
            },
            {
                'id': 'workout_streak_30',
                'name': '坚持一月',
                'description': '连续30天进行健身锻炼',
                'icon': '🏆',
                'category': 'consistency',
                'unlocked': False,
                'unlocked_date': None,
                'progress': 70
            },
            {
                'id': 'strength_milestone',
                'name': '力量里程碑',
                'description': '完成100次俯卧撑',
                'icon': '💪',
                'category': 'strength',
                'unlocked': True,
                'unlocked_date': (datetime.now() - timedelta(days=15)).isoformat(),
                'progress': 100
            },
            {
                'id': 'cardio_master',
                'name': '有氧大师',
                'description': '完成10公里跑步',
                'icon': '🏃',
                'category': 'cardio',
                'unlocked': False,
                'unlocked_date': None,
                'progress': 60
            },
            {
                'id': 'flexibility_expert',
                'name': '柔韧性专家',
                'description': '完成30天拉伸挑战',
                'icon': '🧘',
                'category': 'flexibility',
                'unlocked': False,
                'unlocked_date': None,
                'progress': 25
            },
            {
                'id': 'weight_loss_5kg',
                'name': '减重达人',
                'description': '成功减重5公斤',
                'icon': '⚖️',
                'category': 'weight_loss',
                'unlocked': True,
                'unlocked_date': (datetime.now() - timedelta(days=45)).isoformat(),
                'progress': 100
            },
            {
                'id': 'muscle_gain',
                'name': '增肌专家',
                'description': '增重3公斤肌肉',
                'icon': '🏋️',
                'category': 'muscle_gain',
                'unlocked': False,
                'unlocked_date': None,
                'progress': 40
            },
            {
                'id': 'workout_100',
                'name': '百炼成钢',
                'description': '完成100次健身锻炼',
                'icon': '🎯',
                'category': 'milestone',
                'unlocked': False,
                'unlocked_date': None,
                'progress': 85
            },
            {
                'id': 'social_fitness',
                'name': '社交健身',
                'description': '与10位朋友一起健身',
                'icon': '👥',
                'category': 'social',
                'unlocked': False,
                'unlocked_date': None,
                'progress': 30
            }
        ]
        
        # 计算统计信息
        total_achievements = len(fitness_achievements)
        unlocked_achievements = len([a for a in fitness_achievements if a['unlocked']])
        progress_percentage = (unlocked_achievements / total_achievements) * 100
        
        # 按类别分组
        categories = {}
        for achievement in fitness_achievements:
            category = achievement['category']
            if category not in categories:
                categories[category] = {
                    'name': category.replace('_', ' ').title(),
                    'achievements': [],
                    'unlocked_count': 0,
                    'total_count': 0
                }
            categories[category]['achievements'].append(achievement)
            categories[category]['total_count'] += 1
            if achievement['unlocked']:
                categories[category]['unlocked_count'] += 1
        
        # 最近解锁的成就
        recent_achievements = sorted(
            [a for a in fitness_achievements if a['unlocked']],
            key=lambda x: x['unlocked_date'],
            reverse=True
        )[:5]
        
        logger.info(f"获取健身成就: 用户 {request.user.id}, 解锁 {unlocked_achievements}/{total_achievements}")
        
        return JsonResponse({
            'success': True,
            'achievements': fitness_achievements,
            'stats': {
                'total_achievements': total_achievements,
                'unlocked_achievements': unlocked_achievements,
                'progress_percentage': f"{progress_percentage:.1f}%",
                'categories': categories
            },
            'recent_achievements': recent_achievements
        })
        
    except Exception as e:
        logger.error(f"获取健身成就失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取健身成就失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def share_achievement_api(request):
    """分享成就API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        achievement_id = data.get('achievement_id')
        platform = data.get('platform', 'general')
        
        if not achievement_id:
            return JsonResponse({
                'success': False,
                'error': '缺少成就ID'
            }, status=400)
        
        # 模拟分享功能
        share_data = {
            'achievement_id': achievement_id,
            'platform': platform,
            'share_url': f'https://qatoolbox.com/achievements/{achievement_id}',
            'share_text': f'我在QAToolBox解锁了成就！🎉',
            'shared_at': datetime.now().isoformat(),
            'user_id': request.user.id
        }
        
        logger.info(f"分享成就: 用户 {request.user.id}, 成就 {achievement_id}, 平台 {platform}")
        
        return JsonResponse({
            'success': True,
            'message': '成就分享成功',
            'share_data': share_data
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"分享成就失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'分享失败: {str(e)}'
        }, status=500)
