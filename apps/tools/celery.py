import os

from celery import Celery
from celery.schedules import crontab

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

# 创建Celery实例
app = Celery("qatoolbox")

# 使用Django的设置
app.config_from_object("django.conf:settings", namespace="CELERY")

# 自动发现任务
app.autodiscover_tasks()

# 定时任务配置
app.conf.beat_schedule = {
    # 每5分钟清理一次不活跃的聊天室
    "cleanup-inactive-chat-rooms": {
        "task": "apps.tools.tasks.cleanup_inactive_chat_rooms",
        "schedule": crontab(minute="*/5"),  # 每5分钟执行一次
    },
    # 每10分钟清理一次过期的心动链接
    "cleanup-expired-heart-links": {
        "task": "apps.tools.tasks.cleanup_expired_heart_links",
        "schedule": crontab(minute="*/10"),  # 每10分钟执行一次
    },
    # 每2分钟更新一次用户在线状态
    "update-user-online-status": {
        "task": "apps.tools.tasks.update_user_online_status",
        "schedule": crontab(minute="*/2"),  # 每2分钟执行一次
    },
    # 每15分钟检查一次聊天室活跃度
    "check-chat-room-activity": {
        "task": "apps.tools.tasks.check_chat_room_activity",
        "schedule": crontab(minute="*/15"),  # 每15分钟执行一次
    },
}

# 任务路由配置
app.conf.task_routes = {
    "apps.tools.tasks.*": {"queue": "chat_cleanup"},
}

# 任务序列化配置
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]

# 时区配置
app.conf.timezone = "Asia/Shanghai"
app.conf.enable_utc = False


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
