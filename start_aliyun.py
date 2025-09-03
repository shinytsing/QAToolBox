#!/usr/bin/env python
"""
阿里云生产环境启动脚本
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    # 设置Django设置模块
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.aliyun_production')
    
    # 初始化Django
    django.setup()
    
    # 启动生产服务器
    execute_from_command_line([
        'manage.py', 
        'runserver', 
        '0.0.0.0:8000',
        '--noreload',
        '--insecure'  # 允许静态文件服务
    ])
