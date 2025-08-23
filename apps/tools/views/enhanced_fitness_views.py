from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from django.utils import timezone
import json

from apps.tools.models.fitness_achievement_models import (
    FitnessAchievementModule, EnhancedFitnessAchievement, EnhancedUserFitnessAchievement,
    UserBadgeShowcase
)
from apps.tools.models.exercise_library_models import (
    Exercise, BodyPart, Equipment, UserExercisePreference, WorkoutTemplate
)
from apps.tools.models.training_plan_models import (
    EnhancedTrainingPlan, UserTrainingPlan, TrainingSession, PlanLibrary,
    UserPlanCollection, TrainingPlanCategory
)
from apps.tools.models.fitness_models import EnhancedFitnessUserProfile


@login_required
def enhanced_fitness_center(request):
    """增强版健身中心"""
    try:
        # 获取用户档案
        profile, created = EnhancedFitnessUserProfile.objects.get_or_create(user=request.user)
        
        # 获取用户成就统计
        achievement_stats = get_user_achievement_stats(request.user)
        
        # 获取用户当前训练计划
        current_plans = UserTrainingPlan.objects.filter(
            user=request.user,
            status='in_progress'
        ).select_related('plan')[:3]
        
        # 获取推荐的训练计划
        recommended_plans = get_recommended_plans(request.user)
        
        # 获取最近的训练会话
        recent_sessions = TrainingSession.objects.filter(
            user_plan__user=request.user
        ).order_by('-actual_date')[:5]
        
        # 获取用户收藏的动作
        favorite_exercises = UserExercisePreference.objects.filter(
            user=request.user,
            is_favorite=True
        ).select_related('exercise')[:6]
        
        context = {
            'profile': profile,
            'achievement_stats': achievement_stats,
            'current_plans': current_plans,
            'recommended_plans': recommended_plans,
            'recent_sessions': recent_sessions,
            'favorite_exercises': favorite_exercises,
        }
        
        return render(request, 'tools/enhanced_fitness_center.html', context)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def achievement_dashboard(request):
    """成就仪表盘"""
    try:
        # 获取所有成就模块
        modules = FitnessAchievementModule.objects.filter(is_active=True)
        
        # 获取用户的成就数据
        user_achievements = {}
        module_stats = {}
        
        for module in modules:
            # 获取该模块的所有成就
            all_achievements = EnhancedFitnessAchievement.objects.filter(
                module=module,
                is_active=True
            )
            
            # 获取用户已获得的成就
            earned_achievements = EnhancedUserFitnessAchievement.objects.filter(
                user=request.user,
                achievement__module=module,
                is_completed=True
            ).select_related('achievement')
            
            # 获取进行中的成就
            in_progress_achievements = EnhancedUserFitnessAchievement.objects.filter(
                user=request.user,
                achievement__module=module,
                is_completed=False,
                progress__gt=0
            ).select_related('achievement')
            
            user_achievements[module.name] = {
                'earned': earned_achievements,
                'in_progress': in_progress_achievements,
                'total': all_achievements.count(),
                'earned_count': earned_achievements.count()
            }
            
            # 计算模块统计
            module_stats[module.name] = {
                'completion_rate': (earned_achievements.count() / all_achievements.count() * 100) if all_achievements.count() > 0 else 0,
                'points_earned': sum([ua.achievement.points_reward for ua in earned_achievements])
            }
        
        # 获取用户徽章展示设置
        badge_showcase, created = UserBadgeShowcase.objects.get_or_create(
            user=request.user
        )
        
        context = {
            'modules': modules,
            'user_achievements': user_achievements,
            'module_stats': module_stats,
            'badge_showcase': badge_showcase,
        }
        
        return render(request, 'tools/achievement_dashboard.html', context)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def exercise_library(request):
    """增强版动作库"""
    try:
        # 获取筛选参数
        body_part = request.GET.get('body_part', '')
        difficulty = request.GET.get('difficulty', '')
        equipment = request.GET.get('equipment', '')
        exercise_type = request.GET.get('type', '')
        search = request.GET.get('search', '')
        
        # 构建查询
        exercises = Exercise.objects.filter(is_active=True)
        
        if body_part:
            exercises = exercises.filter(body_parts__name=body_part)
        
        if difficulty:
            exercises = exercises.filter(difficulty=difficulty)
        
        if equipment:
            exercises = exercises.filter(equipment__name=equipment)
        
        if exercise_type:
            exercises = exercises.filter(exercise_type=exercise_type)
        
        if search:
            exercises = exercises.filter(
                Q(name__icontains=search) |
                Q(english_name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # 排序
        sort_by = request.GET.get('sort', 'popularity')
        if sort_by == 'popularity':
            exercises = exercises.order_by('-popularity_score', '-usage_count')
        elif sort_by == 'name':
            exercises = exercises.order_by('name')
        elif sort_by == 'difficulty':
            exercises = exercises.order_by('difficulty', 'name')
        elif sort_by == 'rating':
            exercises = exercises.order_by('-average_rating', 'name')
        
        # 分页
        paginator = Paginator(exercises, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # 获取筛选选项
        body_parts = BodyPart.objects.all().order_by('sort_order')
        equipment_list = Equipment.objects.all().order_by('equipment_type', 'name')
        
        # 获取用户偏好
        user_preferences = {}
        if request.user.is_authenticated:
            prefs = UserExercisePreference.objects.filter(
                user=request.user,
                exercise__in=page_obj
            ).values('exercise_id', 'is_favorite', 'is_mastered')
            user_preferences = {pref['exercise_id']: pref for pref in prefs}
        
        context = {
            'page_obj': page_obj,
            'body_parts': body_parts,
            'equipment_list': equipment_list,
            'user_preferences': user_preferences,
            'current_filters': {
                'body_part': body_part,
                'difficulty': difficulty,
                'equipment': equipment,
                'type': exercise_type,
                'search': search,
                'sort': sort_by
            }
        }
        
        return render(request, 'tools/enhanced_exercise_library.html', context)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def exercise_detail(request, exercise_id):
    """动作详情页面"""
    try:
        exercise = get_object_or_404(Exercise, id=exercise_id, is_active=True)
        
        # 增加浏览次数
        exercise.increment_usage()
        
        # 获取用户偏好
        user_preference, created = UserExercisePreference.objects.get_or_create(
            user=request.user,
            exercise=exercise
        )
        
        # 获取相似动作
        similar_exercises = Exercise.objects.filter(
            body_parts__in=exercise.body_parts.all(),
            is_active=True
        ).exclude(id=exercise.id).distinct()[:6]
        
        # 获取动作变式
        variations = []
        if exercise.variations:
            for variation_name in exercise.variations:
                try:
                    var_exercise = Exercise.objects.get(name=variation_name, is_active=True)
                    variations.append(var_exercise)
                except Exercise.DoesNotExist:
                    pass
        
        context = {
            'exercise': exercise,
            'user_preference': user_preference,
            'similar_exercises': similar_exercises,
            'variations': variations,
        }
        
        return render(request, 'tools/exercise_detail.html', context)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def plan_library(request):
    """计划库"""
    try:
        # 获取筛选参数
        category = request.GET.get('category', '')
        difficulty = request.GET.get('difficulty', '')
        plan_type = request.GET.get('type', '')
        search = request.GET.get('search', '')
        library_type = request.GET.get('library_type', '')
        
        # 构建查询
        plans = PlanLibrary.objects.select_related('plan', 'plan__creator')
        
        if category:
            plans = plans.filter(plan__category__name=category)
        
        if difficulty:
            plans = plans.filter(plan__difficulty=difficulty)
        
        if plan_type:
            plans = plans.filter(plan__plan_type=plan_type)
        
        if library_type:
            plans = plans.filter(library_type=library_type)
        
        if search:
            plans = plans.filter(
                Q(plan__name__icontains=search) |
                Q(plan__description__icontains=search) |
                Q(detailed_description__icontains=search)
            )
        
        # 排序
        sort_by = request.GET.get('sort', 'featured')
        if sort_by == 'featured':
            plans = plans.order_by('-is_featured', '-is_trending', '-view_count')
        elif sort_by == 'popular':
            plans = plans.order_by('-download_count', '-like_count')
        elif sort_by == 'newest':
            plans = plans.order_by('-added_at')
        elif sort_by == 'rating':
            plans = plans.order_by('-plan__average_rating', '-view_count')
        
        # 分页
        paginator = Paginator(plans, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # 获取筛选选项
        categories = TrainingPlanCategory.objects.filter(is_active=True)
        
        # 获取用户收藏状态
        user_collections = {}
        if request.user.is_authenticated:
            collections = UserPlanCollection.objects.filter(
                user=request.user,
                plan__in=[p.plan for p in page_obj]
            ).values('plan_id', 'is_bookmarked', 'is_liked')
            user_collections = {c['plan_id']: c for c in collections}
        
        context = {
            'page_obj': page_obj,
            'categories': categories,
            'user_collections': user_collections,
            'current_filters': {
                'category': category,
                'difficulty': difficulty,
                'type': plan_type,
                'search': search,
                'library_type': library_type,
                'sort': sort_by
            }
        }
        
        return render(request, 'tools/plan_library.html', context)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def plan_detail(request, plan_id):
    """训练计划详情"""
    try:
        plan_library = get_object_or_404(PlanLibrary, plan_id=plan_id)
        plan = plan_library.plan
        
        # 增加浏览次数
        plan_library.increment_view()
        
        # 获取用户与该计划的关系
        user_plan = None
        user_collection = None
        
        try:
            user_plan = UserTrainingPlan.objects.get(user=request.user, plan=plan)
        except UserTrainingPlan.DoesNotExist:
            pass
        
        try:
            user_collection = UserPlanCollection.objects.get(user=request.user, plan=plan)
        except UserPlanCollection.DoesNotExist:
            pass
        
        # 获取计划中的动作
        plan_exercises = []
        if plan.week_schedule:
            exercise_names = set()
            for week_data in plan.week_schedule:
                for day_data in week_data.get('days', []):
                    for module in day_data.get('modules', {}).values():
                        for exercise_data in module:
                            exercise_names.add(exercise_data.get('name', ''))
            
            plan_exercises = Exercise.objects.filter(
                name__in=exercise_names,
                is_active=True
            )[:12]  # 限制显示数量
        
        # 获取相似计划
        similar_plans = PlanLibrary.objects.filter(
            plan__plan_type=plan.plan_type,
            plan__difficulty=plan.difficulty
        ).exclude(plan_id=plan_id)[:4]
        
        context = {
            'plan_library': plan_library,
            'plan': plan,
            'user_plan': user_plan,
            'user_collection': user_collection,
            'plan_exercises': plan_exercises,
            'similar_plans': similar_plans,
        }
        
        return render(request, 'tools/plan_detail.html', context)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# API 接口

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def toggle_exercise_favorite_api(request):
    """切换动作收藏状态"""
    try:
        data = json.loads(request.body)
        exercise_id = data.get('exercise_id')
        
        exercise = get_object_or_404(Exercise, id=exercise_id)
        preference, created = UserExercisePreference.objects.get_or_create(
            user=request.user,
            exercise=exercise
        )
        
        preference.is_favorite = not preference.is_favorite
        preference.save()
        
        return JsonResponse({
            'success': True,
            'is_favorite': preference.is_favorite
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def equip_achievement_badge_api(request):
    """佩戴成就徽章"""
    try:
        data = json.loads(request.body)
        achievement_id = data.get('achievement_id')
        
        user_achievement = get_object_or_404(
            EnhancedUserFitnessAchievement,
            user=request.user,
            achievement_id=achievement_id,
            is_completed=True
        )
        
        # 佩戴徽章
        user_achievement.equip_badge()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def unequip_achievement_badge_api(request):
    """取消佩戴徽章"""
    try:
        data = json.loads(request.body)
        achievement_id = data.get('achievement_id')
        
        user_achievement = get_object_or_404(
            EnhancedUserFitnessAchievement,
            user=request.user,
            achievement_id=achievement_id
        )
        
        # 取消佩戴
        user_achievement.unequip_badge()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def use_plan_template_api(request):
    """使用训练计划模板"""
    try:
        data = json.loads(request.body)
        plan_id = data.get('plan_id')
        
        plan = get_object_or_404(EnhancedTrainingPlan, id=plan_id)
        
        # 检查用户是否已经有这个计划
        user_plan, created = UserTrainingPlan.objects.get_or_create(
            user=request.user,
            plan=plan,
            defaults={
                'status': 'not_started',
                'total_sessions': plan.get_total_sessions()
            }
        )
        
        if created:
            # 增加计划使用次数
            plan.increment_usage()
            
            # 增加库中的下载次数
            try:
                plan_library = PlanLibrary.objects.get(plan=plan)
                plan_library.increment_download()
            except PlanLibrary.DoesNotExist:
                pass
        
        return JsonResponse({
            'success': True,
            'created': created,
            'user_plan_id': user_plan.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def save_custom_plan_api(request):
    """保存自定义训练计划"""
    try:
        data = json.loads(request.body)
        
        plan_data = {
            'name': data.get('name', '我的训练计划'),
            'description': data.get('description', ''),
            'plan_type': data.get('plan_type', 'general_fitness'),
            'difficulty': data.get('difficulty', 'beginner'),
            'duration_weeks': data.get('duration_weeks', 8),
            'training_days_per_week': data.get('training_days_per_week', 3),
            'session_duration': data.get('session_duration', 60),
            'week_schedule': data.get('week_schedule', []),
            'primary_goals': data.get('primary_goals', []),
            'creator': request.user,
            'status': 'active',
            'visibility': data.get('visibility', 'private')
        }
        
        # 创建训练计划
        plan = EnhancedTrainingPlan.objects.create(**plan_data)
        
        # 创建用户计划关联
        user_plan = UserTrainingPlan.objects.create(
            user=request.user,
            plan=plan,
            status='not_started',
            total_sessions=plan.get_total_sessions()
        )
        
        return JsonResponse({
            'success': True,
            'plan_id': plan.id,
            'user_plan_id': user_plan.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_workout_plan_details_api(request, plan_id):
    """获取训练计划详情"""
    try:
        plan = get_object_or_404(EnhancedTrainingPlan, id=plan_id)
        
        # 检查权限
        if plan.visibility == 'private' and plan.creator != request.user:
            return JsonResponse({'success': False, 'error': '无权访问'}, status=403)
        
        # 获取计划详细信息
        plan_details = {
            'id': plan.id,
            'name': plan.name,
            'description': plan.description,
            'plan_type': plan.get_plan_type_display(),
            'difficulty': plan.get_difficulty_display(),
            'duration_weeks': plan.duration_weeks,
            'training_days_per_week': plan.training_days_per_week,
            'session_duration': plan.session_duration,
            'week_schedule': plan.week_schedule,
            'primary_goals': plan.primary_goals,
            'total_sessions': plan.get_total_sessions(),
            'usage_count': plan.usage_count,
            'average_rating': plan.average_rating,
            'creator': plan.creator.username,
            'created_at': plan.created_at.isoformat(),
        }
        
        # 获取计划中的动作详情
        exercise_details = {}
        if plan.week_schedule:
            exercise_names = set()
            for week_data in plan.week_schedule:
                for day_data in week_data.get('days', []):
                    for module in day_data.get('modules', {}).values():
                        for exercise_data in module:
                            exercise_names.add(exercise_data.get('name', ''))
            
            exercises = Exercise.objects.filter(
                name__in=exercise_names,
                is_active=True
            ).prefetch_related('body_parts', 'primary_muscles', 'equipment')
            
            for exercise in exercises:
                exercise_details[exercise.name] = {
                    'id': exercise.id,
                    'name': exercise.name,
                    'english_name': exercise.english_name,
                    'description': exercise.description,
                    'instructions': exercise.instructions,
                    'difficulty': exercise.get_difficulty_display(),
                    'exercise_type': exercise.get_exercise_type_display(),
                    'body_parts': [bp.display_name for bp in exercise.body_parts.all()],
                    'primary_muscles': [mg.chinese_name for mg in exercise.primary_muscles.all()],
                    'equipment': [eq.name for eq in exercise.equipment.all()],
                    'form_cues': exercise.form_cues,
                    'common_mistakes': exercise.common_mistakes,
                    'safety_tips': exercise.safety_tips,
                }
        
        return JsonResponse({
            'success': True,
            'plan': plan_details,
            'exercises': exercise_details
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def get_user_achievement_stats(user):
    """获取用户成就统计"""
    total_achievements = EnhancedUserFitnessAchievement.objects.filter(
        user=user,
        is_completed=True
    ).count()
    
    total_points = EnhancedUserFitnessAchievement.objects.filter(
        user=user,
        is_completed=True
    ).aggregate(
        points=Sum('achievement__points_reward')
    )['points'] or 0
    
    equipped_badges = EnhancedUserFitnessAchievement.objects.filter(
        user=user,
        is_equipped=True
    ).count()
    
    return {
        'total_achievements': total_achievements,
        'total_points': total_points,
        'equipped_badges': equipped_badges
    }


def get_recommended_plans(user):
    """获取推荐的训练计划"""
    try:
        profile = FitnessUserProfile.objects.get(user=user)
        
        # 基于用户目标推荐
        recommended = PlanLibrary.objects.filter(
            is_featured=True
        ).select_related('plan')
        
        # 根据用户目标筛选
        if profile.goal == 'lose_weight':
            recommended = recommended.filter(plan__plan_type='weight_loss')
        elif profile.goal == 'gain_muscle':
            recommended = recommended.filter(plan__plan_type='hypertrophy')
        
        return recommended[:4]
        
    except FitnessUserProfile.DoesNotExist:
        # 返回默认推荐
        return PlanLibrary.objects.filter(
            is_featured=True
        ).select_related('plan')[:4]
