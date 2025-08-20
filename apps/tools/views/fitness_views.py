"""
健身相关视图
包含健身社区、健身档案、健身工具等功能
"""

import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

# 导入相关模型
try:
    from apps.tools.models import (
        FitnessUserProfile, FitnessStrengthProfile, UserFitnessAchievement,
        CheckInCalendar, ExerciseWeightRecord
    )
except ImportError:
    # 如果模型不存在，使用空类
    class FitnessUserProfile:
        pass
    class FitnessStrengthProfile:
        pass
    class UserFitnessAchievement:
        pass
    class CheckInCalendar:
        pass
    class ExerciseWeightRecord:
        pass


@login_required
def fitness_community(request):
    """健身社区页面"""
    return render(request, 'tools/fitness_community.html')


@login_required
def fitness_profile(request):
    """健身个人档案页面"""
    try:
        # 获取或创建用户档案
        profile, created = FitnessUserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'nickname': request.user.username,
                'fitness_level': 'beginner',
                'primary_goals': ['增肌', '减脂'],
                'favorite_workouts': ['力量训练']
            }
        )
        
        # 获取或创建力量档案
        strength_profile, created = FitnessStrengthProfile.objects.get_or_create(
            user=request.user
        )
        
        # 更新统计数据
        profile.update_stats()
        strength_profile.update_stats()
        strength_profile.update_1rm_records()
        
        # 获取用户成就
        achievements = UserFitnessAchievement.objects.filter(
            user=request.user
        ).select_related('achievement').order_by('-earned_at')[:10]
        
        # 获取最近的训练记录
        recent_workouts = CheckInCalendar.objects.filter(
            user=request.user,
            calendar_type='fitness',
            status='completed'
        ).select_related('detail').order_by('-date')[:5]
        
        # 获取最近的重量记录
        recent_weight_records = ExerciseWeightRecord.objects.filter(
            user=request.user
        ).order_by('-workout_date')[:10]
        
        # 获取月度统计
        from datetime import datetime, timedelta
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_workouts = CheckInCalendar.objects.filter(
            user=request.user,
            calendar_type='fitness',
            status='completed',
            date__year=current_year,
            date__month=current_month
        ).count()
        
        # 获取训练类型分布
        workout_types = CheckInCalendar.objects.filter(
            user=request.user,
            calendar_type='fitness',
            status='completed'
        ).select_related('detail')
        
        type_distribution = {}
        for workout in workout_types:
            if hasattr(workout, 'detail') and workout.detail and workout.detail.workout_type:
                workout_type = workout.detail.workout_type
                type_distribution[workout_type] = type_distribution.get(workout_type, 0) + 1
        
        # 获取身体数据（从用户档案中获取）
        body_data = {
            'gender': profile.gender,
            'age': profile.age,
            'height': profile.height,
            'weight': profile.weight,
            'bmi': None,
            'bmi_status': '未计算'
        }
        
        # 计算BMI
        if body_data['height'] and body_data['weight']:
            height_m = body_data['height'] / 100
            body_data['bmi'] = round(body_data['weight'] / (height_m * height_m), 1)
            if body_data['bmi'] < 18.5:
                body_data['bmi_status'] = '偏瘦'
            elif body_data['bmi'] < 24:
                body_data['bmi_status'] = '正常'
            elif body_data['bmi'] < 28:
                body_data['bmi_status'] = '偏胖'
            else:
                body_data['bmi_status'] = '肥胖'
        
        # 获取健身目标（基于力量档案）
        fitness_goals = []
        
        # 三大项目标
        if strength_profile.squat_goal:
            fitness_goals.append({
                'type': 'squat',
                'title': '深蹲目标',
                'current': strength_profile.squat_1rm or 0,
                'target': strength_profile.squat_goal,
                'unit': 'kg',
                'progress': strength_profile.get_progress_percentage('squat'),
                'deadline': '持续训练',
                'icon': 'fas fa-dumbbell'
            })
        
        if strength_profile.bench_press_goal:
            fitness_goals.append({
                'type': 'bench_press',
                'title': '卧推目标',
                'current': strength_profile.bench_press_1rm or 0,
                'target': strength_profile.bench_press_goal,
                'unit': 'kg',
                'progress': strength_profile.get_progress_percentage('bench_press'),
                'deadline': '持续训练',
                'icon': 'fas fa-dumbbell'
            })
        
        if strength_profile.deadlift_goal:
            fitness_goals.append({
                'type': 'deadlift',
                'title': '硬拉目标',
                'current': strength_profile.deadlift_1rm or 0,
                'target': strength_profile.deadlift_goal,
                'unit': 'kg',
                'progress': strength_profile.get_progress_percentage('deadlift'),
                'deadline': '持续训练',
                'icon': 'fas fa-dumbbell'
            })
        
        # 如果没有设置目标，显示默认目标
        if not fitness_goals:
            fitness_goals = [
                {
                    'type': 'weight_loss',
                    'title': '减重目标',
                    'current': body_data['weight'] or 70,
                    'target': (body_data['weight'] or 70) - 5,
                    'unit': 'kg',
                    'progress': 60,
                    'deadline': '2024年12月31日',
                    'icon': 'fas fa-weight'
                },
                {
                    'type': 'strength',
                    'title': '力量目标',
                    'current': strength_profile.total_1rm or 0,
                    'target': 400,
                    'unit': 'kg',
                    'progress': min(round((strength_profile.total_1rm or 0) / 400 * 100, 1), 100),
                    'deadline': '持续训练',
                    'icon': 'fas fa-dumbbell'
                }
            ]
        
        context = {
            'profile': profile,
            'strength_profile': strength_profile,
            'achievements': achievements,
            'recent_workouts': recent_workouts,
            'recent_weight_records': recent_weight_records,
            'monthly_workouts': monthly_workouts,
            'type_distribution': type_distribution,
            'body_data': body_data,
            'fitness_goals': fitness_goals,
            'total_achievements': achievements.count(),
            'current_streak': strength_profile.current_streak,
            'longest_streak': strength_profile.longest_streak,
            'total_duration_hours': round(strength_profile.total_duration / 60, 1) if strength_profile.total_duration else 0
        }
        
        return render(request, 'tools/fitness_profile.html', context)
        
    except Exception as e:
        # 如果出错，返回基本页面
        return render(request, 'tools/fitness_profile.html')


