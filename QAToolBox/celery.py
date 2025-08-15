#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Celery配置文件
"""

import os
from celery import Celery

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# 创建Celery应用
app = Celery('QAToolBox')

# 从Django设置中加载Celery配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()

# 任务路由配置
app.conf.task_routes = {
    'apps.tools.services.async_service.*': {'queue': 'tools'},
    'apps.users.services.*': {'queue': 'users'},
    '*': {'queue': 'default'},
}

# 任务序列化配置
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# 时区配置
app.conf.timezone = 'Asia/Shanghai'
app.conf.enable_utc = False

# 任务执行配置
app.conf.task_always_eager = False  # 生产环境设为False
app.conf.task_eager_propagates = True
app.conf.task_track_started = True
app.conf.task_time_limit = 30 * 60  # 30分钟
app.conf.task_soft_time_limit = 25 * 60  # 25分钟

# 工作进程配置
app.conf.worker_prefetch_multiplier = 1
app.conf.worker_max_tasks_per_child = 1000
app.conf.worker_disable_rate_limits = False

# 结果后端配置
app.conf.result_expires = 3600  # 1小时
app.conf.result_backend_transport_options = {
    'master_name': 'mymaster',
    'visibility_timeout': 3600,
}

# 定时任务配置
# 延迟导入以避免循环依赖
app.conf.beat_schedule = {}

@app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')
    return 'Debug task completed'
