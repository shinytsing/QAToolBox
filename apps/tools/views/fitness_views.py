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
    from apps.tools.models.legacy_models import (
        FitnessUserProfile, FitnessStrengthProfile, UserFitnessAchievement,
        CheckInCalendar, ExerciseWeightRecord, FitnessAchievement, TrainingPlan
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
    class TrainingPlan:
        pass
    class FitnessAchievement:
        pass


@login_required
def fitness_community(request):
    """健身社区页面"""
    return render(request, 'tools/fitness_community.html')


@login_required
def training_mode_selector(request):
    """训练模式选择页面"""
    return render(request, 'tools/training_mode_selector.html')


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
def save_training_plan_api(request):
    """保存周训练计划"""
    try:
        data = json.loads(request.body)
        name = data.get('plan_name') or '我的训练计划'
        mode = data.get('mode') or '五分化'
        cycle_weeks = int(data.get('cycle_weeks') or 8)
        week_schedule = data.get('week_schedule') or []

        plan = TrainingPlan.objects.create(
            user=request.user,
            name=name,
            mode=mode,
            cycle_weeks=cycle_weeks,
            week_schedule=week_schedule,
        )

        return JsonResponse({'success': True, 'plan_id': plan.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def list_training_plans_api(request):
    """列出用户训练计划"""
    plans = TrainingPlan.objects.filter(user=request.user).order_by('-updated_at')[:20]
    results = []
    for p in plans:
        results.append({
            'id': p.id,
            'name': p.name,
            'mode': p.mode,
            'cycle_weeks': p.cycle_weeks,
            'is_active': p.is_active,
            'week_schedule': p.week_schedule,
            'created_at': p.created_at.isoformat(),
            'updated_at': p.updated_at.isoformat(),
        })
    return JsonResponse({'success': True, 'plans': results})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_training_plan_api(request, plan_id):
    """获取训练计划详情"""
    try:
        plan = TrainingPlan.objects.get(id=plan_id, user=request.user)
        return JsonResponse({
            'success': True,
            'plan': {
                'id': plan.id,
                'name': plan.name,
                'mode': plan.mode,
                'cycle_weeks': plan.cycle_weeks,
                'week_schedule': plan.week_schedule,
                'is_active': plan.is_active,
                'visibility': plan.visibility,
                'created_at': plan.created_at.isoformat(),
                'updated_at': plan.updated_at.isoformat()
            }
        })
    except TrainingPlan.DoesNotExist:
        return JsonResponse({'success': False, 'error': '计划不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def equip_badge_api(request):
    """佩戴成就徽章"""
    try:
        data = json.loads(request.body)
        achievement_id = data.get('achievement_id')
        if not achievement_id:
            return JsonResponse({'success': False, 'error': '缺少成就ID'}, status=400)

        achievement = FitnessAchievement.objects.get(id=achievement_id)
        profile, _ = FitnessUserProfile.objects.get_or_create(user=request.user)
        profile.selected_badge = achievement
        profile.save(update_fields=['selected_badge'])

        # 标记用户该成就为已佩戴
        UserFitnessAchievement.objects.filter(user=request.user).update(is_equipped=False)
        ufa, _ = UserFitnessAchievement.objects.get_or_create(user=request.user, achievement=achievement)
        ufa.is_equipped = True
        ufa.save(update_fields=['is_equipped'])

        return JsonResponse({'success': True})
    except FitnessAchievement.DoesNotExist:
        return JsonResponse({'success': False, 'error': '成就不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


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


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_active_training_plan_api(request):
    """获取用户当前激活的训练计划"""
    try:
        # 获取用户最近的激活计划
        active_plan = TrainingPlan.objects.filter(
            user=request.user, 
            is_active=True
        ).order_by('-updated_at').first()
        
        if not active_plan:
            return JsonResponse({
                'success': True,
                'has_plan': False,
                'message': '暂无激活的训练计划'
            })
        
        return JsonResponse({
            'success': True,
            'has_plan': True,
            'plan': {
                'id': active_plan.id,
                'name': active_plan.name,
                'mode': active_plan.mode,
                'cycle_weeks': active_plan.cycle_weeks,
                'week_schedule': active_plan.week_schedule,
                'updated_at': active_plan.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def apply_training_plan_api(request):
    """应用训练计划（设置为激活状态）"""
    try:
        data = json.loads(request.body)
        plan_id = data.get('plan_id')
        
        if not plan_id:
            return JsonResponse({'success': False, 'error': '计划ID不能为空'}, status=400)
        
        # 获取计划
        plan = TrainingPlan.objects.get(id=plan_id, user=request.user)
        
        # 将其他计划设为非激活状态
        TrainingPlan.objects.filter(user=request.user).update(is_active=False)
        
        # 激活当前计划
        plan.is_active = True
        plan.save(update_fields=['is_active'])
        
        return JsonResponse({
            'success': True,
            'message': f'已应用计划：{plan.name}',
            'plan': {
                'id': plan.id,
                'name': plan.name,
                'mode': plan.mode,
                'cycle_weeks': plan.cycle_weeks,
                'week_schedule': plan.week_schedule
            }
        })
        
    except TrainingPlan.DoesNotExist:
        return JsonResponse({'success': False, 'error': '计划不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_training_plan_templates_api(request):
    """获取训练计划模板"""
    try:
        # 使用新的模板数据文件
        from apps.tools.services.fitness_template_data import get_all_templates
        
        all_templates = get_all_templates()
        
        # 将模板转换为数组格式（保持向后兼容）
        templates = []
        for template_id, template in all_templates.items():
            template_data = {
                'id': template_id,
                'name': template['name'],
                'description': template['description'],
                'mode': template['mode'],
                'cycle_weeks': template['cycle_weeks'],
                'difficulty': template['difficulty'],
                'target_goals': template['target_goals'],
                'week_schedule': template['week_schedule']
            }
            templates.append(template_data)
        
        # 备用：如果导入失败，返回默认模板
        if not templates:
            templates = [
                {
                    'id': 'template_5day_split',
                    'name': '五分化力量训练',
                    'description': '经典五分化训练，适合中高级训练者',
                    'mode': '五分化',
                    'cycle_weeks': 8,
                    'difficulty': 'intermediate',
                    'target_goals': ['增肌', '力量提升'],
                    'week_schedule': [
                        {
                            'weekday': '周一', 
                            'body_parts': ['胸部'], 
                            'modules': {
                                'warmup': [
                                    {'name': '动态拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                                    {'name': '轻重量卧推', 'sets': 2, 'reps': 15, 'weight': '空杆', 'rest': '60秒'}
                                ],
                                'main': [
                                    {'name': '杠铃卧推', 'sets': 4, 'reps': '8-10', 'weight': '75kg', 'rest': '3分钟'},
                                    {'name': '哑铃卧推', 'sets': 3, 'reps': '10-12', 'weight': '30kg', 'rest': '90秒'},
                                    {'name': '上斜哑铃推举', 'sets': 3, 'reps': '10-12', 'weight': '25kg', 'rest': '90秒'}
                                ],
                                'accessory': [
                                    {'name': '哑铃飞鸟', 'sets': 3, 'reps': '12-15', 'weight': '15kg', 'rest': '60秒'},
                                    {'name': '双杠臂屈伸', 'sets': 3, 'reps': '10-12', 'weight': '自重', 'rest': '90秒'}
                                ],
                                'cooldown': [
                                    {'name': '胸部拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                                ]
                            }
                        },
                    {
                        'weekday': '周二', 
                        'body_parts': ['背部'], 
                        'modules': {
                            'warmup': [
                                {'name': '动态拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                                {'name': '轻重量划船', 'sets': 2, 'reps': 15, 'weight': '轻重量', 'rest': '60秒'}
                            ],
                            'main': [
                                {'name': '硬拉', 'sets': 4, 'reps': '6-8', 'weight': '100kg', 'rest': '3分钟'},
                                {'name': '引体向上', 'sets': 4, 'reps': '8-10', 'weight': '自重', 'rest': '2分钟'},
                                {'name': '杠铃划船', 'sets': 3, 'reps': '10-12', 'weight': '60kg', 'rest': '90秒'}
                            ],
                            'accessory': [
                                {'name': '坐姿划船', 'sets': 3, 'reps': '12-15', 'weight': '50kg', 'rest': '60秒'},
                                {'name': '高位下拉', 'sets': 3, 'reps': '12-15', 'weight': '45kg', 'rest': '60秒'}
                            ],
                            'cooldown': [
                                {'name': '背部拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                            ]
                        }
                    },
                    {'weekday': '周三', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {
                        'weekday': '周四', 
                        'body_parts': ['肩部'], 
                        'modules': {
                            'warmup': [
                                {'name': '肩部环绕', 'sets': 1, 'reps': '2分钟', 'weight': '', 'rest': ''},
                                {'name': '轻重量推举', 'sets': 2, 'reps': 15, 'weight': '10kg', 'rest': '60秒'}
                            ],
                            'main': [
                                {'name': '站姿推举', 'sets': 4, 'reps': '8-10', 'weight': '40kg', 'rest': '2分钟'},
                                {'name': '哑铃侧平举', 'sets': 4, 'reps': '12-15', 'weight': '12kg', 'rest': '90秒'},
                                {'name': '哑铃前平举', 'sets': 3, 'reps': '12-15', 'weight': '10kg', 'rest': '60秒'}
                            ],
                            'accessory': [
                                {'name': '反向飞鸟', 'sets': 3, 'reps': '15-20', 'weight': '8kg', 'rest': '60秒'},
                                {'name': '直立划船', 'sets': 3, 'reps': '12-15', 'weight': '30kg', 'rest': '60秒'}
                            ],
                            'cooldown': [
                                {'name': '肩部拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                            ]
                        }
                    },
                    {
                        'weekday': '周五', 
                        'body_parts': ['腿部'], 
                        'modules': {
                            'warmup': [
                                {'name': '动态热身', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                                {'name': '轻重量深蹲', 'sets': 2, 'reps': 15, 'weight': '空杆', 'rest': '60秒'}
                            ],
                            'main': [
                                {'name': '杠铃深蹲', 'sets': 4, 'reps': '8-10', 'weight': '80kg', 'rest': '3分钟'},
                                {'name': '罗马尼亚硬拉', 'sets': 3, 'reps': '10-12', 'weight': '60kg', 'rest': '2分钟'},
                                {'name': '保加利亚分腿蹲', 'sets': 3, 'reps': '12-15', 'weight': '20kg', 'rest': '90秒'}
                            ],
                            'accessory': [
                                {'name': '腿举', 'sets': 3, 'reps': '15-20', 'weight': '100kg', 'rest': '90秒'},
                                {'name': '腿弯举', 'sets': 3, 'reps': '12-15', 'weight': '40kg', 'rest': '60秒'}
                            ],
                            'cooldown': [
                                {'name': '腿部拉伸', 'sets': 1, 'reps': '8分钟', 'weight': '', 'rest': ''}
                            ]
                        }
                    },
                    {
                        'weekday': '周六', 
                        'body_parts': ['手臂'], 
                        'modules': {
                            'warmup': [
                                {'name': '手臂环绕', 'sets': 1, 'reps': '2分钟', 'weight': '', 'rest': ''},
                                {'name': '轻重量弯举', 'sets': 2, 'reps': 15, 'weight': '10kg', 'rest': '60秒'}
                            ],
                            'main': [
                                {'name': '杠铃弯举', 'sets': 4, 'reps': '10-12', 'weight': '35kg', 'rest': '90秒'},
                                {'name': '窄距卧推', 'sets': 4, 'reps': '10-12', 'weight': '50kg', 'rest': '90秒'},
                                {'name': '哑铃弯举', 'sets': 3, 'reps': '12-15', 'weight': '15kg', 'rest': '60秒'}
                            ],
                            'accessory': [
                                {'name': '三头肌下压', 'sets': 3, 'reps': '12-15', 'weight': '30kg', 'rest': '60秒'},
                                {'name': '锤式弯举', 'sets': 3, 'reps': '12-15', 'weight': '12kg', 'rest': '60秒'}
                            ],
                            'cooldown': [
                                {'name': '手臂拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                            ]
                        }
                    },
                    {'weekday': '周日', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}}
                ]
            },
            {
                'id': 'template_3day_split',
                'name': '三分化力量训练',
                'description': '适合初中级训练者的三分化计划',
                'mode': '三分化',
                'cycle_weeks': 6,
                'difficulty': 'beginner',
                'target_goals': ['增肌', '基础力量'],
                'week_schedule': [
                    {
                        'weekday': '周一', 
                        'body_parts': ['胸部', '肩部', '三头肌'], 
                        'modules': {
                            'warmup': [
                                {'name': '动态热身', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                                {'name': '轻重量推举', 'sets': 2, 'reps': 15, 'weight': '轻重量', 'rest': '60秒'}
                            ],
                            'main': [
                                {'name': '哑铃卧推', 'sets': 3, 'reps': '10-12', 'weight': '25kg', 'rest': '90秒'},
                                {'name': '哑铃推举', 'sets': 3, 'reps': '10-12', 'weight': '20kg', 'rest': '90秒'},
                                {'name': '双杠臂屈伸', 'sets': 3, 'reps': '8-12', 'weight': '自重', 'rest': '90秒'}
                            ],
                            'accessory': [
                                {'name': '哑铃侧平举', 'sets': 3, 'reps': '12-15', 'weight': '10kg', 'rest': '60秒'},
                                {'name': '三头肌下压', 'sets': 3, 'reps': '12-15', 'weight': '25kg', 'rest': '60秒'}
                            ],
                            'cooldown': [
                                {'name': '上肢拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                            ]
                        }
                    },
                    {'weekday': '周二', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {
                        'weekday': '周三', 
                        'body_parts': ['背部', '二头肌'], 
                        'modules': {
                            'warmup': [
                                {'name': '动态热身', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                                {'name': '轻重量划船', 'sets': 2, 'reps': 15, 'weight': '轻重量', 'rest': '60秒'}
                            ],
                            'main': [
                                {'name': '高位下拉', 'sets': 3, 'reps': '10-12', 'weight': '40kg', 'rest': '90秒'},
                                {'name': '坐姿划船', 'sets': 3, 'reps': '10-12', 'weight': '45kg', 'rest': '90秒'},
                                {'name': '杠铃弯举', 'sets': 3, 'reps': '10-12', 'weight': '30kg', 'rest': '90秒'}
                            ],
                            'accessory': [
                                {'name': '哑铃弯举', 'sets': 3, 'reps': '12-15', 'weight': '12kg', 'rest': '60秒'},
                                {'name': '锤式弯举', 'sets': 3, 'reps': '12-15', 'weight': '10kg', 'rest': '60秒'}
                            ],
                            'cooldown': [
                                {'name': '背部和手臂拉伸', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''}
                            ]
                        }
                    },
                    {'weekday': '周四', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {
                        'weekday': '周五', 
                        'body_parts': ['腿部'], 
                        'modules': {
                            'warmup': [
                                {'name': '动态热身', 'sets': 1, 'reps': '5分钟', 'weight': '', 'rest': ''},
                                {'name': '轻重量深蹲', 'sets': 2, 'reps': 15, 'weight': '空杆', 'rest': '60秒'}
                            ],
                            'main': [
                                {'name': '哑铃深蹲', 'sets': 3, 'reps': '12-15', 'weight': '20kg', 'rest': '2分钟'},
                                {'name': '腿举', 'sets': 3, 'reps': '15-20', 'weight': '80kg', 'rest': '90秒'},
                                {'name': '腿弯举', 'sets': 3, 'reps': '12-15', 'weight': '35kg', 'rest': '90秒'}
                            ],
                            'accessory': [
                                {'name': '腿屈伸', 'sets': 3, 'reps': '15-20', 'weight': '30kg', 'rest': '60秒'},
                                {'name': '提踵', 'sets': 3, 'reps': '20-25', 'weight': '40kg', 'rest': '60秒'}
                            ],
                            'cooldown': [
                                {'name': '腿部拉伸', 'sets': 1, 'reps': '8分钟', 'weight': '', 'rest': ''}
                            ]
                        }
                    },
                    {'weekday': '周六', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周日', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}}
                ]
            },
            {
                'id': 'template_push_pull_legs',
                'name': '推拉腿训练',
                'description': '经典推拉腿分化，平衡发展',
                'mode': '推拉腿',
                'cycle_weeks': 8,
                'difficulty': 'intermediate',
                'target_goals': ['增肌', '力量平衡'],
                'week_schedule': [
                    {'weekday': '周一', 'body_parts': ['推'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周二', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周三', 'body_parts': ['拉'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周四', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周五', 'body_parts': ['腿'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周六', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周日', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}}
                ]
            },
            {
                'id': 'template_cardio',
                'name': '有氧运动计划',
                'description': '专注心肺功能和减脂的有氧计划',
                'mode': '有氧运动',
                'cycle_weeks': 4,
                'difficulty': 'beginner',
                'target_goals': ['减脂', '心肺功能'],
                'week_schedule': [
                    {'weekday': '周一', 'body_parts': ['有氧'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周二', 'body_parts': ['有氧'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周三', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周四', 'body_parts': ['有氧'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周五', 'body_parts': ['有氧'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周六', 'body_parts': ['有氧'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周日', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}}
                ]
            },
            {
                'id': 'template_functional',
                'name': '功能性训练',
                'description': '提升日常生活运动能力的功能性训练',
                'mode': '功能性训练',
                'cycle_weeks': 6,
                'difficulty': 'beginner',
                'target_goals': ['功能性力量', '运动表现'],
                'week_schedule': [
                    {'weekday': '周一', 'body_parts': ['功能性'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周二', 'body_parts': ['功能性'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周三', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周四', 'body_parts': ['功能性'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周五', 'body_parts': ['功能性'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周六', 'body_parts': ['功能性'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}},
                    {'weekday': '周日', 'body_parts': ['休息'], 'modules': {'warmup': [], 'main': [], 'accessory': [], 'cooldown': []}}
                ]
            }
        ]
        
        # 确保每个模板都有完整的键值对结构，便于前端直接使用
        result = {}
        for template in templates:
            # 为了兼容前端的template_key访问方式，我们用id作为key
            template_key = template['id']
            # 重构数据结构，确保前端可以直接使用
            result[template_key] = {
                'name': template['name'],
                'description': template['description'],
                'mode': template['mode'],
                'difficulty': template['difficulty'],
                'target_goals': template['target_goals'],
                'schedule': template['week_schedule']  # 注意这里用schedule，与enhanced_training_plan_editor.js兼容
            }

        return JsonResponse({
            'success': True,
            'templates': result  # 返回字典格式，方便前端根据key直接访问
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
@login_required
def apply_training_plan_template_api(request):
    """应用训练计划模板（创建新计划并激活）"""
    try:
        # 添加调试信息
        print(f"接收到模板应用请求，用户: {request.user.username}")
        print(f"请求体: {request.body}")
        
        data = json.loads(request.body)
        template_id = data.get('template_id')
        custom_name = data.get('custom_name', '')
        
        print(f"模板ID: {template_id}, 自定义名称: {custom_name}")
        
        if not template_id:
            return JsonResponse({'success': False, 'error': '模板ID不能为空'}, status=400)
        
        # 使用新的模板数据文件
        try:
            print("开始获取模板数据...")
            from apps.tools.services.fitness_template_data import get_all_templates
            
            all_templates = get_all_templates()
            
            # 将模板转换为API需要的格式
            templates_dict = {}
            for template_id, template in all_templates.items():
                templates_dict[template_id] = {
                    'name': template['name'],
                    'description': template['description'],
                    'mode': template['mode'],
                    'difficulty': template['difficulty'],
                    'target_goals': template['target_goals'],
                    'cycle_weeks': template['cycle_weeks'],
                    'schedule': template['week_schedule']
                }
            
            print(f"获取到 {len(templates_dict)} 个模板")
            
        except Exception as template_error:
            print(f"获取模板数据错误: {template_error}")
            return JsonResponse({'success': False, 'error': f'获取模板数据失败: {str(template_error)}'}, status=500)
        
        # 查找指定模板
        template = templates_dict.get(template_id)
        if template:
            template['id'] = template_id  # 确保包含id
            print(f"找到模板: {template['name']}")
        else:
            print(f"未找到模板: {template_id}, 可用模板: {list(templates_dict.keys())}")
            return JsonResponse({'success': False, 'error': f'模板不存在: {template_id}'}, status=404)
        
        # 创建新的训练计划
        plan_name = custom_name or template.get('name', '训练计划')
        
        # 将其他计划设为非激活状态
        try:
            updated_count = TrainingPlan.objects.filter(user=request.user).update(is_active=False)
            print(f"已将 {updated_count} 个计划设为非激活状态")
        except Exception as update_error:
            print(f"更新现有计划状态失败: {update_error}")
            # 这里不直接返回错误，因为这不是致命问题
        
        # 安全地获取模板数据，提供默认值
        template_mode = template.get('mode', 'custom')
        template_weeks = template.get('cycle_weeks', 4)
        template_schedule = template.get('schedule', template.get('week_schedule', []))
        
        print(f"准备创建计划 - 名称: {plan_name}, 模式: {template_mode}, 周期: {template_weeks}")
        print(f"计划安排: {template_schedule}")
        
        # 创建新计划
        try:
            # 确保cycle_weeks是整数
            if not isinstance(template_weeks, int):
                try:
                    template_weeks = int(template_weeks)
                except (ValueError, TypeError):
                    template_weeks = 4
            
            # 确保week_schedule是列表
            if not isinstance(template_schedule, list):
                template_schedule = []
            
            new_plan = TrainingPlan.objects.create(
                user=request.user,
                name=plan_name,
                mode=template_mode,
                cycle_weeks=template_weeks,
                week_schedule=template_schedule,
                is_active=True
            )
            print(f"计划创建成功，ID: {new_plan.id}")
            
        except Exception as create_error:
            import traceback
            print(f"创建计划失败: {create_error}")
            print(traceback.format_exc())
            return JsonResponse({
                'success': False, 
                'error': f'创建计划失败: {str(create_error)}'
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'message': f'已应用模板：{plan_name}',
            'plan': {
                'id': new_plan.id,
                'name': new_plan.name,
                'mode': new_plan.mode,
                'cycle_weeks': new_plan.cycle_weeks,
                'week_schedule': new_plan.week_schedule
            }
        })
        
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return JsonResponse({'success': False, 'error': '请求数据格式错误'}, status=400)
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"应用模板API错误: {error_msg}")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': f'应用模板失败: {error_msg}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def save_training_plan_editor_api(request):
    """保存训练计划编辑器中的计划"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"保存训练计划请求 - 用户: {request.user.username}")
        logger.info(f"请求体长度: {len(request.body)} bytes")
        
        data = json.loads(request.body)
        logger.info(f"解析的数据: {data}")
        
        plan_name = data.get('name', '').strip()
        plan_mode = data.get('mode', '五分化')
        cycle_weeks = data.get('cycle_weeks')
        if cycle_weeks is None or cycle_weeks == '':
            cycle_weeks = 8
        else:
            try:
                cycle_weeks = int(cycle_weeks)
            except (ValueError, TypeError):
                cycle_weeks = 8
        week_schedule = data.get('week_schedule', [])
        plan_id = data.get('plan_id')  # 如果有ID，则更新现有计划
        
        logger.info(f"处理后的数据 - plan_name: {plan_name}, plan_mode: {plan_mode}, cycle_weeks: {cycle_weeks}, plan_id: {plan_id}")
        
        if not plan_name:
            return JsonResponse({'success': False, 'error': '计划名称不能为空'}, status=400)
        
        if not week_schedule:
            return JsonResponse({'success': False, 'error': '训练安排不能为空'}, status=400)
        
        # 如果有plan_id，则更新现有计划，否则创建新计划
        if plan_id:
            try:
                plan = TrainingPlan.objects.get(id=plan_id, user=request.user)
                plan.name = plan_name
                plan.mode = plan_mode
                plan.cycle_weeks = cycle_weeks
                plan.week_schedule = week_schedule
                plan.save()
                message = f'训练计划 "{plan_name}" 已更新'
            except TrainingPlan.DoesNotExist:
                return JsonResponse({'success': False, 'error': '计划不存在或无权限'}, status=404)
        else:
            # 创建新计划
            plan = TrainingPlan.objects.create(
                user=request.user,
                name=plan_name,
                mode=plan_mode,
                cycle_weeks=cycle_weeks,
                week_schedule=week_schedule,
                is_active=False  # 新创建的计划默认不激活
            )
            message = f'训练计划 "{plan_name}" 已保存'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'plan': {
                'id': plan.id,
                'name': plan.name,
                'mode': plan.mode,
                'cycle_weeks': plan.cycle_weeks,
                'week_schedule': plan.week_schedule,
                'is_active': plan.is_active,
                'created_at': plan.created_at.isoformat(),
                'updated_at': plan.updated_at.isoformat()
            }
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {str(e)}")
        return JsonResponse({'success': False, 'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        logger.error(f"保存训练计划异常: {str(e)}")
        logger.error(f"异常类型: {type(e)}")
        import traceback
        logger.error(f"堆栈跟踪: {traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_training_plan_api(request, plan_id):
    """删除训练计划"""
    try:
        plan = TrainingPlan.objects.get(id=plan_id, user=request.user)
        plan_name = plan.name
        plan.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'训练计划 "{plan_name}" 已删除'
        })
        
    except TrainingPlan.DoesNotExist:
        return JsonResponse({'success': False, 'error': '计划不存在或无权限'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def import_training_mode_api(request):
    """一键导入训练模式"""
    try:
        data = json.loads(request.body)
        mode = data.get('mode')
        
        if not mode:
            return JsonResponse({'success': False, 'error': '训练模式不能为空'}, status=400)
        
        # 从模板获取训练计划
        template_plan = TrainingPlan.objects.filter(
            mode=mode, 
            visibility='public'
        ).first()
        
        if not template_plan:
            return JsonResponse({'success': False, 'error': f'未找到{mode}模式的模板'}, status=404)
        
        # 为用户创建个人训练计划
        user_plan = TrainingPlan.objects.create(
            user=request.user,
            name=f"{request.user.username}的{template_plan.name}",
            mode=template_plan.mode,
            cycle_weeks=template_plan.cycle_weeks,
            week_schedule=template_plan.week_schedule,
            visibility='private',
            is_active=True
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'{mode}训练模式导入成功！',
            'plan_id': user_plan.id,
            'plan_name': user_plan.name
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_training_modes_api(request):
    """获取可用的训练模式列表"""
    try:
        # 获取所有模板的训练模式
        modes = TrainingPlan.objects.filter(
            visibility='public'
        ).values_list('mode', flat=True).distinct()
        
        training_modes = []
        for mode in modes:
            template = TrainingPlan.objects.filter(
                mode=mode, 
                visibility='public'
            ).first()
            
            if template:
                training_modes.append({
                    'mode': mode,
                    'name': template.name,
                    'description': f'{mode}训练计划',
                    'difficulty': 'intermediate',
                    'target_goals': ['健身', '增肌'],
                    'cycle_weeks': template.cycle_weeks,
                    'icon': get_mode_icon(mode)
                })
        
        # 如果没有找到模板，返回默认模式
        if not training_modes:
            training_modes = [
                {
                    'mode': 'hypertrophy',
                    'name': '五分化力量训练',
                    'description': '适合中高级训练者的经典五分化训练计划',
                    'difficulty': 'intermediate',
                    'target_goals': ['增肌', '力量提升'],
                    'cycle_weeks': 8,
                    'icon': 'fas fa-dumbbell'
                },
                {
                    'mode': 'general_fitness',
                    'name': '高效三分化训练',
                    'description': '适合初中级训练者的三分化训练计划',
                    'difficulty': 'beginner',
                    'target_goals': ['增肌', '塑形'],
                    'cycle_weeks': 6,
                    'icon': 'fas fa-fire'
                },
                {
                    'mode': 'strength',
                    'name': '经典推拉腿训练',
                    'description': '按运动模式划分的高效训练计划',
                    'difficulty': 'intermediate',
                    'target_goals': ['增肌', '力量', '塑形'],
                    'cycle_weeks': 8,
                    'icon': 'fas fa-arrows-alt'
                },
                {
                    'mode': 'endurance',
                    'name': '全面有氧训练计划',
                    'description': '专注心肺功能提升和脂肪燃烧',
                    'difficulty': 'beginner',
                    'target_goals': ['减脂', '心肺', '耐力'],
                    'cycle_weeks': 6,
                    'icon': 'fas fa-running'
                },
                {
                    'mode': 'functional',
                    'name': '全身功能性训练',
                    'description': '提升运动表现和日常功能',
                    'difficulty': 'intermediate',
                    'target_goals': ['功能性', '平衡', '协调'],
                    'cycle_weeks': 8,
                    'icon': 'fas fa-heartbeat'
                }
            ]
        
        return JsonResponse({
            'success': True,
            'training_modes': training_modes
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def get_mode_icon(mode):
    """获取训练模式图标"""
    icons = {
        'hypertrophy': 'fas fa-dumbbell',
        'general_fitness': 'fas fa-fire',
        'strength': 'fas fa-arrows-alt',
        'endurance': 'fas fa-running',
        'functional': 'fas fa-heartbeat',
        'weight_loss': 'fas fa-burn',
        'powerlifting': 'fas fa-weight-hanging',
        'bodybuilding': 'fas fa-male'
    }
    return icons.get(mode, 'fas fa-cog')
