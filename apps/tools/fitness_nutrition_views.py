# NutriCoach Pro功能已隐藏 - 此文件中的所有功能暂时停用
# 如需重新启用，请取消注释相关代码并在urls.py中重新启用路由

"""
import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from .services.nutrition_coach_service import NutritionCoachService
from .models import (
    FitnessUserProfile as FitnessProfile, DietPlan, Meal, NutritionReminder, 
    MealLog, WeightTracking, FoodDatabase
)
from django.db import models


@login_required
def nutrition_dashboard(request):
    """营养定制仪表板"""
    try:
        profile = FitnessProfile.objects.get(user=request.user)
        active_plan = DietPlan.objects.filter(user=request.user, is_active=True).first()
        
        # 获取今日餐食
        today = datetime.now().date()
        today_meals = []
        if active_plan:
            today_meals = Meal.objects.filter(
                plan=active_plan,
                day_of_week=today.isoweekday()
            ).order_by('meal_type')
        
        # 获取今日记录
        today_logs = MealLog.objects.filter(
            user=request.user,
            consumed_date=today
        )
        
        # 获取最近体重记录
        recent_weight = WeightTracking.objects.filter(
            user=request.user
        ).order_by('-measurement_date').first()
        
        context = {
            'profile': profile,
            'active_plan': active_plan,
            'today_meals': today_meals,
            'today_logs': today_logs,
            'recent_weight': recent_weight,
        }
        
        return render(request, 'tools/nutrition_dashboard.html', context)
        
    except FitnessProfile.DoesNotExist:
        return redirect('nutrition_profile_setup')


@login_required
def nutrition_profile_setup(request):
    """用户档案设置"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # 创建或更新用户档案
                profile, created = FitnessProfile.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'age': request.POST.get('age'),
                        'gender': request.POST.get('gender'),
                        'height': float(request.POST.get('height')),
                        'weight': float(request.POST.get('weight')),
                        'goal': request.POST.get('goal'),
                        'activity_level': request.POST.get('activity_level'),
                        'dietary_preferences': request.POST.getlist('dietary_preferences'),
                        'allergies': request.POST.getlist('allergies'),
                    }
                )
                
                if not created:
                    # 更新现有档案
                    profile.age = request.POST.get('age')
                    profile.gender = request.POST.get('gender')
                    profile.height = float(request.POST.get('height'))
                    profile.weight = float(request.POST.get('weight'))
                    profile.goal = request.POST.get('goal')
                    profile.activity_level = request.POST.get('activity_level')
                    profile.dietary_preferences = request.POST.getlist('dietary_preferences')
                    profile.allergies = request.POST.getlist('allergies')
                    profile.save()
                
                messages.success(request, '用户档案设置成功！')
                return redirect('nutrition_generate_plan')
                
        except Exception as e:
            messages.error(request, f'设置失败：{str(e)}')
    
    return render(request, 'tools/nutrition_profile_setup.html')


@login_required
def nutrition_generate_plan(request):
    """生成饮食计划"""
    try:
        profile = FitnessProfile.objects.get(user=request.user)
    except FitnessProfile.DoesNotExist:
        messages.error(request, '请先设置用户档案')
        return redirect('nutrition_profile_setup')
    
    if request.method == 'POST':
        try:
            # 停用当前活跃计划
            DietPlan.objects.filter(user=request.user, is_active=True).update(is_active=False)
            
            # 生成新计划
            service = NutritionCoachService()
            user_data = {
                'age': profile.age,
                'gender': profile.gender,
                'height': profile.height,
                'weight': profile.weight,
                'goal': profile.goal,
                'activity_level': profile.activity_level,
                'dietary_preferences': profile.dietary_preferences,
                'allergies': profile.allergies,
                'intensity': request.POST.get('intensity', 'balanced'),
                'training_days_per_week': int(request.POST.get('training_days_per_week', 3))
            }
            
            plan_data = service.generate_meal_plan_with_deepseek(user_data)
            
            # 创建饮食计划
            with transaction.atomic():
                diet_plan = DietPlan.objects.create(
                    user=request.user,
                    start_date=datetime.now().date(),
                    end_date=datetime.now().date() + timedelta(days=6),
                    daily_calories=plan_data['daily_calories'],
                    protein_goal=plan_data['macros']['protein'],
                    carbs_goal=plan_data['macros']['carbs'],
                    fat_goal=plan_data['macros']['fat']
                )
                
                # 创建餐食
                for day_plan in plan_data['meal_plan']:
                    for meal_data in day_plan['meals']:
                        Meal.objects.create(
                            plan=diet_plan,
                            meal_type=meal_data['meal_type'],
                            day_of_week=day_plan['day'],
                            description=meal_data['name'],
                            ingredients=meal_data.get('ingredients', []),
                            calories=meal_data['nutrition']['calories'],
                            protein=meal_data['nutrition']['protein'],
                            carbs=meal_data['nutrition']['carbs'],
                            fat=meal_data['nutrition']['fat'],
                            ideal_time=self._get_ideal_time(meal_data['meal_type'])
                        )
                
                # 生成提醒
                reminders = service.generate_reminders(user_data, plan_data['meal_plan'])
                for reminder_data in reminders:
                    NutritionReminder.objects.create(
                        user=request.user,
                        reminder_type=reminder_data['type'],
                        message=reminder_data['message'],
                        trigger_time=reminder_data['trigger_time'],
                        is_recurring=reminder_data['is_recurring']
                    )
            
            messages.success(request, '饮食计划生成成功！')
            return redirect('nutrition_dashboard')
            
        except Exception as e:
            messages.error(request, f'计划生成失败：{str(e)}')
    
    return render(request, 'tools/nutrition_generate_plan.html', {'profile': profile})


