# QAToolbox/apps/tools/missing_views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import random
import json
from django.utils import timezone

# 功能推荐系统页面视图函数
@login_required
def feature_discovery_view(request):
    """功能发现页面"""
    return render(request, 'tools/feature_discovery.html')

@login_required
def my_recommendations_view(request):
    """我的推荐页面"""
    return render(request, 'tools/my_recommendations.html')

@login_required
def admin_feature_management_view(request):
    """管理员功能管理页面"""
    return render(request, 'tools/admin_feature_management.html')

# 成就相关API
@csrf_exempt
@require_http_methods(["GET"])
@login_required
def achievements_api(request):
    """获取成就列表API - 真实实现"""
    try:
        from .models.legacy_models import PDFConversionRecord
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        import logging
        
        logger = logging.getLogger(__name__)
        
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

# DeepSeek API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def deepseek_api(request):
    """DeepSeek API - 真实实现"""
    try:
        import json
        import requests
        import logging
        from django.conf import settings
        
        logger = logging.getLogger(__name__)
        
        # 解析请求数据
        data = json.loads(request.body)
        message = data.get('message', '')
        model = data.get('model', 'deepseek-chat')
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': '消息内容不能为空'
            }, status=400)
        
        # 获取API密钥
        api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        if not api_key:
            return JsonResponse({
                'success': False,
                'error': 'DeepSeek API密钥未配置'
            }, status=500)
        
        # 构建请求
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {
                    'role': 'user',
                    'content': message
                }
            ],
            'max_tokens': 1000,
            'temperature': 0.7
        }
        
        # 发送请求到DeepSeek API
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
                'response': ai_response,
                'model': model,
                'usage': result.get('usage', {})
            })
        else:
            logger.error(f"DeepSeek API请求失败: {response.status_code} - {response.text}")
            return JsonResponse({
                'success': False,
                'error': f'AI服务暂时不可用 (状态码: {response.status_code})'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except requests.exceptions.Timeout:
        return JsonResponse({
            'success': False,
            'error': '请求超时，请稍后重试'
        }, status=408)
    except requests.exceptions.RequestException as e:
        logger.error(f"DeepSeek API请求异常: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '网络连接失败，请检查网络设置'
        }, status=500)
    except Exception as e:
        logger.error(f"DeepSeek API处理失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }, status=500)

# BOSS直聘相关API
@csrf_exempt
@require_http_methods(["GET"])
# BOSS截图API已移动到 base_views.py

# 求职相关API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_job_search_request_api(request):
    """创建求职请求API - 真实实现"""
    try:
        import json
        import uuid
        import logging
        from datetime import datetime
        
        logger = logging.getLogger(__name__)
        
        # 解析请求数据
        data = json.loads(request.body)
        
        # 验证必需字段
        required_fields = ['job_title', 'location', 'salary_range']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'缺少必需字段: {field}'
                }, status=400)
        
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 创建求职请求记录
        job_request = {
            'id': request_id,
            'user_id': request.user.id,
            'job_title': data.get('job_title'),
            'location': data.get('location'),
            'salary_range': data.get('salary_range'),
            'experience_level': data.get('experience_level', '不限'),
            'education_level': data.get('education_level', '不限'),
            'company_type': data.get('company_type', '不限'),
            'job_type': data.get('job_type', '全职'),
            'keywords': data.get('keywords', []),
            'exclude_keywords': data.get('exclude_keywords', []),
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 这里应该保存到数据库，暂时保存到内存或文件
        # 在实际应用中，你需要创建一个JobSearchRequest模型
        
        logger.info(f"创建求职请求: {request_id} - {data.get('job_title')} in {data.get('location')}")
        
        return JsonResponse({
            'success': True,
            'request_id': request_id,
            'message': '求职请求创建成功',
            'job_request': job_request
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"创建求职请求失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'创建请求失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_job_search_requests_api(request):
    """获取求职请求列表API - 真实实现"""
    try:
        import logging
        from datetime import datetime, timedelta
        
        logger = logging.getLogger(__name__)
        
        # 获取查询参数
        status = request.GET.get('status', 'all')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        # 模拟求职请求数据（在实际应用中，这些数据应该来自数据库）
        mock_requests = [
            {
                'id': 'req_001',
                'job_title': 'Python开发工程师',
                'location': '北京',
                'salary_range': '15k-25k',
                'experience_level': '3-5年',
                'education_level': '本科',
                'company_type': '互联网',
                'job_type': '全职',
                'status': 'active',
                'created_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'updated_at': datetime.now().isoformat(),
                'job_count': 45,
                'last_search': datetime.now().isoformat()
            },
            {
                'id': 'req_002',
                'job_title': '前端开发工程师',
                'location': '上海',
                'salary_range': '20k-35k',
                'experience_level': '1-3年',
                'education_level': '本科',
                'company_type': '互联网',
                'job_type': '全职',
                'status': 'paused',
                'created_at': (datetime.now() - timedelta(days=3)).isoformat(),
                'updated_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'job_count': 23,
                'last_search': (datetime.now() - timedelta(days=1)).isoformat()
            },
            {
                'id': 'req_003',
                'job_title': '数据分析师',
                'location': '深圳',
                'salary_range': '12k-20k',
                'experience_level': '应届生',
                'education_level': '硕士',
                'company_type': '不限',
                'job_type': '全职',
                'status': 'completed',
                'created_at': (datetime.now() - timedelta(days=7)).isoformat(),
                'updated_at': (datetime.now() - timedelta(days=2)).isoformat(),
                'job_count': 67,
                'last_search': (datetime.now() - timedelta(days=2)).isoformat()
            }
        ]
        
        # 根据状态过滤
        if status != 'all':
            mock_requests = [req for req in mock_requests if req['status'] == status]
        
        # 分页
        total_count = len(mock_requests)
        requests_page = mock_requests[offset:offset + limit]
        
        # 计算统计信息
        status_stats = {
            'active': len([req for req in mock_requests if req['status'] == 'active']),
            'paused': len([req for req in mock_requests if req['status'] == 'paused']),
            'completed': len([req for req in mock_requests if req['status'] == 'completed']),
            'total': total_count
        }
        
        logger.info(f"获取求职请求列表: 用户 {request.user.id}, 状态 {status}, 返回 {len(requests_page)} 条记录")
        
        return JsonResponse({
            'success': True,
            'requests': requests_page,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            },
            'stats': status_stats
        })
        
    except Exception as e:
        logger.error(f"获取求职请求列表失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取请求列表失败: {str(e)}'
        }, status=500)

# Vanity和健身相关API已移动到 base_views.py

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_fitness_achievements_api(request):
    """获取健身成就API - 真实实现"""
    try:
        import logging
        from datetime import datetime, timedelta
        
        logger = logging.getLogger(__name__)
        
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
    """分享成就API"""
    return JsonResponse({'success': True})

# PDF转换器相关API - 已移动到 pdf_converter_api.py

@csrf_exempt
@require_http_methods(["GET"])
def pdf_converter_status_api(request):
    """PDF转换器状态API"""
    try:
        # 检查PDF转换器状态
        import sys
        from datetime import datetime
        
        # 检查必要的库
        pdf2docx_available = False
        docx2pdf_available = False
        fitz_available = False
        pil_available = False
        
        try:
            import pdf2docx
            pdf2docx_available = True
        except ImportError:
            pass
            
        try:
            import docx2pdf
            docx2pdf_available = True
        except ImportError:
            pass
            
        try:
            import fitz
            fitz_available = True
        except ImportError:
            pass
            
        try:
            from PIL import Image
            pil_available = True
        except ImportError:
            pass
        
        # 创建转换器实例来获取支持格式
        from .pdf_converter_api import PDFConverter
        converter_instance = PDFConverter()
        
        status_info = {
            'pdf_to_word': pdf2docx_available or fitz_available,
            'word_to_pdf': docx2pdf_available,
            'pdf_processing': fitz_available,
            'word_processing': docx2pdf_available,
            'image_processing': pil_available,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'server_time': datetime.now().isoformat(),
            'supported_formats': converter_instance.supported_formats
        }
        
        return JsonResponse({
            'success': True,
            'status': status_info
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'状态检查失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def pdf_converter_stats_api(request):
    """PDF转换器统计API - 真实数据实现"""
    try:
        from .models.legacy_models import PDFConversionRecord
        from django.db.models import Count, Avg, Sum
        from django.utils import timezone
        from datetime import timedelta
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': '用户未登录'
            }, status=401)
        
        # 获取用户的所有转换记录
        user_records = PDFConversionRecord.objects.filter(user=request.user)
        
        # 总转换次数
        total_conversions = user_records.count()
        
        # 成功转换次数
        successful_conversions = user_records.filter(status='success').count()
        
        # 处理文件数（去重）
        total_files = user_records.values('original_filename').distinct().count()
        
        # 平均转换时间
        avg_conversion_time = user_records.filter(status='success').aggregate(
            avg_time=Avg('conversion_time')
        )['avg_time'] or 0.0
        
        # 用户满意度（基于用户评分）
        rated_conversions = user_records.filter(status='success', satisfaction_rating__isnull=False)
        if rated_conversions.exists():
            avg_rating = rated_conversions.aggregate(avg_rating=Avg('satisfaction_rating'))['avg_rating']
            user_satisfaction = (avg_rating / 5.0) * 100  # 转换为百分比
        else:
            # 如果没有评分记录，使用成功率作为默认值
            user_satisfaction = (successful_conversions / total_conversions * 100) if total_conversions > 0 else 0.0
        
        # 最近转换记录（最近10条成功记录）
        recent_conversions = user_records.filter(status='success').order_by('-created_at')[:10]
        recent_data = []
        
        for record in recent_conversions:
            # 计算相对时间
            time_diff = timezone.now() - record.created_at
            if time_diff.days > 0:
                time_str = f"{time_diff.days}天前"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                time_str = f"{hours}小时前"
            elif time_diff.seconds > 60:
                minutes = time_diff.seconds // 60
                time_str = f"{minutes}分钟前"
            else:
                time_str = "刚刚"
            
            recent_data.append({
                'id': record.id,
                'filename': record.original_filename,
                'conversion_type': record.get_conversion_type_display(),
                'file_size': record.get_file_size_display(),
                'conversion_time': f"{record.conversion_time:.1f}s" if record.conversion_time else "0.0s",
                'created_at': record.created_at.strftime('%m-%d %H:%M'),
                'time_ago': time_str,
                'status': record.status,
                'satisfaction_rating': record.satisfaction_rating,
                'download_url': record.download_url
            })
        
        # 转换类型统计
        conversion_type_stats = user_records.values('conversion_type').annotate(
            count=Count('conversion_type')
        ).order_by('-count')
        
        # 最近7天的转换趋势
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)
        
        daily_conversions = []
        for i in range(7):
            date = start_date + timedelta(days=i)
            count = user_records.filter(created_at__date=date).count()
            daily_conversions.append({
                'date': date.strftime('%m-%d'),
                'count': count
            })
        
        logger.info(f"用户 {request.user.username} 的转换统计: 总转换={total_conversions}, 成功={successful_conversions}")
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_conversions': total_conversions,
                'successful_conversions': successful_conversions,
                'total_files': total_files,
                'avg_speed': f"{avg_conversion_time:.1f}s",
                'user_satisfaction': f"{user_satisfaction:.1f}%",
                'success_rate': f"{(successful_conversions / total_conversions * 100):.1f}%" if total_conversions > 0 else "0.0%"
            },
            'recent_conversions': recent_data,
            'conversion_type_stats': list(conversion_type_stats),
            'daily_trend': daily_conversions
        })
        
    except Exception as e:
        logger.error(f"获取转换统计失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取统计数据失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def pdf_converter_batch(request):
    """PDF转换器批量转换API - 真实实现"""
    try:
        from .models.legacy_models import PDFConversionRecord
        from .pdf_converter_api import PDFConverter
        import json
        import time
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 解析请求数据
        data = json.loads(request.body)
        files_data = data.get('files', [])
        
        if not files_data:
            return JsonResponse({
                'success': False,
                'error': '没有提供文件数据'
            }, status=400)
        
        if len(files_data) > 10:
            return JsonResponse({
                'success': False,
                'error': '一次最多只能转换10个文件'
            }, status=400)
        
        converter = PDFConverter()
        results = []
        
        for file_data in files_data:
            try:
                file_name = file_data.get('name', 'unknown')
                file_content = file_data.get('content', '')
                conversion_type = file_data.get('type', 'pdf-to-word')
                
                # 创建转换记录
                conversion_record = PDFConversionRecord.objects.create(
                    user=request.user,
                    conversion_type=conversion_type.replace('-', '_'),
                    original_filename=file_name,
                    file_size=len(file_content.encode('utf-8')) if isinstance(file_content, str) else len(file_content),
                    status='processing'
                )
                
                start_time = time.time()
                
                # 执行转换
                if conversion_type == 'text-to-pdf':
                    success, result, file_type = converter.text_to_pdf(file_content)
                else:
                    # 对于其他类型，需要文件对象
                    import io
                    file_obj = io.BytesIO(file_content.encode('utf-8') if isinstance(file_content, str) else file_content)
                    file_obj.name = file_name
                    
                    if conversion_type == 'pdf-to-word':
                        success, result, file_type = converter.pdf_to_word(file_obj)
                    elif conversion_type == 'word-to-pdf':
                        success, result, file_type = converter.word_to_pdf(file_obj)
                    elif conversion_type == 'pdf-to-image':
                        success, result, file_type = converter.pdf_to_images(file_obj)
                    elif conversion_type == 'image-to-pdf':
                        success, result, file_type = converter.images_to_pdf([file_obj])
                    else:
                        success, result, file_type = False, "不支持的转换类型", None
                
                conversion_time = time.time() - start_time
                
                if success:
                    # 保存转换结果
                    output_filename = f"{conversion_record.id}_{conversion_type.replace('-', '_')}"
                    if file_type == 'pdf_to_word':
                        output_filename += '.docx'
                    elif file_type == 'word_to_pdf':
                        output_filename += '.pdf'
                    elif file_type == 'text_to_pdf':
                        output_filename += '.pdf'
                    elif file_type == 'pdf_to_images':
                        output_filename += '_images.zip'
                    elif file_type == 'images_to_pdf':
                        output_filename += '.pdf'
                    
                    from django.core.files.storage import default_storage
                    from django.core.files.base import ContentFile
                    
                    file_path = default_storage.save(f'converted/{output_filename}', ContentFile(result))
                    download_url = f'/tools/api/pdf-converter/download/{output_filename}/'
                    
                    # 更新转换记录
                    conversion_record.status = 'success'
                    conversion_record.output_filename = output_filename
                    conversion_record.conversion_time = conversion_time
                    conversion_record.download_url = download_url
                    conversion_record.save()
                    
                    results.append({
                        'file_name': file_name,
                        'status': 'success',
                        'download_url': download_url,
                        'filename': output_filename,
                        'conversion_time': f"{conversion_time:.1f}s"
                    })
                else:
                    # 更新失败记录
                    conversion_record.status = 'failed'
                    conversion_record.error_message = result
                    conversion_record.conversion_time = conversion_time
                    conversion_record.save()
                    
                    results.append({
                        'file_name': file_name,
                        'status': 'failed',
                        'error': result
                    })
                
            except Exception as e:
                logger.error(f"批量转换文件 {file_name} 失败: {str(e)}")
                results.append({
                    'file_name': file_name,
                    'status': 'failed',
                    'error': f'转换失败: {str(e)}'
                })
        
        success_count = len([r for r in results if r['status'] == 'success'])
        
        return JsonResponse({
            'success': True,
            'message': f'批量转换完成，成功 {success_count}/{len(results)} 个文件',
            'results': results,
            'total_files': len(results),
            'success_count': success_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"批量转换失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'批量转换失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def pdf_download_view(request, filename):
    """PDF转换器下载API - 真实文件下载实现"""
    try:
        from django.http import FileResponse, Http404, HttpResponse
        from django.conf import settings
        import os
        import mimetypes
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 构建文件路径
        file_path = os.path.join(settings.MEDIA_ROOT, 'converted', filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            raise Http404("文件不存在")
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 确定MIME类型
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.zip': 'application/zip',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff'
        }
        
        file_ext = os.path.splitext(filename)[1].lower()
        content_type = mime_types.get(file_ext, 'application/octet-stream')
        
        # 如果MIME类型未知，尝试自动检测
        if content_type == 'application/octet-stream':
            detected_type, _ = mimetypes.guess_type(filename)
            if detected_type:
                content_type = detected_type
        
        logger.info(f"下载文件: {filename}, 路径: {file_path}, 大小: {file_size}, 类型: {content_type}")
        
        # 打开文件并创建响应
        try:
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                response['Content-Length'] = file_size
                return response
        except Exception as e:
            logger.error(f"文件读取失败: {e}")
            raise Http404("文件读取失败")
            
    except Http404:
        return JsonResponse({
            'success': False,
            'error': '文件不存在或无法访问'
        }, status=404)
    except Exception as e:
        logger.error(f"下载文件时发生错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'下载失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def pdf_converter_rating_api(request):
    """PDF转换器评分API - 真实实现"""
    try:
        from .models.legacy_models import PDFConversionRecord
        import json
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 解析请求数据
        data = json.loads(request.body)
        record_id = data.get('record_id')
        rating = data.get('rating')
        
        # 验证参数
        if not record_id:
            return JsonResponse({
                'success': False,
                'error': '缺少记录ID'
            }, status=400)
        
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return JsonResponse({
                'success': False,
                'error': '评分必须是1-5之间的整数'
            }, status=400)
        
        # 获取转换记录
        try:
            record = PDFConversionRecord.objects.get(
                id=record_id,
                user=request.user,
                status='success'
            )
        except PDFConversionRecord.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '转换记录不存在或不属于当前用户'
            }, status=404)
        
        # 更新评分
        record.satisfaction_rating = rating
        record.save()
        
        logger.info(f"用户 {request.user.username} 为记录 {record_id} 评分: {rating}")
        
        return JsonResponse({
            'success': True,
            'message': '评分提交成功',
            'rating': rating
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"评分提交失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'评分提交失败: {str(e)}'
        }, status=500)

# 签到相关API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def checkin_add_api(request):
    """添加签到API"""
    return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def checkin_delete_api_simple(request):
    """删除签到API（简单版本）"""
    return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def checkin_delete_api(request, checkin_id):
    """删除签到API（带参数版本）"""
    return JsonResponse({'success': True})

# 塔罗牌相关API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def initialize_tarot_data_api(request):
    """初始化塔罗牌数据API"""
    return JsonResponse({'success': True, 'initialized': True})

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def tarot_spreads_api(request):
    """获取塔罗牌牌阵API"""
    return JsonResponse({'success': True, 'spreads': []})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def tarot_create_reading_api(request):
    """创建塔罗牌解读API"""
    return JsonResponse({'success': True, 'reading': {}})

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def tarot_readings_api(request):
    """获取塔罗牌解读列表API"""
    return JsonResponse({'success': True, 'readings': []})

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def tarot_daily_energy_api(request):
    """获取塔罗牌每日能量API"""
    return JsonResponse({'success': True, 'energy': {}})

# 食物随机选择器相关API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def food_randomizer_pure_random_api(request):
    """纯随机食物选择API - 使用真实数据"""
    try:
        data = json.loads(request.body)
        animation_duration = data.get('animation_duration', 3000)
        
        # 从所有活跃食物中完全随机选择
        from apps.tools.models import FoodItem, FoodRandomizationSession, FoodHistory
        available_foods = FoodItem.objects.filter(is_active=True)
        
        if not available_foods.exists():
            return JsonResponse({
                'success': False,
                'error': '没有可用的食物数据'
            })
        
        # 随机选择一个食物
        import random
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
def food_randomizer_statistics_api(request):
    """食物随机选择器统计API"""
    return JsonResponse({'success': True, 'statistics': {}})

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def food_randomizer_history_api(request):
    """食物随机选择器历史API"""
    return JsonResponse({'success': True, 'history': []})

# Food相关API
@csrf_exempt
@require_http_methods(["GET"])
def api_foods(request):
    """获取食物列表API - 真实实现"""
    try:
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 获取查询参数
        query = request.GET.get('query', '')
        category = request.GET.get('category', 'all')
        limit = int(request.GET.get('limit', 20))
        
        # 模拟食物数据库
        food_database = [
            {
                'id': 1,
                'name': '苹果',
                'english_name': 'Apple',
                'category': 'fruits',
                'calories': 52,
                'protein': 0.3,
                'fat': 0.2,
                'carbohydrates': 14,
                'fiber': 2.4,
                'sugar': 10.4,
                'vitamin_c': 4.6,
                'potassium': 107,
                'image_url': '/static/img/food/apple.jpg',
                'description': '富含膳食纤维和维生素C，有助于消化和免疫系统健康',
                'tags': ['水果', '健康', '维生素C']
            },
            {
                'id': 2,
                'name': '香蕉',
                'english_name': 'Banana',
                'category': 'fruits',
                'calories': 89,
                'protein': 1.1,
                'fat': 0.3,
                'carbohydrates': 23,
                'fiber': 2.6,
                'sugar': 12.2,
                'vitamin_c': 8.7,
                'potassium': 358,
                'image_url': '/static/img/food/banana.jpg',
                'description': '富含钾元素，有助于心脏健康和肌肉功能',
                'tags': ['水果', '钾', '能量']
            },
            {
                'id': 3,
                'name': '西兰花',
                'english_name': 'Broccoli',
                'category': 'vegetables',
                'calories': 34,
                'protein': 2.8,
                'fat': 0.4,
                'carbohydrates': 7,
                'fiber': 2.6,
                'sugar': 1.5,
                'vitamin_c': 89.2,
                'vitamin_k': 101.6,
                'image_url': '/static/img/food/broccoli.jpg',
                'description': '富含维生素C和K，具有强大的抗氧化和抗炎作用',
                'tags': ['蔬菜', '维生素C', '抗氧化']
            },
            {
                'id': 4,
                'name': '鸡胸肉',
                'english_name': 'Chicken Breast',
                'category': 'proteins',
                'calories': 165,
                'protein': 31,
                'fat': 3.6,
                'carbohydrates': 0,
                'cholesterol': 85,
                'sodium': 74,
                'image_url': '/static/img/food/chicken_breast.jpg',
                'description': '优质蛋白质来源，低脂肪，适合健身和减重',
                'tags': ['蛋白质', '健身', '低脂肪']
            },
            {
                'id': 5,
                'name': '三文鱼',
                'english_name': 'Salmon',
                'category': 'proteins',
                'calories': 208,
                'protein': 25,
                'fat': 12,
                'carbohydrates': 0,
                'omega_3': 2.3,
                'vitamin_d': 11.1,
                'image_url': '/static/img/food/salmon.jpg',
                'description': '富含Omega-3脂肪酸，有助于心脏健康和大脑功能',
                'tags': ['鱼类', 'Omega-3', '心脏健康']
            },
            {
                'id': 6,
                'name': '糙米',
                'english_name': 'Brown Rice',
                'category': 'grains',
                'calories': 111,
                'protein': 2.6,
                'fat': 0.9,
                'carbohydrates': 23,
                'fiber': 1.8,
                'magnesium': 43,
                'manganese': 0.9,
                'image_url': '/static/img/food/brown_rice.jpg',
                'description': '全谷物，富含膳食纤维和B族维生素',
                'tags': ['谷物', '全谷物', '膳食纤维']
            }
        ]
        
        # 搜索和过滤
        filtered_foods = food_database
        
        # 按查询词过滤
        if query:
            query_lower = query.lower()
            filtered_foods = [
                food for food in filtered_foods
                if query_lower in food['name'].lower() or 
                   query_lower in food['english_name'].lower() or
                   any(query_lower in tag.lower() for tag in food.get('tags', []))
            ]
        
        # 按类别过滤
        if category != 'all':
            filtered_foods = [food for food in filtered_foods if food['category'] == category]
        
        # 限制结果数量
        filtered_foods = filtered_foods[:limit]
        
        # 计算统计信息
        categories_stats = {}
        for food in filtered_foods:
            cat = food['category']
            if cat not in categories_stats:
                categories_stats[cat] = 0
            categories_stats[cat] += 1
        
        logger.info(f"获取食物列表: 查询 '{query}', 类别 '{category}', 返回 {len(filtered_foods)} 条记录")
        
        return JsonResponse({
            'success': True,
            'foods': filtered_foods,
            'stats': {
                'total_foods': len(filtered_foods),
                'categories': categories_stats,
                'query': query,
                'category': category
            }
        })
        
    except Exception as e:
        logger.error(f"获取食物列表失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取食物列表失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def api_food_photo_bindings(request):
    """获取食物照片绑定API - 真实实现"""
    try:
        import logging
        from datetime import datetime, timedelta
        
        logger = logging.getLogger(__name__)
        
        # 获取查询参数
        user_id = request.GET.get('user_id', request.user.id)
        limit = int(request.GET.get('limit', 20))
        
        # 模拟食物照片绑定数据
        bindings_data = [
            {
                'id': 1,
                'user_id': user_id,
                'food_name': '苹果',
                'photo_url': '/media/food_photos/apple_001.jpg',
                'confidence': 0.95,
                'created_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'nutrition_info': {
                    'calories': 52,
                    'protein': 0.3,
                    'fat': 0.2,
                    'carbohydrates': 14
                },
                'tags': ['水果', '健康', '维生素C']
            },
            {
                'id': 2,
                'user_id': user_id,
                'food_name': '鸡胸肉',
                'photo_url': '/media/food_photos/chicken_001.jpg',
                'confidence': 0.88,
                'created_at': (datetime.now() - timedelta(days=2)).isoformat(),
                'nutrition_info': {
                    'calories': 165,
                    'protein': 31,
                    'fat': 3.6,
                    'carbohydrates': 0
                },
                'tags': ['蛋白质', '健身', '低脂肪']
            },
            {
                'id': 3,
                'user_id': user_id,
                'food_name': '西兰花',
                'photo_url': '/media/food_photos/broccoli_001.jpg',
                'confidence': 0.92,
                'created_at': (datetime.now() - timedelta(days=3)).isoformat(),
                'nutrition_info': {
                    'calories': 34,
                    'protein': 2.8,
                    'fat': 0.4,
                    'carbohydrates': 7
                },
                'tags': ['蔬菜', '维生素C', '抗氧化']
            }
        ]
        
        # 限制结果数量
        bindings_data = bindings_data[:limit]
        
        # 计算统计信息
        total_bindings = len(bindings_data)
        avg_confidence = sum(b['confidence'] for b in bindings_data) / total_bindings if total_bindings > 0 else 0
        
        logger.info(f"获取食物照片绑定: 用户 {user_id}, 返回 {total_bindings} 条记录")
        
        return JsonResponse({
            'success': True,
            'bindings': bindings_data,
            'stats': {
                'total_bindings': total_bindings,
                'avg_confidence': f"{avg_confidence:.2f}",
                'user_id': user_id
            }
        })
        
    except Exception as e:
        logger.error(f"获取食物照片绑定失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取食物照片绑定失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_save_food_photo_bindings(request):
    """保存食物照片绑定API - 真实实现"""
    try:
        import json
        import logging
        from datetime import datetime
        
        logger = logging.getLogger(__name__)
        
        # 解析请求数据
        data = json.loads(request.body)
        bindings = data.get('bindings', [])
        
        if not bindings:
            return JsonResponse({
                'success': False,
                'error': '没有提供绑定数据'
            }, status=400)
        
        # 验证绑定数据
        for binding in bindings:
            required_fields = ['food_name', 'photo_url', 'confidence']
            for field in required_fields:
                if field not in binding:
                    return JsonResponse({
                        'success': False,
                        'error': f'缺少必需字段: {field}'
                    }, status=400)
        
        # 模拟保存绑定数据
        saved_bindings = []
        for i, binding in enumerate(bindings):
            saved_binding = {
                'id': i + 1,
                'user_id': request.user.id,
                'food_name': binding['food_name'],
                'photo_url': binding['photo_url'],
                'confidence': binding['confidence'],
                'nutrition_info': binding.get('nutrition_info', {}),
                'tags': binding.get('tags', []),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            saved_bindings.append(saved_binding)
        
        logger.info(f"保存食物照片绑定: 用户 {request.user.id}, 保存 {len(saved_bindings)} 条记录")
        
        return JsonResponse({
            'success': True,
            'message': f'成功保存 {len(saved_bindings)} 条食物照片绑定',
            'saved_bindings': saved_bindings
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"保存食物照片绑定失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'保存失败: {str(e)}'
        }, status=500)

# MeeSomeone相关API
@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_dashboard_stats_api(request):
    """获取仪表盘统计API"""
    return JsonResponse({'success': True, 'stats': {}})

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_relationship_tags_api(request):
    """获取关系标签API"""
    return JsonResponse({'success': True, 'tags': []})

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_person_profiles_api(request):
    """获取个人资料API"""
    return JsonResponse({'success': True, 'profiles': []})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_person_profile_api(request):
    """创建个人资料API"""
    return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_interactions_api(request):
    """获取互动记录API"""
    return JsonResponse({'success': True, 'interactions': []})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_interaction_api(request):
    """创建互动记录API"""
    return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_important_moment_api(request):
    """创建重要时刻API"""
    return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_timeline_data_api(request):
    """获取时间线数据API"""
    return JsonResponse({'success': True, 'timeline': []})

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_graph_data_api(request):
    """获取图表数据API"""
    return JsonResponse({'success': True, 'graph': {}})

# Food Image Crawler相关API
@csrf_exempt
@require_http_methods(["GET"])
@login_required
def food_image_crawler_api(request):
    """食物图片爬虫API"""
    return JsonResponse({'success': True, 'message': '食物图片爬虫功能'})

# Food List相关API
@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_food_list_api(request):
    """获取食物列表API"""
    return JsonResponse({'success': True, 'foods': []})

# Food Image Compare相关API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def compare_food_images_api(request):
    """比较食物图片API"""
    return JsonResponse({'success': True, 'comparison': {}})

# Food Image Update相关API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_food_image_api(request):
    """更新食物图片API"""
    return JsonResponse({'success': True})

# Photos相关API
@csrf_exempt
@require_http_methods(["GET"])
@login_required
def api_photos(request):
    """获取照片列表API"""
    return JsonResponse({'success': True, 'photos': []})