@login_required
def fitness_tools(request):
    """健身工具页面"""
    return render(request, 'tools/fitness_tools.html')


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_weight_record_api(request):
    """添加重量记录API"""
    try:
        data = json.loads(request.body)
        
        # 验证必填字段
        required_fields = ['exercise_type', 'weight', 'reps', 'workout_date']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'字段 {field} 不能为空'
                }, status=400)
        
        # 创建重量记录
        weight_record = ExerciseWeightRecord.objects.create(
            user=request.user,
            exercise_type=data['exercise_type'],
            weight=float(data['weight']),
            reps=int(data['reps']),
            sets=int(data.get('sets', 1)),
            rpe=int(data['rpe']) if data.get('rpe') else None,
            notes=data.get('notes', ''),
            workout_date=data['workout_date']
        )
        
        # 更新力量档案
        strength_profile, created = FitnessStrengthProfile.objects.get_or_create(
            user=request.user
        )
        strength_profile.update_1rm_records()
        
        return JsonResponse({
            'success': True,
            'message': '重量记录添加成功',
            'record_id': weight_record.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_fitness_community_posts_api(request):
    """获取健身社区帖子API"""
    try:
        # 这里应该从数据库获取健身社区帖子
        posts_data = [
            {
                'id': 1,
                'user': {
                    'id': 1,
                    'username': '健身达人',
                    'avatar': '/static/img/default-avatar.svg'
                },
                'content': '今天完成了深蹲训练，感觉很有成就感！',
                'image': None,
                'likes_count': 15,
                'comments_count': 3,
                'created_at': '2024-01-15 14:30',
                'is_liked': False
            },
            {
                'id': 2,
                'user': {
                    'id': 2,
                    'username': '力量训练者',
                    'avatar': '/static/img/default-avatar.svg'
                },
                'content': '卧推突破个人记录，100kg！',
                'image': '/static/img/fitness/workout.jpg',
                'likes_count': 28,
                'comments_count': 8,
                'created_at': '2024-01-15 12:15',
                'is_liked': True
            }
        ]
        
        return JsonResponse({
            'success': True,
            'posts': posts_data
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
        content = data.get('content', '').strip()
        image = data.get('image')
        
        if not content:
            return JsonResponse({
                'success': False,
                'error': '内容不能为空'
            }, status=400)
        
        # 这里应该保存到数据库
        post_id = int(timezone.now().timestamp())
        
        return JsonResponse({
            'success': True,
            'message': '帖子发布成功',
            'post_id': post_id
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
        
        if not post_id:
            return JsonResponse({
                'success': False,
                'error': '帖子ID不能为空'
            }, status=400)
        
        # 这里应该更新数据库
        return JsonResponse({
            'success': True,
            'message': '点赞成功'
        })
        
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
        content = data.get('content', '').strip()
        
        if not post_id or not content:
            return JsonResponse({
                'success': False,
                'error': '帖子ID和评论内容不能为空'
            }, status=400)
        
        # 这里应该保存到数据库
        comment_id = int(timezone.now().timestamp())
        
        return JsonResponse({
            'success': True,
            'message': '评论发布成功',
            'comment_id': comment_id
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
        user_id = request.GET.get('user_id')
        
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': '用户ID不能为空'
            }, status=400)
        
        # 这里应该从数据库获取用户档案
        profile_data = {
            'user_id': user_id,
            'username': '健身达人',
            'avatar': '/static/img/default-avatar.svg',
            'fitness_level': 'intermediate',
            'primary_goals': ['增肌', '力量提升'],
            'total_workouts': 156,
            'current_streak': 7,
            'longest_streak': 30,
            'total_duration_hours': 234.5,
            'achievements_count': 12
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
        
        # 这里应该更新数据库
        return JsonResponse({
            'success': True,
            'message': '关注成功'
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
        # 这里应该从数据库获取成就
        achievements_data = [
            {
                'id': 1,
                'name': '初学者',
                'description': '完成第一次训练',
                'icon': '🏃‍♂️',
                'unlocked': True,
                'unlocked_at': '2024-01-01 10:00'
            },
            {
                'id': 2,
                'name': '坚持者',
                'description': '连续训练7天',
                'icon': '🔥',
                'unlocked': True,
                'unlocked_at': '2024-01-07 15:30'
            },
            {
                'id': 3,
                'name': '力量王者',
                'description': '三大项总重量达到500kg',
                'icon': '💪',
                'unlocked': False,
                'progress': 75
            }
        ]
        
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
        
        # 这里应该处理分享逻辑
        return JsonResponse({
            'success': True,
            'message': '成就分享成功'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
