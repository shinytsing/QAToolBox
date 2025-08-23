from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import ChatRoom, UserOnlineStatus, HeartLinkRequest
import logging

from datetime import datetime, time
from django.utils import timezone
from .fitness_nutrition_models import NutritionReminder, MealLog, DietPlan, Meal


logger = logging.getLogger(__name__)

@shared_task
def cleanup_inactive_chat_rooms():
    """清理不活跃的聊天室任务 - 12小时无活动自动删除"""
    try:
        from django.core.management import call_command
        # 使用新的清理命令，清理12小时无活动的聊天室
        call_command('cleanup_inactive_chatrooms', hours=12)
        logger.info('🧹 聊天室清理任务执行完成：清理12小时无活动的聊天室')
        return True
    except Exception as e:
        logger.error(f'❌ 聊天室清理任务执行失败: {e}')
        return False

@shared_task
def cleanup_expired_heart_links():
    """清理过期的心动链接任务"""
    try:
        from django.core.management import call_command
        call_command('cleanup_heart_links')
        logger.info('心动链接清理任务执行完成')
        return True
    except Exception as e:
        logger.error(f'心动链接清理任务执行失败: {e}')
        return False

@shared_task
def update_user_online_status():
    """更新用户在线状态任务"""
    try:
        now = timezone.now()
        cutoff_time = now - timedelta(minutes=5)  # 5分钟无活动认为离线
        
        # 查找超过5分钟没有活动的在线用户
        inactive_users = UserOnlineStatus.objects.filter(
            is_online=True,
            last_seen__lt=cutoff_time
        )
        
        # 更新为离线状态
        inactive_users.update(
            status='offline',
            is_online=False
        )
        
        if inactive_users.exists():
            logger.info(f'更新了 {inactive_users.count()} 个用户的在线状态为离线')
        
        return True
    except Exception as e:
        logger.error(f'更新用户在线状态任务执行失败: {e}')
        return False

@shared_task
def check_chat_room_activity():
    """检查聊天室活跃度任务"""
    try:
        now = timezone.now()
        active_rooms = ChatRoom.objects.filter(status='active')
        
        for room in active_rooms:
            # 检查房间是否超过30分钟没有消息
            last_message = room.messages.order_by('-created_at').first()
            if last_message:
                if now - last_message.created_at > timedelta(minutes=30):
                    # 标记为不活跃，但不立即结束
                    logger.info(f'聊天室 {room.room_id} 超过30分钟无消息')
        
        return True
    except Exception as e:
        logger.error(f'检查聊天室活跃度任务执行失败: {e}')
        return False


@shared_task
def send_nutrition_reminders():
    """发送营养提醒"""
    now = timezone.now()
    current_time = now.time()
    current_weekday = now.isoweekday()
    
    # 获取当前时间需要发送的提醒
    reminders = NutritionReminder.objects.filter(
        is_active=True,
        trigger_time__hour=current_time.hour,
        trigger_time__minute=current_time.minute
    )
    
    for reminder in reminders:
        # 检查是否在触发日期内
        if current_weekday in reminder.trigger_days or not reminder.trigger_days:
            # 这里可以集成实际的提醒发送逻辑
            # 比如发送邮件、短信、推送通知等
            print(f"发送提醒给用户 {reminder.user.username}: {reminder.message}")
            
            # 更新最后发送时间
            reminder.last_sent = now
            reminder.save()


@shared_task
def check_meal_completion():
    """检查餐食完成情况"""
    today = timezone.now().date()
    
    # 获取所有活跃的饮食计划
    active_plans = DietPlan.objects.filter(is_active=True)
    
    for plan in active_plans:
        # 获取今日应该完成的餐食
        today_meals = Meal.objects.filter(
            plan=plan,
            day_of_week=today.isoweekday()
        )
        
        # 检查哪些餐食还没有记录
        for meal in today_meals:
            meal_log = MealLog.objects.filter(
                user=plan.user,
                meal=meal,
                consumed_date=today
            ).first()
            
            if not meal_log:
                # 创建提醒
                NutritionReminder.objects.get_or_create(
                    user=plan.user,
                    reminder_type='meal_log',
                    message=f'您还没有记录{meal.get_meal_type_display()}，记得及时记录哦！',
                    trigger_time=time(14, 0),  # 下午2点提醒
                    is_recurring=False
                )


@shared_task
def update_plan_progress():
    """更新计划进度"""
    # 这里可以添加计划进度更新的逻辑
    # 比如根据用户的实际完成情况调整计划
    pass