def _get_ideal_time(meal_type):
    """获取理想用餐时间"""
    time_mapping = {
        'breakfast': '07:00',
        'lunch': '12:00',
        'dinner': '18:00',
        'snack': '15:00',
        'pre_workout': '16:00',
        'post_workout': '18:30'
    }
    return time_mapping.get(meal_type)


@login_required
def nutrition_meal_log(request):
    """餐食记录"""
    if request.method == 'POST':
        try:
            meal_id = request.POST.get('meal_id')
            consumed_date = request.POST.get('consumed_date')
            consumed_time = request.POST.get('consumed_time')
            is_completed = request.POST.get('is_completed') == 'true'
            
            meal = get_object_or_404(Meal, id=meal_id)
            
            # 创建或更新记录
            log, created = MealLog.objects.get_or_create(
                user=request.user,
                meal=meal,
                consumed_date=consumed_date,
                defaults={
                    'consumed_time': consumed_time,
                    'is_completed': is_completed
                }
            )
            
            if not created:
                log.consumed_time = consumed_time
                log.is_completed = is_completed
                log.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET请求显示记录页面
    today = datetime.now().date()
    logs = MealLog.objects.filter(
        user=request.user,
        consumed_date=today
    ).order_by('consumed_time')
    
    return render(request, 'tools/nutrition_meal_log.html', {'logs': logs})


@login_required
def nutrition_weight_tracking(request):
    """体重追踪"""
    if request.method == 'POST':
        try:
            weight = float(request.POST.get('weight'))
            body_fat = request.POST.get('body_fat_percentage')
            measurement_date = request.POST.get('measurement_date')
            notes = request.POST.get('notes', '')
            
            WeightTracking.objects.create(
                user=request.user,
                weight=weight,
                body_fat_percentage=float(body_fat) if body_fat else None,
                measurement_date=measurement_date,
                notes=notes
            )
            
            messages.success(request, '体重记录添加成功！')
            return redirect('nutrition_weight_tracking')
            
        except Exception as e:
            messages.error(request, f'记录失败：{str(e)}')
    
    # 获取历史记录
    weight_history = WeightTracking.objects.filter(
        user=request.user
    ).order_by('-measurement_date')[:30]  # 最近30条记录
    
    return render(request, 'tools/nutrition_weight_tracking.html', {
        'weight_history': weight_history
    })


@login_required
def nutrition_reminders(request):
    """提醒管理"""
    if request.method == 'POST':
        try:
            reminder_id = request.POST.get('reminder_id')
            action = request.POST.get('action')
            
            reminder = get_object_or_404(NutritionReminder, id=reminder_id, user=request.user)
            
            if action == 'toggle':
                reminder.is_active = not reminder.is_active
                reminder.save()
            elif action == 'delete':
                reminder.delete()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # 获取用户提醒
    reminders = NutritionReminder.objects.filter(
        user=request.user
    ).order_by('trigger_time')
    
    return render(request, 'tools/nutrition_reminders.html', {'reminders': reminders})


@login_required
def nutrition_progress(request):
    """进度分析"""
    # 获取最近30天的数据
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    # 体重变化
    weight_records = WeightTracking.objects.filter(
        user=request.user,
        measurement_date__range=[start_date, end_date]
    ).order_by('measurement_date')
    
    # 餐食完成率
    meal_completion = MealLog.objects.filter(
        user=request.user,
        consumed_date__range=[start_date, end_date]
    ).values('consumed_date').annotate(
        total_meals=models.Count('id'),
        completed_meals=models.Count('id', filter=models.Q(is_completed=True))
    )
    
    # 计算统计数据
    weight_change = 0
    if weight_records.count() >= 2:
        first_weight = weight_records.first().weight
        last_weight = weight_records.last().weight
        weight_change = last_weight - first_weight
    
    avg_completion_rate = 0
    if meal_completion:
        total_completed = sum(record['completed_meals'] for record in meal_completion)
        total_meals = sum(record['total_meals'] for record in meal_completion)
        avg_completion_rate = (total_completed / total_meals * 100) if total_meals > 0 else 0
    
    context = {
        'weight_records': weight_records,
        'meal_completion': meal_completion,
        'weight_change': weight_change,
        'avg_completion_rate': avg_completion_rate,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'tools/nutrition_progress.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def nutrition_api_generate_plan(request):
    """API接口：生成饮食计划"""
    try:
        data = json.loads(request.body)
        service = NutritionCoachService()
        
        plan_data = service.generate_meal_plan_with_deepseek(data)
        
        return JsonResponse({
            'success': True,
            'data': plan_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def nutrition_settings(request):
    """营养设置"""
    try:
        profile = FitnessProfile.objects.get(user=request.user)
    except FitnessProfile.DoesNotExist:
        return redirect('nutrition_profile_setup')
    
    if request.method == 'POST':
        try:
            # 更新设置
            profile.dietary_preferences = request.POST.getlist('dietary_preferences')
            profile.allergies = request.POST.getlist('allergies')
            profile.training_days_per_week = int(request.POST.get('training_days_per_week', 3))
            profile.save()
            
            messages.success(request, '设置更新成功！')
            return redirect('nutrition_settings')
            
        except Exception as e:
            messages.error(request, f'设置更新失败：{str(e)}')
    
    return render(request, 'tools/nutrition_settings.html', {'profile': profile})
"""
